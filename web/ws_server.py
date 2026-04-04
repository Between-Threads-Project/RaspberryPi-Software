import asyncio

import uvicorn
from fastapi import FastAPI, WebSocket
from state import get_state

app = FastAPI()
clients = set()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)

    try:
        while True:
            await asyncio.sleep(0.05)  # ~20 FPS
            await ws.send_json({"type": "servo_update", "data": get_state()})
    except Exception:
        clients.remove(ws)


def start_ws_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)
