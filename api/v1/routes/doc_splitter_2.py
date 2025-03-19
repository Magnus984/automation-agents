import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
# from docling.document_converter import DocumentConverter
from typing import List, Dict
# from pydantic import BaseModel
# import base64
import os
import re

import pymupdf4llm
# import pypandoc


# Reponse Model
from pydantic import BaseModel
from typing import Dict, List

class ConsolidationResponse(BaseModel):
    headers: List[str]  # List of headers
    content: Dict[str, str]  # Dictionary of content


doc_splitter_2 = APIRouter(tags=["Docs Splitter 2"])


# Directory where all files will be saved for consolidation
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
# Ensure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  


def save_uploaded_file(upload_file: UploadFile) -> str: 
    temp_dir = tempfile.gettempdir()  # Gets OS-specific temp directory 
    file_path = os.path.join(temp_dir, upload_file.filename) 
    with open(file_path, "wb") as buffer: buffer.write(upload_file.file.read()) 
    return file_path



def split_into_sections(markdown_content: str) -> Dict[str, str]:
    """
    Split markdown content into introduction, body, and conclusion.
    This is a placeholder function; replace with actual logic.
    """

    sections = {}

    matches = re.findall(r'^(#{1,6})\s*(.+?)\s*[:|.]?\n([\s\S]*?)(?=^#{1,6}\s|\Z)', markdown_content, re.MULTILINE)

    for level, heading, content in matches:
        heading = heading.strip()
        content = " ".join(content.split()) 
        content = content.replace('-----', '').strip() 
        sections[heading] = content
    
    return sections

@doc_splitter_2.post("/upload_file")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Endpoint to upload a single file and save it to the upload folder.
    Args:
        file (UploadFile): The file to upload.
    Returns:
        Dict[str, str]: A message indicating success or failure.
    """
    try:
        # Save the file to the upload folder
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        return {"status": "success", "message": f"File '{file.filename}' uploaded successfully.", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@doc_splitter_2.delete("/clear_folder")
async def clear_folder():
    """
    Endpoint to clear all files from the upload folder.
    Returns:
        Dict[str, str]: A message indicating success or failure.
    """
    try:
        # Remove all files in the upload folder
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return {"status": "success", "message": "Upload folder cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @doc_splitter_2.post("/consolidate_docs")
# async def document_consolidator() -> Dict[str, Dict[str, str]]:
#     """
#     Endpoint to fetch all files from the upload folder, convert them to markdown, and consolidate content by headings.
#     Returns:
#         Dict[str, Dict[str, str]]: Consolidated content with headers and their corresponding content.
#     """
#     section_content = {}
#     headers = []

#     try:
#         # Get all files in the upload folder
#         files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]

#         if not files:
#             raise HTTPException(status_code=404, detail="No files found in the upload folder.")

#         for filename in files:
#             file_path = os.path.join(UPLOAD_FOLDER, filename)

#             try:
#                 # Convert the file to markdown
#                 markdown_content = pymupdf4llm.to_markdown(file_path)

#                 # Split the markdown content into sections
#                 sections = split_into_sections(markdown_content)

#                 # Consolidate sections
#                 for heading, content in sections.items():
#                     if heading in section_content:
#                         section_content[heading] += " " + content
#                     else:
#                         section_content[heading] = content
#                         headers.append(heading)

#             except Exception as e:
#                 continue  # Skip this file and continue with the next one

#         return {
#             "headers": headers,
#             "content": section_content
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to consolidate files: {str(e)}")

