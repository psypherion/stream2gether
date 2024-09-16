# videoHost.py

from starlette.applications import Starlette
from starlette.responses import StreamingResponse
from starlette.routing import Route
from starlette.requests import Request
import os
from chunkizer import VideoStreamer

VIDEO_DIR = 'uploads'
VIDEO_PATH = os.path.join(VIDEO_DIR, 'crocker.mp4')

async def stream_video(request: Request) -> StreamingResponse:
    video_streamer = VideoStreamer(VIDEO_PATH)
    return await video_streamer.stream_video(request)

async def update_video(request: Request) -> StreamingResponse:
    global VIDEO_PATH
    form = await request.form()
    new_video_path = form.get("video_path")
    if new_video_path and os.path.exists(new_video_path):
        VIDEO_PATH = new_video_path
        return StreamingResponse("Video updated successfully", status_code=200)
    else:
        return StreamingResponse("Failed to update video", status_code=400)

app = Starlette(
    debug=True,
    routes=[
        Route('/stream', stream_video),
        Route('/update_video', update_video, methods=["POST"])
    ]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
