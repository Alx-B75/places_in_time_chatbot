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
        const toggleLink = document.getElementById("toggle-auth");
        const formTitle = document.getElementById("form-title");
        const messageBox = document.getElementById("message");
        let isLogin = true;

        if (toggleLink) {
            toggleLink.addEventListener("click", (e) => {
                e.preventDefault();
                isLogin = !isLogin;
                formTitle.textContent = isLogin ? "Login" : "Register";
                toggleLink.textContent = isLogin ? "Don't have an account? Register" : "Already have an account? Login";
                authForm.querySelector("button").textContent = isLogin ? "Login" : "Register";
                messageBox.textContent = "";
            });
        }

        authForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = authForm.username.value;
            const password = authForm.password.value;
            const endpoint = isLogin ? "login" : "register";
            messageBox.textContent = "";

            try {
                const response = await fetch(`${backendUrl}/${endpoint}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                    },
                    body: new URLSearchParams({ username, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    if (data.access_token) {
                        localStorage.setItem("placesInTimeToken", data.access_token);
                        window.location.href = `/user/${data.user_id}/threads`;
                    } else {
                         alert("Registration successful! Please log in.");
                         window.location.reload();
                    }
                } else {
                    messageBox.textContent = data.detail || "An unknown error occurred.";
                }
            } catch (err) {
                messageBox.textContent = "Error: Could not connect to the server.";
                console.error("Network or server error:", err);
            }
        });
    }

    // --- THREADS PAGE LOGIC ---
    if (pathname.includes("/user/") && pathname.includes("/threads")) {
        const userIdMatch = pathname.match(/\/user\/(\d+)\/threads/);
        const userId = userIdMatch ? userIdMatch[1] : null;

        if (userId) {
            const newThreadButton = document.getElementById("new-thread-button");
            if (newThreadButton) {
                newThreadButton.addEventListener("click", () => {
                    window.location.href = `${backendUrl}/figures/ask?user_id=${userId}`;
                });
            }

            const token = localStorage.getItem("placesInTimeToken");
            const threadsList = document.getElementById("threads-list");

            if (!token) {
                if (threadsList) threadsList.innerHTML = "<p>You are not logged in. Redirecting...</p>";
                window.location.href = "/";
                return;
            }

            fetch(`${backendUrl}/threads/user/${userId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            .then((res) => {
                if (res.status === 401) {
                    localStorage.removeItem("placesInTimeToken");
                    window.location.href = "/";
                    throw new Error("Unauthorized");
                }
                if (!res.ok) throw new Error(`Server responded with status: ${res.status}`);
                return res.json();
            })
            .then((threads) => {
                if (!threadsList) return;
                if (!threads || threads.length === 0) {
                    threadsList.innerHTML = "<p>You have no chat threads. Start a new one!</p>";
                } else {
                    threadsList.innerHTML = "";
                    threads.forEach((thread) => {
                        const item = document.createElement("div");
                        item.className = "thread-box";
                        item.innerHTML = `
                            <a href="${backendUrl}/thread/${thread.id}">${thread.title || "Untitled Thread"}</a>
                            <p>Created: ${new Date(thread.created_at).toLocaleString()}</p>
                        `;
                        threadsList.appendChild(item);
                    });
                }
            })
            .catch((err) => {
                if (err.message !== "Unauthorized" && threadsList) {
                    threadsList.innerHTML = "<p style='color: red;'>Error: Could not load your threads.</p>";
                }
                console.error("Error loading threads:", err);
            });
        }
    }

    // --- DYNAMIC CHAT FORM LOGIC ---
    const chatForm = document.getElementById("chat-form");
    if (chatForm) {
        const thinkingIndicator = document.getElementById("thinking-indicator");
        const messagesContainer = document.getElementById("messages-container");
        const submitButton = document.getElementById("submit-button");
        const messageInput = document.getElementById("message-input");

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
            const figureHeader = document.querySelector(".figure-text-container h1");
            const figureName = figureHeader ? figureHeader.textContent.replace('Chat with ', '') : 'Historical Guide';
            const token = localStorage.getItem("placesInTimeToken");

            thinkingIndicator.textContent = `${figureName} is thinking...`;
            thinkingIndicator.style.display = "block";
            submitButton.disabled = true;
            appendMessageToChat('user', 'Your Question', messageText);
            messageInput.value = "";

            try {
                const response = await fetch(`${backendUrl}/ask`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        user_id: parseInt(userId), message: messageText, figure_slug: figureSlug,
                        thread_id: threadId ? parseInt(threadId) : null
                    })
                });

                thinkingIndicator.style.display = "none";
                submitButton.disabled = false;

                if (response.ok) {
                    const newChatMessage = await response.json();
                    appendMessageToChat('assistant', figureName, newChatMessage.message);
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
            messageBubble.innerHTML = `<span class="message-role">${senderName}</span><p class="message-content"></p>`;
            messageBubble.querySelector('.message-content').textContent = message;
            messageWrapper.appendChild(messageBubble);
            messagesContainer.appendChild(messageWrapper);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
});