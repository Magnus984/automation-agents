from httpx import AsyncClient, HTTPStatusError
from loguru import logger

from api.core.config import settings
from api.v1.schemas.table_question_answering import ModelRequest

HEADERS = {"Authorization": f"Bearer {settings.hugging_face_api_token}"}


async def query_model(request: ModelRequest):
    async with AsyncClient(timeout=None) as client:
        try:
            logger.info("Sending request to model with URL: {}", settings.url)
            response = await client.post(
                url=settings.url, json={"input": request.model_dump()}, headers=HEADERS
            )
            response.raise_for_status()
            logger.info("Received response: {}", response.json())
            return response.json()
        except HTTPStatusError as e:
            logger.error("HTTP error occurred: {}", e)
            raise
        except Exception as e:
            logger.error("An unexpected error occurred: {}", e)
            raise