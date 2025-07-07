document.addEventListener("DOMContentLoaded", () => {
    // This function automatically selects the correct backend URL
    const getBackendUrl = () => {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // We are on the local machine for testing
            return 'http://localhost:8000';
        }
        // We are on the live site
        return 'https://places-backend-o8ym.onrender.com';
    };

    const backendUrl = getBackendUrl();
    const pathname = window.location.pathname;

    // === LOGIN + REGISTER LOGIC (on index.html) ===
    const authForm = document.getElementById("auth-form");
    if (authForm) {
        const toggleLink = document.getElementById("toggle-auth");
        const formTitle = document.getElementById("form-title");
        const messageBox = document.getElementById("message");
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
                        // Save the token to the browser's local storage
                        localStorage.setItem("placesInTimeToken", data.access_token);
                        // Use the user_id from the response to redirect
                        window.location.href = `/user/${data.user_id}/threads`;
                    } else {
                         // Handle a successful registration
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

    // === THREADS PAGE LOGIC (on threads.html) ===
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
                threadsList.innerHTML = "<p>You are not logged in. Redirecting...</p>";
                window.location.href = "/";
                return;
            }

            // Fetch threads using the Authorization header
            fetch(`${backendUrl}/threads/user/${userId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
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
                    return;
                }

                threadsList.innerHTML = "";
                threads.forEach((thread) => {
                    const item = document.createElement("div");
                    item.className = "thread-box";
                    // This now correctly points to the backend
                    item.innerHTML = `
                        <a href="${backendUrl}/thread/${thread.id}">${thread.title || "Untitled Thread"}</a>
                        <p>Created: ${new Date(thread.created_at).toLocaleString()}</p>
                    `;
                    threadsList.appendChild(item);
                });
            })
            .catch((err) => {
                if (err.message !== "Unauthorized") {
                    if (threadsList) {
                        threadsList.innerHTML = "<p style='color: red;'>Error: Could not load your threads.</p>";
                    }
                    console.error("Error loading threads:", err);
                }
            });
        }
    }
});