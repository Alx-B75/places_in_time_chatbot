document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("auth-form");
  const toggleLink = document.getElementById("toggle-auth");
  const title = document.getElementById("form-title");
  const message = document.getElementById("message");

  let isLogin = true;

  toggleLink.addEventListener("click", function (event) {
    event.preventDefault();
    isLogin = !isLogin;
    title.textContent = isLogin ? "Login" : "Register";
    toggleLink.textContent = isLogin
      ? "Don't have an account? Register"
      : "Already have an account? Login";
  });

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
      message.textContent = "Username and password are required.";
      return;
    }

    const endpoint = isLogin ? "/login_user" : "/register_user";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      const responseText = await response.text();
      let data;
      try {
        data = JSON.parse(responseText);
      } catch {
        data = {};
      }

      if (response.ok) {
        message.textContent = "Success!";
      } else {
        message.textContent = data.detail || "Something went wrong.";
      }

    } catch (err) {
      console.error("Error:", err);
      message.textContent = "Network error or server unavailable.";
    }
  });
});
