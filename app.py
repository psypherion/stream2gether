from chunkizer import VideoStreamer
from idGen import RoomKeyGenerator
from starlette.applications import Starlette
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates, _TemplateResponse
from starlette.requests import Request
import uvicorn
import os
from typing import Any
import aiofiles
from starlette.middleware.sessions import SessionMiddleware
# from socketHandler import websocket_endpoint  # Import the websocket endpoint

UPLOAD_DIR = "uploads"

templates = Jinja2Templates(directory="templates")
SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "your-default-secret-key")


if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

rooms: dict = {}

async def index(request: Request) -> _TemplateResponse:
    # use profile_id as seed
    # keep database PK profile_id
    room_key: str = RoomKeyGenerator(seed=123).generate_key(length=6)
    rooms[room_key] = {
        "media": None,
        "user_names": []
    }
    context: dict = {
        "request": request,
        "title": "stream2gether",
        "room_key": room_key
    }
    return templates.TemplateResponse("index.html", context=context)


async def host(request: Request) -> Any:
    if request.method == "POST":
        form = await request.form()
        room_key = form.get("room_key", RoomKeyGenerator(seed=123).generate_key(length=6))

        # Initialize room if it doesn't exist
        if room_key not in rooms:
            rooms[room_key] = {
                "media_name": form.get("going_to_watch", "Untitled"),  # Ensure media_name is set
                "user_names": []
            }
        else:
            # Room already exists; ensure media_name is still there
            if "media_name" not in rooms[room_key]:
                rooms[room_key]["media_name"] = form.get("going_to_watch", "Untitled")

        user_name = form.get("name", "anon")
        if user_name not in rooms[room_key]["user_names"]:
            rooms[room_key]["user_names"].append(user_name)

        # Handle the uploaded file
        media = form.get("file")
        if media:
            file_path = os.path.join(UPLOAD_DIR, media.filename)
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(await media.read())

            # Save video file path in the session
            request.session["media_path"] = media.filename
            request.session["room_key"] = room_key

        # Redirect to the room after uploading
        return RedirectResponse(url=f"/room/{room_key}", status_code=303)

    return templates.TemplateResponse("host.html", {"request": request})


# Stream the uploaded video
async def stream_video(request: Request) -> Response:
    # room_key = request.path_params['room_key']
    media_path = request.session.get("media_path")  # Get the uploaded video path from session

    if not media_path:
        return Response("Video not found", status_code=404)

    # Full path to the uploaded video
    video_path = os.path.join(UPLOAD_DIR, media_path)

    try:
        # Initialize VideoStreamer with the video path
        video_streamer = VideoStreamer(video_path)
        return await video_streamer.stream_video(request)
    except ValueError as e:
        return Response(f"Error: {str(e)}", status_code=400)
    except Exception as e:
        return Response(f"Internal Server Error: {str(e)}", status_code=500)



async def room(request: Request) -> _TemplateResponse:
    room_key = request.path_params['key']  # Get room key from the URL

    if room_key in rooms:
        room_data = rooms.get(room_key)

        # Ensure media_name is available
        media_name = room_data.get("media_name", "Untitled")
        user_names = room_data.get("user_names", [])

        # Video stream URL (this will point to the stream_video route)
        video_url = f"/stream/{room_key}"

        # Pass movie name, video URL, and joined user names to the room.html template
        return templates.TemplateResponse("room.html", {
            "request": request,
            "movie_name": media_name,
            "video_url": video_url,
            "user_names": user_names,
            "room_key": room_key
        })
    else:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Room not found"})

app = Starlette(
    debug=True,
    routes=[
        Route("/", index),
        Route("/host", host, name="host", methods=["GET", "POST"]),
        Route("/room/{key}", room, name="room"),  # Route for the room
        Route("/stream/{room_key}", stream_video, name="stream_video"),  # Route for video streaming
        Route("/guest", index, name="guest"),
        Mount("/static", StaticFiles(directory="static"), name="static")
    ]
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
from starlette.routing import Route

# Add WebSocket route
# app.add_route('/ws/{key}', websocket_endpoint)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)