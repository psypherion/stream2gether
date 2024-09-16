# app.py

from chunkizer import VideoStreamer
from idGen import RoomKeyGenerator
from starlette.applications import Starlette
from starlette.responses import RedirectResponse
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates, _TemplateResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
from typing import Dict, List, Any
import aiofiles
from socketHandler import handle_connection
import logging
from tunnels import Cloudflare
import subprocess

logger = logging.getLogger(__name__)
UPLOAD_DIR = "uploads"

templates = Jinja2Templates(directory="templates")
SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "your-default-secret-key")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

RoomData = Dict[str, Any]
rooms: Dict[str, RoomData] = {}

# Extract the first tunnel URL and use it for streaming
cloudflare = Cloudflare()
cloudflare.path_checker()  # Ensure the log directory exists
log_files = cloudflare.log_list
urls = cloudflare.extract_tunnels_recursively(log_files)
streaming_base_url = urls[0] if urls else "http://localhost:8000"  # Fallback URL if no tunnel is found

async def index(request: Request) -> _TemplateResponse:
    room_key: str = RoomKeyGenerator(seed=123).generate_key(length=6)
    rooms[room_key] = {
        "media_name": None,
        "user_names": []
    }
    context: Dict[str, Any] = {
        "request": request,
        "title": "stream2gether",
        "room_key": room_key
    }
    return templates.TemplateResponse("index.html", context=context)

async def host(request: Request) -> Any:
    if request.method == "POST":
        form = await request.form()
        room_key: str = form.get("room_key", RoomKeyGenerator(seed=123).generate_key(length=6))

        if room_key not in rooms:
            rooms[room_key] = {
                "media_name": form.get("going_to_watch", "Untitled"),
                "user_names": []
            }
        else:
            if "media_name" not in rooms[room_key]:
                rooms[room_key]["media_name"] = form.get("going_to_watch", "Untitled")
            else:
                rooms[room_key]["media_name"] = form.get("going_to_watch", rooms[room_key]["media_name"])

        user_name: str = form.get("name", "anon")
        if user_name not in rooms[room_key]["user_names"]:
            rooms[room_key]["user_names"].append(user_name)

        request.session['username'] = user_name
        request.session['room_key'] = room_key

        media = form.get("file")
        if media:
            file_path = os.path.join(UPLOAD_DIR, media.filename)
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(await media.read())

            request.session["media_path"] = media.filename

            # Update videoHost.py with the new video path
            subprocess.run(["curl", "-X", "POST", "-d", f"video_path={file_path}", "http://localhost:8000/update_video"])

        return RedirectResponse(url=f"/room/{room_key}", status_code=303)

    return templates.TemplateResponse("host.html", {"request": request})

async def guest(request: Request) -> Any:
    if request.method == "POST":
        form = await request.form()
        room_key: str = form.get("room_key")
        user_name: str = form.get("name", "anon")

        if room_key in rooms:
            if user_name not in rooms[room_key]["user_names"]:
                rooms[room_key]["user_names"].append(user_name)

            request.session['username'] = user_name
            request.session['room_key'] = room_key

            return RedirectResponse(url=f"/room/{room_key}", status_code=303)
        else:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "message": "Room not found"
            })

    return templates.TemplateResponse("guest.html", {"request": request})

async def room(request: Request) -> _TemplateResponse:
    room_key: str = request.path_params['key']
    if room_key in rooms:
        room_data = rooms[room_key]

        media_name: str = room_data.get("media_name", "Untitled")
        user_names: List[str] = room_data.get("user_names", [])

        video_url: str = f"{streaming_base_url}/stream/"

        logger.debug(f"Room key: {room_key}")
        logger.debug(f"Media name: {media_name}")
        logger.debug(f"User names: {user_names}")

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
        Route("/room/{key}", room, name="room"),
        Route("/guest", guest, name="guest", methods=["GET", "POST"]),
        WebSocketRoute("/ws/{room_key}", handle_connection),  # WebSocket route for chat
        Mount("/static", StaticFiles(directory="static"), name="static")
    ]
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
