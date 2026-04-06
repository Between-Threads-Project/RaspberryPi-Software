import asyncio
import importlib
import threading

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from web.state import consume_dirty, get_state

receiver_thread = None
receiver_stop_event = None

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://100.127.151.6:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket clients ---
clients = set()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)

    try:
        while True:
            await asyncio.sleep(0.05)

            if consume_dirty():
                await ws.send_json({"type": "servo_update", "data": get_state()})

    except Exception:
        clients.discard(ws)


# --- Script runner (CORE) ---
def run_script(module: str, name: str):
    try:
        mod = importlib.import_module(module)

        if not hasattr(mod, "main"):
            raise HTTPException(
                status_code=500,
                detail=f"{name} has no main() function",
            )

        mod.main()

        return {"status": "success", "message": f"{name} executed"}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"{name} failed: {str(e)}",
        )


# --- API endpoints ---
@app.post("/start")
async def start_script():
    return run_script("scripts.start", "start")


@app.post("/end")
async def end_script():
    return run_script("scripts.end", "end")


@app.post("/start_receiver")
async def start_receiver():
    global receiver_thread, receiver_stop_event

    if receiver_thread and receiver_thread.is_alive():
        return {"status": "already_running"}

    receiver = importlib.import_module("scripts.receiver")

    receiver_stop_event = threading.Event()

    receiver_thread = threading.Thread(
        target=receiver.main,
        args=(receiver_stop_event,),
        daemon=True,
    )

    receiver_thread.start()

    return {"status": "started"}


@app.post("/stop_receiver")
async def stop_receiver():
    global receiver_stop_event

    if not receiver_stop_event:
        return {"status": "not_running"}

    receiver_stop_event.set()

    return {"status": "stopping"}


# --- Server ---
def start_ws_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_ws_server()
