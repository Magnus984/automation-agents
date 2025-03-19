from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import requests
import smtplib
import json
from email.mime.text import MIMEText

sales_outreach_router = APIRouter(tags=["Sales Outreach"])

# Replace with your actual Groq API key and SMTP details
GROQ_API_KEY = "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"
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "ccvosafo@gmail.com"
# SMTP_PASSWORD = "yxla rwhr kxlp mtsd"

# Input model
class MessageRequest(BaseModel):
    name: str
    email: EmailStr
    role: str
    company_name: str
    product: str
    # linkedin_username: str

# class Profile():
#     first_name: str
#     last_name: str
#     headline: str
#     city: str
#     most_recent_position: str
#     role: str
#     company: str
    

# Function to generate message using Groq
# def generate_message(linkedin_username: str) -> str:
# def generate_message(name: str, company_name: str, role: str, linkedin_username: str) -> str:
def generate_message(name: str, email: EmailStr, company_name: str, role: str, product: str) -> str:
    
    # linkedin_url = "https://linkedin-data-api.p.rapidapi.com/"
    # querystring = {"username":linkedin_username}

    # headers = {
    #     "x-rapidapi-key": "b97ac7d537mshc947e075f1ff5a0p134b39jsnff97c7acd4b4",
    #     "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    # }

    # linkedin_response = requests.get(linkedin_url, headers=headers, params=querystring)
    # data = linkedin_response.json()
    # # print("data issssss", data)
    # first_name = data.get("firstName", "")
    # last_name = data.get("lastName", "")
    # headline = data.get("headline", "")
    # city = data.get("geo", {}).get("city", "")

    # # Getting the most recent position
    # most_recent_position = data.get("position", [])[0] if data.get("position") else {}
    # role = most_recent_position.get("title", "")
    # company = most_recent_position.get("companyName", "")
    
    prompt = f"""Name: {name}, Role: {role}, Company: {company_name}, Product: {product}
    Draft an email to convince them to utilise our company Inngen's AI solutions.
    Respond with just the email body.
    """

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = json.dumps(
        {"messages":
            [{
                "role":"user",
                "content":prompt 
                # "content":prompt + " ".join("post" + item["text"] for item in linkedin_response.json()["data"])
                # "content":prompt + linkedin_response.json()["data"][0]["text"]
             }],
         "model":"llama-3.3-70b-versatile"
        }
    )
    
    headers = {
    'Authorization': 'Bearer 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',
    'Content-Type': 'application/json',
    }
    # print("linkedin_response:", linkedin_response.text)

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise HTTPException(status_code=500, detail="Failed to generate message from Groq")
    # print(response.json())

    # import requests
    # from bs4 import BeautifulSoup

    # # LinkedIn profile URL (Replace with target profile)
    # profile_url = "https://www.linkedin.com/in/nrich01/"

    # # Headers (Use your actual LinkedIn user-agent from browser)
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    # }

    # # Manually copy your LinkedIn cookies from browser (after logging in)
    # cookies = {
    #     "li_at": "AQEDATCzM3UFSHTXAAABlJLadLcAAAGVBMpJO00AhZuPAwe5TL0DZQ1Net9LgHdmh6nDRO_6xuKFy1YNyv-PQuoURYy-DOaLlWRyGzOTJLjThlphy5X6RV6pjCkxGV7_mc3Wjo5hxClULjJu7xyufPU2"  # Get this from your browser's dev tools
    # }

    # # Send a GET request
    # response = requests.get(profile_url, headers=headers, cookies=cookies)
    # # response = requests.get(profile_url)

    # # Check if request was successful
    # if response.status_code == 200:
    #     soup = BeautifulSoup(response.text, "html.parser")

    #     # Extract profile name
    #     name_tag = soup.find("h1")
    
    #     names = name_tag.text.strip() if name_tag else "Name not found"

    #     print("Profile Name:", names)
    # else:
    #     print(f"Failed to retrieve profile. Status Code: {response.status_code}")
    
    return response.json()["choices"][0]["message"]["content"]


# Function to send an email
# def send_email(to_email: str, message: str):
#     msg = MIMEText(message)
#     msg["Subject"] = "AI Solutions You Need"
#     msg["From"] = SMTP_USERNAME
#     msg["To"] = to_email

#     try:
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(SMTP_USERNAME, SMTP_PASSWORD)
#             server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# API endpoint
@sales_outreach_router.post("/sales_outreach")
async def sales_outreach(request: MessageRequest):
    try:
        # message = generate_message(linkedin_username)
        message = generate_message(request.name, request.email, request.company_name, request.role, request.product)
        # sent_email = send_email(request.email, message)
        return {"message": message}
        # return {"message": message, "email": sent_email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
