from asyncio import Lock
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from backend.file_utils.file_system import UploadHandler
from backend.models.upload import StartRequest, UploadPartRequest
from backend.services.upload import (
    handle_complete_upload,
    handle_start_upload,
    handle_upload_part,
)

router = APIRouter(prefix="")


@router.get("/status")
async def get_status():
    return {"status": "ok"}


@router.post("/start")
async def start_upload(request: Request, start_request: StartRequest) -> UUID:
    async with request.app.state.global_lock:
        upload_id = await handle_start_upload(
            filename=start_request.filename,
            num_chunks=start_request.num_chunks,
            uploads=request.app.state.uploads,
        )
        # create a lock for this upload_id
        if upload_id not in request.app.state.locks:
            request.app.state.locks[upload_id] = Lock()
    return upload_id


@router.post("/part/<upload_id>/<chunk_id>")
async def upload_part(
    request: Request,
    upload_id: str,
    chunk_id: int,
    upload_part_request: UploadPartRequest,
):
    async with request.app.state.global_lock:
        # check we have a lock for this upload_id
        if UUID(upload_id) not in request.app.state.locks:
            raise HTTPException(status_code=400, detail="Upload_id invalid")

    async with request.app.state.locks[UUID(upload_id)]:
        return await handle_upload_part(
            upload_id=UUID(upload_id),
            chunk_id=chunk_id,
            data=upload_part_request.data,
            uploads=request.app.state.uploads,
        )


@router.post("/complete/<upload_id>")
async def complete_upload(request: Request, upload_id: str) -> FileResponse:
    async with request.app.state.global_lock:
        # check we have a lock for this upload_id
        if UUID(upload_id) not in request.app.state.locks:
            raise HTTPException(status_code=400, detail="Upload_id invalid")

    async with request.app.state.locks[UUID(upload_id)]:
        filepath = await handle_complete_upload(
            upload_id=UUID(upload_id),
            uploads=request.app.state.uploads,
            upload_dir=request.app.state.upload_dir,
        )
    upload_handler: UploadHandler = request.app.state.uploads[UUID(upload_id)]
    return FileResponse(filepath, filename=upload_handler.filename)
