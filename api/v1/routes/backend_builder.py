from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import requests
import base64
from api.core.config import settings
# import subprocess
# import git
# import os

backend_builder = APIRouter(tags=["Backend Builder"])

# class SchemaInput(BaseModel):
#     db_name: str
#     username: str
#     password: str
#     input_schema: dict  # Example: {"users": {"name": "str", "email": "str"}}

# token = settings.github_token
# username = settings.github_username
# GITHUB_USERNAME = username
# GITHUB_TOKEN = token
REPO_NAME = "generated-fastapi-backends"
GITHUB_API_URL = "https://api.github.com/user/repos"
# GITHUB_REPO_URL = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"

def create_github_repo(github_username, github_token):
    """Creates a GitHub repository if it doesn't exist"""
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
        }
    data = {"name": REPO_NAME, "private": True}  # Set private to True if needed

    response = requests.post(GITHUB_API_URL, json=data, headers=headers)

    if response.status_code in [201, 422]:  # 201: Created, 422: Already exists
        return f"https://github.com/{github_username}/{REPO_NAME}.git"
    else:
        raise HTTPException(status_code=500, detail=f"Failed to create GitHub repo: {response.json()}")
    
    
@backend_builder.post("/generate")
# def generate_backend(data: SchemaInput):
def generate_backend(mongo_uri: str, db_name: str, github_username: str, github_token: str, input_schema: dict):
    create_github_repo(github_username, github_token)
    # mongo_uri = f"mongodb+srv://{data.username}:{data.password}@primarycluster.jc2ou.mongodb.net/?retryWrites=true&w=majority"
    uri = mongo_uri
    script_content = f"""
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

try:
    client = MongoClient("{uri}")
    db = client["{db_name}"]
    print("Connected to MongoDB successfully!")
    
except Exception as e:
    print(f"Error connecting to MongoDB")
"""
    
    for collection_name, fields in input_schema.items():
        script_content += f"\n{collection_name}_collection = db['{collection_name}']\n"
        schema_class = f"class {collection_name.capitalize()}(BaseModel):\n"
        
        if isinstance(fields, dict):  # Handles nested or regular dictionary
            for field, field_type in fields.items():
                schema_class += f"    {field}: {field_type}\n"
        else:  # Handles a regular dictionary format
            schema_class += f"    {collection_name}: {fields}\n"
        
        script_content += f"\n{schema_class}\n"
        script_content += f"@app.post('/{collection_name}')\ndef create_{collection_name}(item: {collection_name.capitalize()}):\n"
        script_content += f"    {collection_name}_collection.insert_one(item.model_dump())\n    return item\n"
        
        script_content += f"\n@app.get('/{collection_name}')\ndef get_{collection_name}():\n"
        script_content += f"    return list({collection_name}_collection.find({{}}, {{'_id': 0}}))\n"
    
    script_content += """
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
    """
    
    file_path = "generated_backend.py"
    with open(file_path, "w") as f:
        f.write(script_content)
    
    # Run the generated FastAPI app in the background
    # try:
    #     subprocess.Popen(["uvicorn", "generated_backend:app", "--host", "0.0.0.0", "--port", "8001"])
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to start the generated FastAPI app: {str(e)}")

    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=500, detail="Failed to generate file")
    
#     return {"script": script_content, "download_url": "/download"}

    # Push to GitHub Repository
    try:
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Encode content in base64
        encoded_content = base64.b64encode(script_content.encode()).decode()

        # GitHub API URL for the file
        file_url = f"https://api.github.com/repos/{github_username}/{REPO_NAME}/contents/{file_path}"

        # Get SHA if the file already exists (needed for updates)
        existing_file = requests.get(file_url, headers=headers)
        sha = existing_file.json().get("sha") if existing_file.status_code == 200 else None

        # Prepare payload
        payload = {
            "message": "Auto-generated FastAPI backend",
            "content": encoded_content,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha  # Required if updating existing file

        response = requests.put(file_url, json=payload, headers=headers)

        if response.status_code not in [200, 201]:
            raise HTTPException(status_code=500, detail=f"Failed to upload to GitHub: {response.json()}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pushing to GitHub: {str(e)}")
    
    github_repo_url = f"https://github.com/{github_username}/{REPO_NAME}"
    # return {"file": FileResponse(file_path, media_type='application/octet-stream', filename="generated_backend.py"), "repo_link": github_repo_url}
    return {"repo_link": github_repo_url}

    # return FileResponse(file_path, media_type='application/octet-stream', filename="generated_backend.py")

