from fastapi import APIRouter, File, UploadFile
from docling.document_converter import DocumentConverter
from typing import List, Dict
import os
import re

# import markdown

doc_splitter = APIRouter(tags=["Docs Splitter 1"])

# @router.post("/doc_splitter")
# async def document_section_splitter(files: List[UploadFile] = File(...)) -> Dict[str, List[Dict[str, str]]]:

def save_uploaded_file(upload_file: UploadFile) -> str:
    """
    Save the uploaded file to a temporary location and return its path.
    """
    file_path = f"/tmp/{upload_file.filename}"  # Save to a temporary directory
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return file_path

def split_into_sections(markdown_content: str) -> Dict[str, str]:
    """
    Split markdown content into introduction, body, and conclusion.
    This is a placeholder function; replace with actual logic.
    """

    sections = {}
    matches = re.findall(r'##\s*(.*?)\s*[:|.]?\n(.*?)(?=##\s|$)', markdown_content, re.DOTALL)
    
    for heading, content in matches:
        heading = heading.strip()
        content = content.strip()
        sections[heading] = content
    
    return sections

@doc_splitter.post("/process-doc_splitter/")
async def document_section_splitter(files: List[UploadFile] = File(...)) :
    """
    Endpoint to accept files, convert them to markdown using docling, and split into sections.
    """
    results = {}

    for file in files:
        # Save the uploaded file to a temporary location
        file_path = save_uploaded_file(file)
        
        # Use docling to convert the file to markdown
        converter = DocumentConverter()
        result = converter.convert(file_path)
        markdown_content = result.document.export_to_markdown()
        
        # Split the markdown content into sections
        sections = split_into_sections(markdown_content)
        
        # Store results for this file
        for heading, content in sections.items():
            if heading in results:
                results[heading] += " " + content
            else:
                results[heading] = content
        
        # Clean up: Delete the temporary file
        os.remove(file_path)

    return results