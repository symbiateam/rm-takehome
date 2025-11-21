import sys
import tempfile
from asyncio import Lock

import uvicorn
from fastapi import FastAPI

sys.path.append("..")  # allows us to import from backend

from backend.routes import upload

app = FastAPI()
app.include_router(upload.router)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        print(tmp_dir)
        app.state.upload_dir = tmp_dir
        app.state.uploads = {}
        app.state.locks = {}
        app.state.global_lock = Lock()
        uvicorn.run(app, host="localhost", port=8000)
