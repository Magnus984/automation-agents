from pydantic import BaseModel

class UserRequest(BaseModel):
    query: str
    file_name: str
    content: str

class ModelRequest(BaseModel):
    query: str
    table: dict[str, list]
