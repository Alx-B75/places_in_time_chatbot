document.addEventListener("DOMContentLoaded", () => {
  const pathname = window.location.pathname;

  // === LOGIN + REGISTER ===
  const form = document.getElementById("auth-form");
  const toggleLink = document.getElementById("toggle-auth");
  const formTitle = document.getElementById("form-title");
  const messageBox = document.getElementById("message");

  if (form && toggleLink && formTitle) {
    let isLogin = true;

    toggleLink.addEventListener("click", (e) => {
      e.preventDefault();
      isLogin = !isLogin;
      formTitle.textContent = isLogin ? "Login" : "Register";
      toggleLink.textContent = isLogin
        ? "Don't have an account? Register"
        : "Already have an account? Login";
      form.querySelector("button").textContent = isLogin ? "Login" : "Register";
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = form.username.value;
      const password = form.password.value;
      const endpoint = isLogin ? "login" : "register";

      try {
        const response = await fetch(`https://places-backend-o8ym.onrender.com/${endpoint}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
          body: new URLSearchParams({ username, password }),
          redirect: "follow",
        });

        if (response.redirected) {
          window.location.href = response.url;
        } else if (response.status === 401) {
          const errorData = await response.json();
          messageBox.textContent = "Login failed: " + (errorData.detail || "Check credentials.");
        } else {
          const errorText = await response.text();
          messageBox.textContent = "Unexpected response (" + response.status + "): " + errorText;
        }
      } catch (err) {
        messageBox.textContent = "Error: Could not connect to server. Check your connection.";
      }
    });
  }

  // === THREADS PAGE ===
  if (pathname.includes("/user/") && pathname.includes("/threads")) {
    const userIdMatch = pathname.match(/\/user\/(\d+)\/threads/);
    const userId = userIdMatch ? userIdMatch[1] : null;

    if (userId) {
      fetch(`https://places-backend-o8ym.onrender.com/threads/user/${userId}`)
        .then((res) => res.json())
        .then((threads) => {
          const container = document.getElementById("thread-list");
          if (!container) return;

          if (threads.length === 0) {
            container.innerHTML = "<p>No threads yet.</p>";
            return;
          }

          container.innerHTML = "";
          threads.forEach((thread) => {
            const item = document.createElement("div");
            item.className = "thread-item";
            item.innerHTML = `
              <a href="https://places-backend-o8ym.onrender.com/thread/${thread.id}">
                ${thread.title || "Untitled Thread"} – ${new Date(thread.created_at).toLocaleString()}
              </a>
            `;
            container.appendChild(item);
          });
        })
        .catch((err) => {
          const container = document.getElementById("thread-list");
          if (container) container.innerHTML = "<p>Error loading threads.</p>";
        });
    }
  }
});
