from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import requests
from PyPDF2 import PdfReader
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import openai
import io
import numpy as np
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report
from typing import Dict, Union

rag_system = APIRouter(tags=["Rag System"])


@rag_system.post("/set_credentials/")
async def set_credentials(
    openai_key: str = Form(...),
    database_name: str = Form(...),
    mongodb_uri: str = Form(...),
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    global user_openai_key, user_mongodb_uri

    # Store the user's OpenAI key and MongoDB URI
    user_openai_key = openai_key
    user_mongodb_uri = mongodb_uri

    # Set the OpenAI API key globally
    openai.api_key = user_openai_key

    # Connect to MongoDB using the user's URI
    client = AsyncIOMotorClient(user_mongodb_uri)
    db = client[database_name]
    
    # Set up MongoDB collections based on user-provided URI
    fs = AsyncIOMotorGridFSBucket(db)
    global files_collection, tags_collection
    files_collection = db["files"]
    tags_collection = db["tags"]

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "POST /set_credentials",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
            
    return {"message": "Credentials set successfully!"}

def generate_embedding(text: str):
    response = openai.embeddings.create(input=text, model="text-embedding-ada-002")
    return response.data[0].embedding

def tag(text: str, tags: list[str]):
    tags_str = ", ".join(tags)
    
    # Make the request
    url = "https://fourth-ir-tagging-agent-8dwd.onrender.com/Tag"
    headers = {
        'accept': 'application/json'
    }
    params = {
        'Text': text,
        'Tags': tags_str,
        'Threshold': '0.8'
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()["tags"]
    

@rag_system.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
   
    extracted_text = ""
    
    if file.content_type == "application/pdf":
        # Read the file into memory
        contents = await file.read()
        # Use PdfReader to extract text
        pdf_reader = PdfReader(io.BytesIO(contents))
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + "\n"
    
        print("text extracted successfully: ")      
     
    else:
        # Handle unsupported file types
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    try:
        db_tags = []
        async for tag_doc in tags_collection.find({}, {"_id": 0, "tag": 1}):
            db_tags.append(tag_doc["tag"])
    except Exception:
        raise HTTPException(status_code=404, detail="Database not found. Kindly set credentials above.") 
    
        
    identified_tags = tag(extracted_text, db_tags)
    print("tags successfully identified")    
    

    try:
        embedding = generate_embedding(extracted_text)
        print("embeddings generated")
    except Exception as e:
        error_message = str(e).split(" - ")[1].split("'error': ")[1].split(", 'type':")[0].strip("{}").split("'message': ")[1].strip("'")
        raise HTTPException(status_code=e.status_code, detail=error_message) 
    
    try:
        
        file_doc = {
            "filename": file.filename,
            "text": extracted_text,
            "tags": identified_tags,
            "embedding": embedding
        }
        
        result = await files_collection.insert_one(file_doc)

        if auth["is_valid"] and result:
            report = send_report(
                auth,
                auth['client'],
                "POST /upload",
            )
            if report.status == "error":
                raise HTTPException(
                    status_code=report.status_code,
                    detail=report.data.error
                )

        print("embeddings inserted into db")
        return {"file_id": str(result.inserted_id), "filename": file.filename, "tags": identified_tags}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@rag_system.get("/query/")
async def query_database(
    query: str,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    try:
        db_tags = [tag_doc["tag"] async for tag_doc in tags_collection.find({}, {"_id": 0, "tag": 1})]
        query_tags = tag(query, db_tags)
    except Exception:
        raise HTTPException(status_code=404, detail="Database not found. Kindly set credentials above.") 
    
    print("query has been tagged", query_tags )
    
    # Generate OpenAI embedding for query
    try:
        query_embedding = generate_embedding(query)
        print("query has been embedded")
    except Exception as e:
        error_message = str(e).split(" - ")[1].split("'error': ")[1].split(", 'type':")[0].strip("{}").split("'message': ")[1].strip("'")
        raise HTTPException(status_code=e.status_code, detail=error_message) 
    
    # Retrieve matching embeddings based on tags
    matching_docs = [doc async for doc in files_collection.find({"tags": {"$in": query_tags}}, {"_id": 0, "embedding": 1, "text": 1})]

    # print("matching docs: ", matching_docs)
    
    if not matching_docs:
        return {"response": "No relevant documents found."}

    # Compute similarity (dot product as cosine similarity is normalized)
    similarities = [
        (doc["text"], np.dot(query_embedding, doc["embedding"]))
        for doc in matching_docs
    ]

    # Sort by highest similarity
    most_relevant_text = sorted(similarities, key=lambda x: x[1], reverse=True)[0][0]

    # Use ChatGPT to generate response
    chat_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an assistant that answers questions based on retrieved documents."},
                  {"role": "user", "content": f"Answer based on this document:\n{most_relevant_text}\n\nQuery: {query}"}]
    )

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "GET /query",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
    
    return {"response": chat_response.choices[0].message.content}

@rag_system.post("/add_tag/")
async def add_tag(
    tag: str,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    try:
        # Find the file in MongoDB
        if await tags_collection.find_one({"tag": tag}):
            raise HTTPException(status_code=400, detail="Tag already exists")
        # Insert the new tag into the tags collection
        await tags_collection.insert_one({"tag": tag})
    except Exception:
        raise HTTPException(status_code=404, detail=str("Database not found. Kindly set credentials above."))

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "POST /add_tag",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )

    return {"message": f"Tag '{tag}' added successfully"}

# Endpoint to view all tags for a specific file
@rag_system.get("/get_tags/")
async def view_tags(
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    # Retrieve all tags from the tags collection
    tags = []
    try:
        async for tag_doc in tags_collection.find({}, {"_id": 0, "tag": 1}):
            tags.append(tag_doc["tag"])
    except Exception:
        raise HTTPException(status_code=404, detail=str("Database not found. Kindly set credentials above.")) 
    
    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "GET /get_tags",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
        
    return {"tags": tags}

# Endpoint to delete a tag from a file
@rag_system.delete("/delete_tag/")
async def delete_tag(
    tag_name: str,
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):
    # Find the file in MongoDB
    try: 
        if not await tags_collection.find_one({"tag": tag_name}):
            raise HTTPException(status_code=404, detail="Tag not found")
        # Delete the tag from the tags collection
        await tags_collection.delete_one({"tag": tag_name})
        # Remove the tag from all files that have it
        await files_collection.update_many({"tags": tag_name}, {"$pull": {"tags": tag_name}})
    except HTTPException:
        # Re-raise the HTTPException if it was already raised (e.g., "Tag not found")
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Database not found. Kindly set credentials above.") 
    
    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "DELETE /delete_tag",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
        
    return {"message": f"Tag '{tag_name}' deleted successfully"}