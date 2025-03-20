from re import S
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import pandas as pd
from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
from datetime import datetime
import numpy as np
import tempfile
from dotenv import load_dotenv
import os
from api.core.config import settings

load_dotenv()

# api_key = os.environ.get("OPENAI_API_KEY")
api_key = settings.openai_api_key

client = OpenAI(api_key=api_key)

data_cleaning = APIRouter(tags=["Data Cleaning"])

# @data_cleaning.get("/health")
# def health():
#     return {"status": "OK"}

UPLOAD_DIR = "uploads_data_cleaning"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store both DataFrame and metadata
data_store: Dict[str, Dict[str, Any]] = {}

class CommandRequest(BaseModel):
    uuid: str
    command: str

@data_cleaning.post("/upload-file/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        file_extension = os.path.splitext(file.filename)[-1].lower()
        file_uuid = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save file locally
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Read file into DataFrame
        if file_extension in [".xls", ".xlsx"]:
            wb = pd.ExcelFile(file_path)
            sheets = wb.sheet_names
            df = wb.parse(sheets[0])
            metadata = {
                "File Type": "Excel",
                "Number of Sheets": len(sheets),
                "Sheet Names": sheets,
                "Active Sheet": sheets[0]
            }
        elif file_extension == ".csv":
            df = pd.read_csv(file_path)
            metadata = {
                "File Type": "CSV",
                "Number of Sheets": 1,
                "Sheet Names": ["N/A"],
                "Active Sheet": "N/A"
            }
        else:
            return JSONResponse(content={"error": "Unsupported file format"}, status_code=400)

        # Common metadata
        metadata.update({
            "File Name": file.filename,
            "File Size (KB)": round(os.path.getsize(file_path) / 1024, 2),
            "Last Modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            "Number of Rows": df.shape[0],
            "Number of Columns": df.shape[1],
            "Column Names": df.columns.tolist(),
            "Data Types": df.dtypes.astype(str).to_dict(),
            "Missing Values Count": df.isnull().sum().to_dict(),
            "Unique Values Count": df.nunique().to_dict(),
            "Duplicate Rows": int(df.duplicated().sum()),
        })

        # Store in data_store
        data_store[file_uuid] = {
            "df": df,
            "metadata": metadata
        }

        return JSONResponse(content={
            "message": "File uploaded successfully",
            "uuid": file_uuid,
            "metadata": metadata
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@data_cleaning.post("/process/")
async def process_command(request: CommandRequest):
    try:
        entry = data_store.get(request.uuid)
        if not entry:
            raise HTTPException(status_code=404, detail="File not found")
        
        df = entry["df"]
        metadata = entry["metadata"]
        

        # Format metadata for prompt
        columns_str = ", ".join(metadata["Column Names"])
        data_types_str = ", ".join([f"{col}: {dtype}" for col, dtype in metadata["Data Types"].items()])
        missing_values_str = ", ".join([f"{col}: {count}" for col, count in metadata["Missing Values Count"].items()])
        
        prompt = f"""
        You are a specialized data analysis assistant that converts natural language instructions into precise Python code using pandas to manipulate a DataFrame. Your task is to interpret the user's request and provide the exact code needed to accomplish it, ensuring that the DataFrame 'df' is updated accordingly.
        Command: {request.command}
        
        ### DataFrame Metadata ###
        - Columns: {columns_str}
        - Data Types: {data_types_str}
        - Number of Rows: {metadata['Number of Rows']}
        - Missing Values: {missing_values_str}
        - Unique Values Count: {metadata['Unique Values Count']}
        - Duplicate Rows: {metadata['Duplicate Rows']}
        
        ### Requirements ###
        1. Generate valid pandas code that directly addresses the command.
        2. Use only DataFrame columns mentioned in the metadata.
        3. Handle missing values appropriately if relevant.
        4. Return a single line of code without explanations.
        
        Example Response:
        python
        df.dropna(subset=['Age'], inplace=True)
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        
        generated_code = response.choices[0].message.content
        print("Generated Code: ",generated_code)

        # Use regex to extract code between triple backticks
        import re
        code_match = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)

        if code_match:
            code_line = code_match.group(1).strip()
        else:
            # Fallback: Remove any remaining backticks and whitespace
            code_line = generated_code.replace('```', '').strip()

        print("Code line:", code_line)

        

        # Execute the generated code
        # Execute the generated code
        local_vars = {'df': df.copy()}
        global_vars = {'np': np, 'pd': pd}  # Make numpy and pandas available
        try:
            exec(code_line, global_vars, local_vars)
            modified_df = local_vars['df']
            data_store[request.uuid]["df"] = modified_df

            return JSONResponse(content={
                "message": "Command executed successfully",
                "generated_code": code_line,
                "preview": modified_df.head().to_dict()
            })
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Code execution error: {str(e)}")


    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from fastapi.responses import FileResponse




# Modified download endpoint
@data_cleaning.get("/download/{file_uuid}")
async def download_processed_file(file_uuid: str):
    try:
        entry = data_store.get(file_uuid)
        if not entry:
            raise HTTPException(status_code=404, detail="File not found")

        df = entry["df"]
        metadata = entry["metadata"]
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            # Save DataFrame to temporary CSV
            df.to_csv(temp_file.name, index=False)
            
            # Return the temporary file as response
            return FileResponse(
                temp_file.name,
                media_type="text/csv",
                filename=f"processed_{metadata['File Name']}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
