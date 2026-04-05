import asyncio
import subprocess

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket

from web.state import get_state

app = FastAPI()
clients = set()


def notify_clients(message_type: str, data: dict | None = None):
    """Notify all connected WebSocket clients."""
    if data is None:
        data = {}

    for client in clients:
        try:
            asyncio.create_task(client.send_json({"type": message_type, "data": data}))
        except Exception:
            clients.remove(client)


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


@app.post("/start")
async def start_script():
    """Endpoint to run the start script."""
    try:
        result = subprocess.run(
            ["python", "scripts/start.py"], capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500, detail=f"Script failed: {result.stderr}"
            )

        notify_clients(
            "script_status",
            {"script": "start", "status": "success", "output": result.stdout},
        )

        return {"status": "success", "output": result.stdout}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Script execution timed out")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running script: {str(e)}")


@app.post("/end")
async def end_script():
    """Endpoint to run the end script."""
    try:
        result = subprocess.run(
            ["python", "scripts/end.py"], capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500, detail=f"Script failed: {result.stderr}"
            )

        notify_clients(
            "script_status",
            {"script": "end", "status": "success", "output": result.stdout},
        )

        return {"status": "success", "output": result.stdout}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Script execution timed out")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running script: {str(e)}")


def start_ws_server():
    uvicorn.run(app, host="0.0.0.0", port=3000)
