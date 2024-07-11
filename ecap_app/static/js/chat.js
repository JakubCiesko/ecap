document.getElementById('send-btn').addEventListener('click', function() {
    var userMessage = document.getElementById('user-message').value;
    if (userMessage.trim() !== "") {
        addMessageToChatBox("You", userMessage, "#38c7aa");
        sendMessageToServer(userMessage);
    }
    document.getElementById('user-message').value = "";
});

function addMessageToChatBox(sender, message, color) {
    var chatBox = document.getElementById('chat-box');
    var messageElement = document.createElement('div');
    messageElement.innerHTML = "<strong style='color: " + color + ";'>" + sender + ":</strong> " + message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
}

function sendMessageToServer(message) {
    fetch('/process_message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // CSRF token for security
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addMessageToChatBox("LLM", data.response, "#BB436C");
        } else {
            console.error("Error processing message:", data.error);
        }
    })
    .catch(error => {
        console.error("Error sending message:", error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
