from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import requests
import pdfplumber
import json
import re
from api.core.config import settings
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report
from typing import Union, Dict


screening_analyst = APIRouter(tags=["Screening Analyst"])
token = settings.HUGGING_FACE_API_TOKEN
API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": f"Bearer {token}"}
    
def extract_text_from_pdf(file):
    """Extracts text from a PDF file."""
    with pdfplumber.open(file) as pdf:
        text = " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text if text else ""

def extract_candidate_info(text):
    """Extracts candidate name and contact details using regex."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    
    email = re.findall(email_pattern, text)
    phone = re.findall(phone_pattern, text)
    
    name = text.split("\n")[0] if text else "Unknown"
    
    return {
        "name": name.strip(),
        "email": email[0] if email else "Not found",
        "phone": phone[0] if phone else "Not found"
    }



def match_resumes(job_text, resumes_text):
    """Matches resumes against the job description using TF-IDF & Cosine Similarity."""

    data = json.dumps({
        "inputs": {
        "source_sentence": job_text,
        "sentences": resumes_text
    },
    })

    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()
        


@screening_analyst.post("/match-resumes/")
async def match_resumes_to_job(
    job_description: UploadFile = File(...),
    resume: UploadFile = File(...),
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
):

    job_text = extract_text_from_pdf(job_description.file)
    resume_text = extract_text_from_pdf(resume.file)
    candidate_info = extract_candidate_info(resume_text)
    
    resumes_data = [{
        "filename": resume.filename,
        "info": candidate_info,
        "text": resume_text
    }]
    resumes_texts = [resume_text]

    similarity_scores = match_resumes(job_text, resumes_texts)
    
    # print(similarity_scores)
    
    for i, resume in enumerate(resumes_data):
        resume["similarity_score"] = round(similarity_scores[i], 2)

    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "POST /match-resumes",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
        
    return {
        "job": job_description.filename,
        "matched_resumes": resumes_data
    }
    