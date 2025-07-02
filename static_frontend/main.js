document.addEventListener("DOMContentLoaded", () => {
  const pathname = window.location.pathname;
  const backendUrl = "https://places-backend-o8ym.onrender.com";

  // === LOGIN + REGISTER LOGIC ===
  const authForm = document.getElementById("auth-form");
  const toggleLink = document.getElementById("toggle-auth");
  const formTitle = document.getElementById("form-title");
  const messageBox = document.getElementById("message");

  if (authForm && toggleLink && formTitle) {
    let isLogin = true;

    toggleLink.addEventListener("click", (e) => {
      e.preventDefault();
      isLogin = !isLogin;
      formTitle.textContent = isLogin ? "Login" : "Register";
      toggleLink.textContent = isLogin
        ? "Don't have an account? Register"
        : "Already have an account? Login";
      authForm.querySelector("button").textContent = isLogin ? "Login" : "Register";
      messageBox.textContent = ""; // Clear any previous error messages
    });

    authForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = authForm.username.value;
      const password = authForm.password.value;
      const endpoint = isLogin ? "login" : "register";
      messageBox.textContent = ""; // Clear message box

      try {
        const response = await fetch(`${backendUrl}/${endpoint}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
          body: new URLSearchParams({ username, password }),
          // We no longer expect a redirect, so the 'redirect' property is removed.
        });

        // The backend now sends JSON on success (200 OK) and failure (4xx).
        const data = await response.json();

        if (response.ok) {
          // SUCCESS: The backend sent us the user_id.
          // We now construct the frontend URL and navigate there.
          window.location.href = `/user/${data.user_id}/threads`;
        } else {
          // FAILURE: The backend sent an error message.
          messageBox.textContent = data.detail || "An unknown error occurred.";
        }

      } catch (err) {
        messageBox.textContent = "Error: Could not connect to the server.";
        console.error("Network or server error:", err);
      }
    });
  }

  // === THREADS PAGE LOGIC ===
if (pathname.includes("/user/") && pathname.includes("/threads")) {
    const userIdMatch = pathname.match(/\/user\/(\d+)\/threads/);
    const userId = userIdMatch ? userIdMatch[1] : null;

    if (userId) {
        // --- This is the new code to add ---
        const newThreadButton = document.getElementById("new-thread-button");
        if (newThreadButton) {
            newThreadButton.addEventListener("click", () => {
                // Navigate to the backend's page for asking a new figure, passing the user's ID
                window.location.href = `${backendUrl}/figures/ask?user_id=${userId}`;
            });
        }
        // --- End of new code ---

        // This is your existing code for fetching and displaying threads
        fetch(`${backendUrl}/threads/user/${userId}`)
            .then((res) => {
                if (!res.ok) {
                    throw new Error(`Server responded with status: ${res.status}`);
                }
                return res.json();
            })
            .then((threads) => {
                const threadsList = document.getElementById("threads-list");
                if (!threadsList) return;

                if (!threads || threads.length === 0) {
                    threadsList.innerHTML = "<p>You have no chat threads. Start a new one!</p>";
                    return;
                }

                threadsList.innerHTML = ""; // Clear any loading text
                threads.forEach((thread) => {
                    const item = document.createElement("div");
                    item.className = "thread-box";
                    item.innerHTML = `
                        <a href="${backendUrl}/thread/${thread.id}">
                            ${thread.title || "Untitled Thread"}
                        </a>
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