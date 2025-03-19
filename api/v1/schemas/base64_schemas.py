from pydantic import BaseModel

class EncodeText(BaseModel):
    text: str

class DecodeText(BaseModel):
    base64_string: str