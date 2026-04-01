import asyncio
import json
import os
import subprocess

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

USER = os.getenv("USER") or os.getlogin()
HOME = os.path.expanduser("~")
UV_PATH = os.path.join(HOME, ".local", "bin", "uv")

BASE_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(BASE_DIR, "state.json")

app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"servos": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


state = load_state()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


def run_script(script_name: str):
    subprocess.Popen([UV_PATH, "run", script_name])


@app.post("/start")
async def start():
    run_script("start.py")
    return {"message": "start launched"}


@app.post("/end")
async def end():
    run_script("end.py")
    return {"message": "end launched"}


@app.post("/main")
async def main():
    run_script("main.py")
    return {"message": "main launched"}


@app.get("/state")
def get_state():
    return state


@app.post("/state")
async def update_state(new_state: dict):
    global state
    state.update(new_state)
    save_state(state)

    # broadcast temps réel
    await manager.broadcast(state)

    return {"status": "updated"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        # envoie état initial
        await websocket.send_json(state)

        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
