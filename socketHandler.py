from starlette.websockets import WebSocket, WebSocketDisconnect
from typing import List, Dict

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_key: str):
        await websocket.accept()
        if room_key not in self.active_connections:
            self.active_connections[room_key] = []
        self.active_connections[room_key].append(websocket)
        print(f"WebSocket connected: Room {room_key}, Total Connections: {len(self.active_connections[room_key])}")

    def disconnect(self, websocket: WebSocket, room_key: str):
        if room_key in self.active_connections:
            self.active_connections[room_key].remove(websocket)
            print(f"WebSocket disconnected: Room {room_key}, Total Connections: {len(self.active_connections[room_key])}")

    async def send_message(self, room_key: str, message: str):
        if room_key in self.active_connections:
            for connection in self.active_connections[room_key]:
                await connection.send_text(message)

manager = WebSocketConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    room_key = websocket.query_params.get('room_key')
    if not room_key:
        await websocket.close(code=4000)  # Close connection if room_key is missing
        return
    await manager.connect(websocket, room_key)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(room_key, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_key)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)  # Close connection with a generic error code
