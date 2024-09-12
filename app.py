import uuid
import shutil
from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

