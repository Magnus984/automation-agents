# from fastapi import APIRouter, HTTPException
# from transformers import pipeline
# from pydantic import BaseModel

# router = APIRouter()


# # Load the summarization pipeline
# summarizer = pipeline("summarization")

# class TextRequest(BaseModel):
#     text: str
#     max_length: int = 60
#     min_length: int = 25

# @router.post("/summarize")
# async def summarize(request: TextRequest):
#     try:
#         summary = summarizer(request.text, max_length=request.max_length, min_length=request.min_length, do_sample=False)
#         print(request.max_length, request.min_length)
#         return {"summary": summary[0]['summary_text']}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
