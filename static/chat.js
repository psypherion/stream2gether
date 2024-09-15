document.addEventListener('DOMContentLoaded', () => {
    // Ensure room_key is fetched correctly from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const roomKey = urlParams.get('room_key');

    if (!roomKey) {
        console.error('Room key is missing.');
        return;
    }

    // Function to create WebSocket connection
    function createWebSocket(roomKey) {
        const ws = new WebSocket('ws://' + window.location.host + '/ws?room_key=' + encodeURIComponent(roomKey));

        ws.onopen = () => {
            console.log('WebSocket connection opened');
        };

        ws.onclose = (event) => {
            console.log('WebSocket connection closed', event);
            // Optionally, you can implement a reconnection strategy here
            setTimeout(() => {
                createWebSocket(roomKey);
            }, 1000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error', error);
        };

        ws.onmessage = (event) => {
            const message = event.data;
            const messageElement = document.createElement('div');
            messageElement.textContent = message;
            document.getElementById('chat').appendChild(messageElement);
        };

        return ws;
    }

    const socket = createWebSocket(roomKey);

    document.getElementById('send-button').addEventListener('click', (event) => {
        event.preventDefault(); // Prevent form submission and page refresh
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value;
        if (message.trim() !== '') {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(message);
                messageInput.value = ''; // Clear the input field
            } else {
                console.warn('WebSocket is not open. Message not sent.');
            }
        }
    });

    // Prevent page refresh on form submission
    document.getElementById('join-us').addEventListener('submit', (event) => {
        event.preventDefault();
    });
});
