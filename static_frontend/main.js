document.addEventListener("DOMContentLoaded", function () {
  const registerForm = document.getElementById("registerForm");
  const loginForm = document.getElementById("loginForm");

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("registerUsername").value;
      const password = document.getElementById("registerPassword").value;
      const message = document.getElementById("registerMessage");

      try {
        const response = await fetch("/register_user", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
          message.textContent = "Registration successful. Please log in.";
        } else {
          message.textContent = data.detail || "Registration failed.";
        }
      } catch (err) {
        console.error("Error:", err);
        message.textContent = "Network error or server unavailable.";
      }
    });
  }

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const username = document.getElementById("loginUsername").value;
      const password = document.getElementById("loginPassword").value;
      const message = document.getElementById("loginMessage");

      try {
        const response = await fetch("/login_user", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.user_id) {
          localStorage.setItem("user_id", data.user_id);
          window.location.href = "/static_frontend/dashboard.html";
        } else {
          message.textContent = data.detail || "Login failed.";
        }
      } catch (err) {
        console.error("Error:", err);
        message.textContent = "Network error or server unavailable.";
      }
    });
  }
});
