from fastapi import APIRouter, HTTPException
from loguru import logger
import pandas as pd

from api.v1.schemas.table_question_answering import (
    ModelRequest, UserRequest
    )
from api.v1.services.table_question_answering.documents import handle_uploaded_file
from api.v1.services.table_question_answering.huggingface import query_model


router = APIRouter(tags=['TQA'])

@router.post('/query')
async def query_model_endpoint(request: UserRequest):
    try:
        async with handle_uploaded_file(content=request.content, file_name=request.file_name) as temp_file: 
            df = pd.read_excel(temp_file)
            data = df.to_dict(index=False)

        logger.info(f"Received request: {request}")
        response = await query_model(ModelRequest(query=request.query, table=data))
        logger.info(f"Response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error querying model: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")