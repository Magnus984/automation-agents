from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import Dict
import requests
import uuid
import subprocess
import os
import json
import enum


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

dynamic_scrapper = APIRouter(tags=["Dynamic Scrapper"])

class ScrapeRequest(BaseModel):
    url: str

class Status(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"

# class Health(BaseModel):
#     status: Status
#     version: str
#     releaseId: str

# class HealthResponse(responses.JSONResponse):
#     media_type = "application/health+json"

# @app.get("/health", response_class=HealthResponse)
# async def get_health() -> Dict[str, str]:
#     return {
#         "status": Status.PASS.value,  # Correct enum reference
#         "version": "0.0.1",
#         "releaseId": "1",
#     }



@dynamic_scrapper.get("/test-link")
async def test_link(link: str):
    try:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            return "Successfully fetched the webpage!"
        else:
            return {
                "Message: ": "Failed to fetch webpage",
                "Status Code: ": response.status_code
            }  
    except requests.exceptions.HTTPError as err:
        return f"HTTP error occurred: {err}"



@dynamic_scrapper.post("/scrape")
async def scrape_website(request: ScrapeRequest):
    unique_id = str(uuid.uuid4())  # Generate a unique file name for each request
    output_file = f"output_{unique_id}.json"
    
    command = [
        "scrapy", "runspider", "tradingagent/tradingagent/spiders/dynamic_spider.py",  # Make sure the path to the spider is correct
        "-a", f"start_url={request.url}",
        "-o", output_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Scraping failed or no data collected.")
        
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        os.remove(output_file)  # Cleanup the file after reading
        return {"status": "success", "data": data}
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Scrapy error: {e.stderr}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))