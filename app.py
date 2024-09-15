# main.py
from chunkizer import VideoStreamer
from idGen import RoomKeyGenerator
from starlette.applications import Starlette
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates, _TemplateResponse
from starlette.requests import Request
import uvicorn
import os
from typing import Any
import aiofiles
from starlette.middleware.sessions import SessionMiddleware
from socketHandler import handle_connection

# Create the Starlette app
app = Starlette()

UPLOAD_DIR = "uploads"
templates = Jinja2Templates(directory="templates")
SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "your-default-secret-key")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

rooms: dict = {}

async def index(request: Request) -> _TemplateResponse:
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

        if room_key not in rooms:
            rooms[room_key] = {
                "media_name": form.get("going_to_watch", "Untitled"),
                "user_names": []
            }
        else:
            if "media_name" not in rooms[room_key]:
                rooms[room_key]["media_name"] = form.get("going_to_watch", "Untitled")

        user_name = form.get("name", "anon")
        if user_name not in rooms[room_key]["user_names"]:
            rooms[room_key]["user_names"].append(user_name)

        media = form.get("file")
        if media:
            file_path = os.path.join(UPLOAD_DIR, media.filename)
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(await media.read())

            request.session["media_path"] = media.filename
            request.session["room_key"] = room_key

        return RedirectResponse(url=f"/room/{room_key}", status_code=303)

    return templates.TemplateResponse("host.html", {"request": request})

async def stream_video(request: Request) -> Response:
    media_path = request.session.get("media_path")

    if not media_path:
        return Response("Video not found", status_code=404)

    video_path = os.path.join(UPLOAD_DIR, media_path)

    try:
        video_streamer = VideoStreamer(video_path)
        return await video_streamer.stream_video(request)
    except ValueError as e:
        return Response(f"Error: {str(e)}", status_code=400)
    except Exception as e:
        return Response(f"Internal Server Error: {str(e)}", status_code=500)

async def room(request: Request) -> _TemplateResponse:
    room_key = request.path_params['key']

    if room_key in rooms:
        room_data = rooms.get(room_key)
        media_name = room_data.get("media_name", "Untitled")
        user_names = room_data.get("user_names", [])

        video_url = f"/stream/{room_key}"

        return templates.TemplateResponse("room.html", {
            "request": request,
            "movie_name": media_name,
            "video_url": video_url,
            "user_names": user_names,
            "room_key": room_key
        })
    else:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Room not found"})

# Define the routes
routes = [
    Route("/", index),
    Route("/host", host, name="host", methods=["GET", "POST"]),
    Route("/room/{key}", room, name="room"),
    Route("/stream/{room_key}", stream_video, name="stream_video"),
    Route("/guest", index, name="guest"),
    Mount("/static", StaticFiles(directory="static"), name="static"),
    WebSocketRoute("/ws/{room_key}", handle_connection)
]

# Create the Starlette app with routes and middleware
app = Starlette(
    debug=True,
    routes=routes
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)
