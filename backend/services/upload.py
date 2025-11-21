import base64
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException

from backend.file_utils.file_system import UploadChunk, UploadHandler


async def handle_start_upload(
    filename: str,
    num_chunks: int,
    uploads: dict[UUID, UploadHandler],
) -> UUID:
    """Create a new upload session and return its upload_id.

    Args:
        filename (str): The name of the file being uploaded.
        num_chunks (int): The total number of chunks the file will be divided into.
        uploads (dict[UUID, UploadHandler]): The mapping of upload_id to handlers.

    Returns:
        upload_id (UUID): The unique identifier for the upload session.
    """
    # get valid UUID
    upload_id = uuid4()
    while upload_id in uploads:
        upload_id = uuid4()

    # create the upload handler
    uploads[upload_id] = UploadHandler(
        filename=filename,
        num_chunks=num_chunks,
        upload_id=upload_id,
    )
    return upload_id


async def handle_upload_part(
    upload_id: UUID,
    chunk_id: int,
    data: str,
    uploads: dict[UUID, UploadHandler],
) -> None:
    """Handle the upload of a single part of a file.

    Args:
        upload_id (UUID): The unique identifier for the upload session.
        chunk_id (int): The identifier for the chunk being uploaded.
        data (str): The data of the chunk being uploaded (in base64 format).
        uploads (dict[UUID, UploadHandler]): The mapping of upload_id to handlers.
    """
    # check upload_id validity
    if upload_id not in uploads:
        raise HTTPException(status_code=400, detail="Invalid upload_id")
    upload_handler = uploads[upload_id]

    # create a chunk and add it if it's valid
    chunk = UploadChunk(chunk_id=chunk_id, data=data)
    upload_handler.add_chunk(chunk)


async def handle_complete_upload(
    upload_id: UUID,
    uploads: dict[UUID, UploadHandler],
    upload_dir: str,
) -> str:
    """Finalize the file if it has every chunk and return the filepath to that file.

    Args:
        upload_id (UUID): The unique identifier for the upload session.
        uploads (dict[UUID, UploadHandler]): The mapping of upload_id to handlers.
        upload_dir (str): Name of temporary directory to store our generated files.

    Returns:
        filepath (str): path to the temporarily created completed file.
    """
    # check upload_id validity
    if upload_id not in uploads:
        raise HTTPException(status_code=400, detail="Invalid upload_id")
    upload_handler = uploads[upload_id]

    # check for the file validity
    if not upload_handler.is_valid():
        raise HTTPException(status_code=400, detail="File is not complete yet")

    # create the file
    # if it already exists, just return as complete has been called already
    output_filepath = Path(upload_dir) / f"{upload_id}.bin"
    if output_filepath.exists():
        return str(output_filepath)

    with output_filepath.open("wb") as f:
        for chunk_data in upload_handler.get_chunks():
            f.write(base64.b64decode(chunk_data))

    return str(output_filepath)
