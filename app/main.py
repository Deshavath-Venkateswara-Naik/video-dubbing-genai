from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

from app.pipeline import run_pipeline
from app.config import VIDEO_PATH, FINAL_VIDEO_PATH

app = FastAPI(title="Video Dubbing API")


@app.post("/dub-video")
async def dub_video(file: UploadFile = File(...)):
    # Ensure input directory exists
    os.makedirs(os.path.dirname(VIDEO_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(FINAL_VIDEO_PATH), exist_ok=True)

    # Save uploaded video
    with open(VIDEO_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run your existing pipeline
    await run_pipeline()

    # Return final video
    return FileResponse(FINAL_VIDEO_PATH, media_type="video/mp4", filename="dubbed_video.mp4")

