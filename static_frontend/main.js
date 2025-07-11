document.addEventListener("DOMContentLoaded", () => {
    // This function automatically selects the correct backend URL
    const getBackendUrl = () => {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        return 'https://places-backend-o8ym.onrender.com';
    };

    const backendUrl = getBackendUrl();
    const pathname = window.location.pathname;

    // --- LOGIN & REGISTER LOGIC ---
    const authForm = document.getElementById("auth-form");
    if (authForm) {
        // ... (existing login/register code is unchanged)
    }

    // --- THREADS PAGE LOGIC ---
    if (pathname.includes("/user/") && pathname.includes("/threads")) {
        // ... (existing threads page logic is unchanged)
    }

    // --- DYNAMIC CHAT FORM LOGIC ---
    const chatForm = document.getElementById("chat-form");
    if (chatForm) {
        const thinkingIndicator = document.getElementById("thinking-indicator");
        const messagesContainer = document.getElementById("messages-container");
        const submitButton = document.getElementById("submit-button");
        const messageInput = document.getElementById("message-input");

        // Auto-scroll chat to the bottom on page load
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        chatForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const messageText = messageInput.value.trim();
            if (!messageText) return;

            const userId = document.getElementById("user_id").value;
            let threadId = document.getElementById("thread_id").value;
            const figureSlug = document.getElementById("figure_slug").value;
            const figureName = document.querySelector(".figure-text-container h1")?.textContent.replace('Chat with ', '') || 'Historical Guide';
            const token = localStorage.getItem("placesInTimeToken");

            // 1. Update UI to show loading state
            thinkingIndicator.textContent = `${figureName} is thinking...`;
            thinkingIndicator.style.display = "block";
            submitButton.disabled = true;
            appendMessageToChat('user', 'Your Question', messageText);
            messageInput.value = "";

            // 2. Send data to the backend API
            try {
                const response = await fetch(`${backendUrl}/ask`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        user_id: parseInt(userId),
                        message: messageText,
                        figure_slug: figureSlug,
                        thread_id: threadId ? parseInt(threadId) : null
                    })
                });

                thinkingIndicator.style.display = "none";
                submitButton.disabled = false;

                if (response.ok) {
                    const newChatMessage = await response.json();
                    appendMessageToChat('assistant', figureName, newChatMessage.message);

                    // If this was the first message in a new thread, update the hidden thread_id input
                    if (!threadId && newChatMessage.thread_id) {
                        document.getElementById("thread_id").value = newChatMessage.thread_id;
                    }
                } else {
                     appendMessageToChat('assistant', 'Error', 'Sorry, an error occurred.');
                }

            } catch (error) {
                 thinkingIndicator.style.display = "none";
                 submitButton.disabled = false;
                 appendMessageToChat('assistant', 'Error', 'Could not connect to the server.');
            }
        });

        function appendMessageToChat(role, senderName, message) {
            if (!messagesContainer) return;
            const messageWrapper = document.createElement('div');
            messageWrapper.className = `message-wrapper ${role}-message`;

            const messageBubble = document.createElement('div');
            messageBubble.className = 'message-bubble';
            messageBubble.innerHTML = `
                <span class="message-role">${senderName}</span>
                <p class="message-content"></p>
            `;
            // Set textContent to prevent HTML injection
            messageBubble.querySelector('.message-content').textContent = message;

            messageWrapper.appendChild(messageBubble);
            messagesContainer.appendChild(messageWrapper);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
});