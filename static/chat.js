// chat.js

document.addEventListener("DOMContentLoaded", () => {
    const roomKey = "{{ room_key }}";
    const wsUrl = `ws://${window.location.host}/ws/${encodeURIComponent(roomKey)}`;
    const socket = new WebSocket(wsUrl);

    const chat = document.getElementById('chat');
    const messageInput = document.getElementById('message-input');
    const messageForm = document.getElementById('message-form');

    // Handle incoming messages
    socket.onmessage = (event) => {
        const messageElem = document.createElement('div');
        messageElem.textContent = event.data;
        chat.appendChild(messageElem);
        chat.scrollTop = chat.scrollHeight;
    };

    // Send message on button click
    document.getElementById('send-button').addEventListener('click', () => {
        const message = messageInput.value.trim();
        if (message) {
            const data = JSON.stringify({ message });
            socket.send(data);
            messageInput.value = '';
        }
    });

    // Prevent form submission
    messageForm.addEventListener('submit', (event) => {
        event.preventDefault();
    });
});
