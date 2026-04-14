from __future__ import annotations

import socketio
from fastapi import FastAPI

from src.sockets.server import create_socket_server

app = FastAPI()


@app.get("/")
async def root():
    return {"success": True, "service": "realtime-service", "message": "D-Lite realtime service is running", "sockets": {"chat": "socket.io", "calls": "socket.io"}}


@app.get("/health")
async def health():
    return {"success": True, "service": "realtime-service", "status": "ok"}

sio = create_socket_server()
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

