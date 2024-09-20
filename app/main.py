from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
from selenium_script import save_media

app = FastAPI()

# Define the public folder path
PUBLIC_FOLDER = "public"
HOSTING_DOMAIN = "http://example.com"  # Replace with your actual domain

class MediaRequest(BaseModel):
    video_id: str

def save_media_task(video_id: str):
    return save_media(video_id, PUBLIC_FOLDER)

@app.post("/save_media/")
async def save_media_endpoint(request: MediaRequest, background_tasks: BackgroundTasks):
    # Add a background task to download the video
    download_url = save_media_task(request.video_id)
    
    # Append the hosting domain to the download URL
    full_download_url = f"{HOSTING_DOMAIN}{download_url}"
    
    return {"message": "Media download started", "download_url": full_download_url}
