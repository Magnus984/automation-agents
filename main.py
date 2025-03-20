from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes import api_version_one
from api.core.config import settings
import uvicorn

app = FastAPI(title=settings.PROJECT_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(api_version_one)

@app.get("/", tags=["Home"],)
async def get_root() -> dict:
    """
    Root endpoint for the API
    
    Returns:
        Redirects to docs
    """
    return responses.RedirectResponse("/docs")

@app.get("/health", tags=["Home"])
def health():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

