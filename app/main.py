from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os

from app.pipeline import run_pipeline

app = FastAPI(title="Video Dubbing API")

INPUT_PATH = "data/input/input_video.mp4"
OUTPUT_PATH = "data/output/final_dubbed_video.mp4"


@app.post("/dub-video")
async def dub_video(file: UploadFile = File(...)):
    
    # Save uploaded video
    with open(INPUT_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run your existing pipeline
    await run_pipeline()

    # Return final video
    return FileResponse(OUTPUT_PATH, media_type="video/mp4", filename="dubbed_video.mp4")

