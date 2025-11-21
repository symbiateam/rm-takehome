from typing import Generator
from uuid import UUID

from fastapi import HTTPException


class UploadChunk:
    def __init__(self, chunk_id: int, data: str):
        self.chunk_id = chunk_id
        self.data = data


class UploadHandler:
    def __init__(self, filename: str, num_chunks: int, upload_id: UUID):
        self.filename = filename
        self.num_chunks = num_chunks
        self.upload_id = upload_id

        self.chunks: dict[int, UploadChunk] = {}

    def is_valid(self) -> bool:
        return len(self.chunks) == self.num_chunks

    def add_chunk(self, chunk: UploadChunk) -> None:
        # check chunk_id validity
        if chunk.chunk_id < 0 or chunk.chunk_id >= self.num_chunks:
            raise HTTPException(status_code=400, detail="Invalid chunk_id")
        if chunk.chunk_id in self.chunks:
            return

        self.chunks[chunk.chunk_id] = chunk

    def get_chunks(self) -> Generator[str, None, None]:
        for chunk_id in range(self.num_chunks):
            yield self.chunks[chunk_id].data
