# socketHandler.py
from starlette.websockets import WebSocket
from starlette.responses import HTMLResponse
import json

async def handle_connection(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    # Handle case where data is not valid JSON
                    await websocket.send_text("Error: Invalid message format.")
                    continue

            if 'message' in data:
                # Broadcast message to all connected clients
                message = data['message']
                await websocket.send_text(f"Received: {message}")
                # You might want to broadcast the message to all clients here
            else:
                await websocket.send_text("Error: No message key in the data.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()
