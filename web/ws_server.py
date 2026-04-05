import asyncio
import subprocess

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from web.state import get_state

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket clients ---
clients = set()


def notify_clients(message_type: str, data: dict | None = None):
    if data is None:
        data = {}

    dead_clients = set()

    for client in clients:
        try:
            asyncio.create_task(client.send_json({"type": message_type, "data": data}))
        except Exception:
            dead_clients.add(client)

    clients.difference_update(dead_clients)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)

    try:
        while True:
            await asyncio.sleep(0.05)
            await ws.send_json({"type": "servo_update", "data": get_state()})
    except Exception:
        clients.discard(ws)


# --- Script runner (CORE) ---
def run_script(module: str, name: str):
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", module],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"{name} failed: {result.stderr}",
            )

        notify_clients(
            "script_status",
            {"script": name, "status": "success", "output": result.stdout},
        )

        return {"status": "success", "output": result.stdout}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail=f"{name} timed out")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- API endpoints ---
@app.post("/start")
async def start_script():
    return run_script("scripts.start", "start")


@app.post("/end")
async def end_script():
    return run_script("scripts.end", "end")


@app.post("/main")
async def main_script():
    return run_script("scripts.receiver", "receiver")


# --- Server ---
def start_ws_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_ws_server()
