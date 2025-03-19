import os
from contextlib import asynccontextmanager
from fastapi import HTTPException
from loguru import logger


@asynccontextmanager
async def handle_uploaded_file(content: bytes, file_name: str):
    """
    Context manager to handle file upload and cleanup.
    """
    temp_file_path = f"{file_name}"
    try:
        with open(temp_file_path, "wb") as temp_file:
            logger.info(f"Creating temporary file: {temp_file.name}")
            temp_file.write(content)
        yield temp_file.name
    except Exception as e:
        logger.error(f"Error handling uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process uploaded file")
    finally:
        try:
            os.remove(temp_file.name)
            logger.info(f"Cleaned up temporary file: {temp_file.name}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary file: {e}")