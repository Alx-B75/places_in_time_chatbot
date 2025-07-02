document.addEventListener("DOMContentLoaded", () => {
    const pathname = window.location.pathname;
    const backendUrl = "https://places-backend-o8ym.onrender.com";

    // === LOGIN + REGISTER LOGIC (on index.html) ===
    const authForm = document.getElementById("auth-form");
    const toggleLink = document.getElementById("toggle-auth");
    const formTitle = document.getElementById("form-title");
    const messageBox = document.getElementById("message");

    if (authForm) {
        let isLogin = true;

        toggleLink.addEventListener("click", (e) => {
            e.preventDefault();
            isLogin = !isLogin;
            formTitle.textContent = isLogin ? "Login" : "Register";
            toggleLink.textContent = isLogin
                ? "Don't have an account? Register"
                : "Already have an account? Login";
            authForm.querySelector("button").textContent = isLogin ? "Login" : "Register";
            messageBox.textContent = "";
        });

        authForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // This is the line that fails to run when there's a syntax error
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
                    window.location.href = `/user/${data.user_id}/threads`;
                } else {
                    messageBox.textContent = data.detail || "An unknown error occurred.";
                }
            } catch (err) {
                messageBox.textContent = "Error: Could not connect to the server.";
                console.error("Network or server error:", err);
            }
        });
    }

    // === THREADS PAGE LOGIC (on threads.html) ===
    if (pathname.includes("/user/") && pathname.includes("/threads")) {
        const userIdMatch = pathname.match(/\/user\/(\d+)\/threads/);
        const userId = userIdMatch ? userIdMatch[1] : null;

        if (userId) {
            // Event listener for the "New Thread" button
            const newThreadButton = document.getElementById("new-thread-button");
            if (newThreadButton) {
                newThreadButton.addEventListener("click", () => {
                    window.location.href = `${backendUrl}/figures/ask?user_id=${userId}`;
                });
            }

            // Fetch and display existing threads
            fetch(`${backendUrl}/threads/user/${userId}`)
                .then((res) => {
                    if (!res.ok) throw new Error(`Server responded with status: ${res.status}`);
                    return res.json();
                })
                .then((threads) => {
                    const threadsList = document.getElementById("threads-list");
                    if (!threadsList) return;

                    if (!threads || threads.length === 0) {
                        threadsList.innerHTML = "<p>You have no chat threads. Start a new one!</p>";
                        return;
                    }

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
                })
                .catch((err) => {
                    const threadsList = document.getElementById("threads-list");
                    if (threadsList) {
                        threadsList.innerHTML = "<p style='color: red;'>Error: Could not load your threads.</p>";
                    }
                    console.error("Error loading threads:", err);
                });
        }
    }
});