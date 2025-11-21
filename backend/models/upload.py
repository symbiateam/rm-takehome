from pydantic import BaseModel


class StartRequest(BaseModel):
    filename: str
    num_chunks: int


class UploadPartRequest(BaseModel):
    data: str
