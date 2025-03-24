from fastapi import APIRouter, Query, Body, Depends, HTTPException
import requests
from api.core.config import settings
from api.v1.routes.auth import auth_guard
from api.core.dependencies.api_key_usage import send_report
from typing import Dict, Union


fourth_ir_tagging_agent = APIRouter(tags=["4th-IR Tagging Agent"])

url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"


@fourth_ir_tagging_agent.post("/tag")
def tagging_agent(
    Text: str = Body(..., description="The input text to be analyzed"),
    Tags: str = Query(..., description="Comma-separated list of tags"),
    Threshold: float = Query(0.5, description="Confidence threshold for tagging"),
    auth: Dict[str, Union[str, bool]] = Depends(auth_guard)
    ):  # Text and tags input from the users   text_input = input("Enter the text to classify: ")
    labels = [label.strip() for label in Tags.split(',')]  #Creates an array for tags from the user input  #Comma is a key element for the word separaton   #Removes the space before an after each word after the comma # tag_input = input("Enter your labels separated by commas (e.g. urgent, phone, support): ")
    idkyet= 'true' 
    # Request body
    request_body = {
    "inputs": Text,
    "parameters":{"candidate_labels": labels,  "multi_label": idkyet}}

    # Header for the POST request
    token = settings.HUGGING_FACE_API_TOKEN
    headers = {
    "Authorization": f"Bearer {token}"
    }
    # POST request to the API
    response = requests.post(url, headers=headers, json=request_body)
    response_fromAPI = ""
    #Check status code 
    if response.status_code == 200:
        # print("Response from model:", response.json())  
        response_fromAPI = response.json()
    # Output the result from the model
    else:
        print(f"Error: {response.status_code} - {response.text}")

    #after the endpoint does its thing lets try and manipulate it 
    #creating list variables for the necessary ones 
    labels_print = response_fromAPI["labels"]
    scores_print = response_fromAPI["scores"]

    #Now lets create a fuction that maps each label to their score 
    zipped = zip(labels_print, (scores_print))
    mapped = tuple(zipped)
    print("mapped", mapped)

    return_list = []
    #Now lets just and set a threshold and prin what is above the threshold
    for label, score in mapped:
        if score >= Threshold:
             return_list.append(label)
    
    if auth["is_valid"]:
        report = send_report(
            auth,
            auth['client'],
            "POST /tag",
        )

        if report.status == "error":
            raise HTTPException(
                status_code=report.status_code,
                detail=report.data.error
            )
    
    return{"tags":return_list}