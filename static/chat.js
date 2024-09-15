document.addEventListener("DOMContentLoaded", () => {
    const roomKey = "{{ room_key }}";
    const wsUrl = `ws://${window.location.host}/ws/${encodeURIComponent(roomKey)}`;
    const socket = new WebSocket(wsUrl);

    const chat = document.getElementById('chat');
    const messageInput = document.getElementById('message-input');
    const messageForm = document.getElementById('message-form');

    // Handle incoming messages
    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data); // Parse the incoming JSON
            console.log("Received WebSocket data:", data); // Debugging: log received data

            // Check for the message type
            if (data.type === 'message') {
                // Display only the chat message, e.g., 'username: message'
                const messageElem = document.createElement('div');
                messageElem.textContent = data.data; // This should show "username: message"
                chat.appendChild(messageElem);
                chat.scrollTop = chat.scrollHeight; // Scroll to the latest message

            } else if (data.type === 'user_list') {
                // Update the list of joined users
                const joinedUsersElement = document.querySelector('.chatHead p');
                joinedUsersElement.innerHTML = `Joined Users: ${data.data.join(' | ')}`;
            }

        } catch (error) {
            console.error("Error parsing WebSocket message:", error, event.data);
            // Optionally, display a message to the user or log the error in the UI.
        }
    };

    // Send message on button click
    document.getElementById('send-button').addEventListener('click', () => {
        const message = messageInput.value.trim();
        if (message) {
            const data = JSON.stringify({ message });
            socket.send(data); // Send the message to the WebSocket server
            messageInput.value = ''; // Clear the input field
        }
    });

    // Prevent form submission
    messageForm.addEventListener('submit', (event) => {
        event.preventDefault();
    });
});