@doc_splitter_2.post("/consolidate_docs", response_model=ConsolidationResponse)
async def document_consolidator() -> ConsolidationResponse:
    """
    Endpoint to fetch all files from the upload folder, convert them to markdown, and consolidate content by headings.
    Returns:
        ConsolidationResponse: Consolidated content with headers and their corresponding content.
    """
    section_content = {}
    headers = []

    try:
        # Get all files in the upload folder
        files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]

        if not files:
            raise HTTPException(status_code=404, detail="No files found in the upload folder.")

        for filename in files:
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            try:
                # Convert the file to markdown
                markdown_content = pymupdf4llm.to_markdown(file_path)

                # Split the markdown content into sections
                sections = split_into_sections(markdown_content)

                # Consolidate sections
                for heading, content in sections.items():
                    if heading in section_content:
                        section_content[heading] += " " + content
                    else:
                        section_content[heading] = content
                        headers.append(heading)

            except Exception as e:
                continue  # Skip this file and continue with the next one

        # Return the response using the Pydantic model
        return ConsolidationResponse(headers=headers, content=section_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to consolidate files: {str(e)}")

# @doc_splitter_2.post("/consolidate_docs")
# async def document_consolidator(files: List[UploadFile] = File(...)) :
#     """
#     Endpoint to accept files, convert them to markdown using docling, and split into sections.
#     """
#     section_content = {}
#     headers = []

#     for file in files:
#         # Decode Base64 content
#         # file_bytes = base64.b64decode(file.content)
#         # file_path = f"/tmp/{file.filename}"  # Temporary file path
#         file_path = save_uploaded_file(file)

#         # Save file temporarily
#         # with open(file_path, "wb") as f:
#         #     f.write(file_bytes)

#         # Convert to markdown
#         markdown_content = pymupdf4llm.to_markdown(file_path) 

#         # Split into sections
#         sections = split_into_sections(markdown_content)
        
#         for heading, content in sections.items():
#             if heading in section_content:
#                 section_content[heading] += " " + content
#             else:
#                 section_content[heading] = content
#                 headers.append(heading)
       
#         # Remove temporary file
#         os.remove(file_path)
        
#     results = {
#         "headers": headers,
#         "content": section_content
#     }
    
#     return results




# First response

# {
#   "headers": [
#     "Introduction",
#     "Body",
#     "Economic Impact",
#     "Conclusion",
#     "Challenges"
#   ],
#   "content": {
#     "Introduction": "Climate change has emerged as one of the most pressing global issues of the 21st century. This document aims to discuss the causes of climate change, its consequences, and the steps that can be taken to mitigate its effects. The rise of artificial intelligence (AI) has fundamentally altered various industries, offering opportunities for innovation and transformation. This document will explore the impact of AI in the healthcare sector, focusing on how it is reshaping diagnostics, patient care, and administrative processes. The rise of artificial intelligence (AI) has fundamentally altered various industries, offering opportunities for innovation and transformation. This document will explore the impact of AI in the healthcare sector, focusing on how it is reshaping diagnostics, patient care, and administrative processes.",
#     "Body": "The primary cause of climate change is the increase in greenhouse gases, such as carbon dioxide, methane, and nitrous oxide, due to human activities like deforestation, burning fossil fuels, and industrial processes. These gases trap heat in the Earth's atmosphere, leading to global warming. The consequences of climate change include rising sea levels, extreme weather events, and biodiversity loss. To mitigate these effects, global cooperation is needed to reduce emissions, adopt renewable energy sources, and implement conservation efforts to protect ecosystems. AI has revolutionized diagnostics by enabling faster and more accurate detection of diseases. Machine learning models can analyze medical images with remarkable precision, identifying conditions such as cancer and neurological disorders earlier than traditional methods. In patient care, AI-powered chatbots and virtual assistants are providing patients with real-time support, answering questions, and scheduling appointments. Additionally, AI-driven algorithms are helping healthcare providers manage resources efficiently, reducing human error in administrative tasks. AI has revolutionized diagnostics by enabling faster and more accurate detection of diseases. Machine learning models can analyze medical images with remarkable precision, identifying conditions such as cancer and neurological disorders earlier than traditional methods. In patient care, AI-powered chatbots and virtual assistants are providing patients with real-time support, answering questions, and scheduling appointments. Additionally, AI-driven algorithms are helping healthcare providers manage resources efficiently, reducing human error in administrative tasks.",
#     "Economic Impact": "Climate change has significant economic implications. Natural disasters caused by global warming lead to billions of dollars in damages, affecting infrastructure, agriculture, and businesses. Many industries, such as tourism and farming, are highly dependent on stable weather conditions and are at risk due to extreme climate changes. On the other hand, the shift towards renewable energy and sustainable practices presents economic opportunities, fostering innovation in green technology and job creation in eco-friendly industries.",
#     "Conclusion": "In conclusion, addressing climate change requires collective action at the global level. By making significant changes to our energy consumption, industrial practices, and conservation efforts, we can minimize the damage caused by climate change and work towards a more sustainable future—both environmentally and economically. In conclusion, AI is making significant strides in the healthcare industry, improving both patient outcomes and operational efficiency. As the technology continues to evolve, it holds the potential to address many challenges within the healthcare system, ultimately saving lives and reducing costs. In conclusion, AI is making significant strides in the healthcare industry, improving both patient outcomes and operational efficiency. However, challenges such as data security, model accuracy, and implementation costs must be addressed to ensure AI’s long-term success in the healthcare sector.",
#     "Challenges": "Despite its benefits, AI in healthcare faces several challenges. One major concern is data privacy, as patient records contain sensitive information that must be protected. Additionally, the reliability of AI models depends on the quality of the data they are trained on, which can sometimes lead to biased or inaccurate outcomes. Furthermore, the integration of AI into existing healthcare systems requires significant investment and training, which can be a barrier for some institutions."
#   }
# }