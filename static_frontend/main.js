document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("register-form");
  const loginForm = document.getElementById("login-form");

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("register-username").value;
      const password = document.getElementById("register-password").value;
      const message = document.getElementById("register-message");

      try {
        const response = await fetch("/register_user", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) {
          message.textContent = "Registration successful! Redirecting...";
          setTimeout(() => {
            window.location.href = "index.html";
          }, 1000);
        } else {
          message.textContent = data.detail || "Registration failed.";
        }
      } catch (err) {
        console.error("Register error:", err);
        message.textContent = "Network error or server unavailable.";
      }
    });
  }

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("login-username").value;
      const password = document.getElementById("login-password").value;
      const message = document.getElementById("login-message");

      try {
        const response = await fetch("/login_user", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) {
          localStorage.setItem("user_id", data.user_id);
          localStorage.setItem("username", data.username);
          message.textContent = "Success!";
          window.location.href = "threads.html";
        } else {
          message.textContent = data.detail || "Login failed.";
        }
      } catch (err) {
        console.error("Login error:", err);
        message.textContent = "Network error or server unavailable.";
      }
    });
  }
});
