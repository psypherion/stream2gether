from starlette.websockets import WebSocket
import json

# Dictionary to store connected WebSockets for each room
connected_users = {}

async def handle_connection(websocket: WebSocket):
    room_key = websocket.path_params['room_key']
    username = websocket.session.get('username', 'anon')  # Retrieve username from session

    # Accept the WebSocket connection
    await websocket.accept()

    if room_key not in connected_users:
        connected_users[room_key] = []

    # Add the new WebSocket connection and the username to the list
    connected_users[room_key].append({'websocket': websocket, 'username': username})

    # Notify all clients about the updated list of users in the room
    await broadcast_user_list(room_key)

    try:
        while True:
            data = await websocket.receive_text()
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_text("Error: Invalid message format.")
                    continue

            if 'message' in data:
                # Format message as 'username: message'
                message = f"{username}: {data['message']}"

                # Broadcast the message to all users in the room
                await broadcast_message(room_key, message)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Remove the WebSocket connection when the user disconnects
        connected_users[room_key] = [
            user for user in connected_users[room_key] if user['websocket'] != websocket
        ]
        await broadcast_user_list(room_key)
        await websocket.close()

async def broadcast_message(room_key: str, message: str):
    for user in connected_users.get(room_key, []):
        await user['websocket'].send_text(json.dumps({"type": "message", "data": message}))

async def broadcast_user_list(room_key: str):
    # Get the list of usernames in the room
    user_list = [user['username'] for user in connected_users.get(room_key, [])]
    # Broadcast the user list to all users in the room
    for user in connected_users.get(room_key, []):
        await user['websocket'].send_text(json.dumps({"type": "user_list", "data": user_list}))
