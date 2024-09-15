from starlette.websockets import WebSocket
import json

# Dictionary to keep track of connected clients and their usernames
connected_clients = {}

async def handle_connection(websocket: WebSocket):
    await websocket.accept()

    try:
        # Extract username from the session
        username = websocket.session.get('username', 'anon')  # Default to 'anon' if no username is set
        connected_clients[websocket] = username

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
                # Format the message as "username: message"
                message = data['message']
                formatted_message = f"{username}: {message}"

                # Broadcast message to all connected clients
                await broadcast_message(formatted_message)
            else:
                await websocket.send_text("Error: No message key in the data.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Remove client from connected_clients on disconnect
        connected_clients.pop(websocket, None)
        await websocket.close()


async def broadcast_message(message: str):
    """
    Broadcasts a message to all connected clients.
    """
    disconnected_clients = []
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception as e:
            print(f"Error sending message to client: {e}")
            disconnected_clients.append(client)

    # Remove disconnected clients from the list
    for client in disconnected_clients:
        connected_clients.pop(client, None)
