document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("auth-form");
  const toggleLink = document.getElementById("toggle-auth");
  const title = document.getElementById("form-title");
  const button = document.getElementById("submit-button");
  const messageDiv = document.getElementById("message");

  let isLogin = true;

  toggleLink.addEventListener("click", (e) => {
    e.preventDefault();
    isLogin = !isLogin;
    title.textContent = isLogin ? "Login" : "Register";
    button.textContent = isLogin ? "Login" : "Register";
    toggleLink.textContent = isLogin
      ? "Don't have an account? Register"
      : "Already have an account? Login";
    messageDiv.textContent = "";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    messageDiv.textContent = "";

    const username = form.username.value;
    const password = form.password.value;
    const endpoint = isLogin ? "/login" : "/register";

    try {
      const response = await fetch(`https://places-backend-o8ym.onrender.com${endpoint}`, {
        method: "POST",
        headers: {
          "Accept": "text/html",
        },
        body: new URLSearchParams({ username, password }),
        redirect: "manual"
      });

      if (response.status === 302 || response.status === 303) {
        const location = response.headers.get("Location");
        if (location) {
          window.location.href = location.startsWith("http")
            ? location
            : `https://places-backend-o8ym.onrender.com${location}`;
        } else {
          messageDiv.textContent = "Redirect successful, but no location header was received.";
        }
      } else if (response.status === 401) {
        messageDiv.textContent = "Login failed: Invalid username or password.";
      } else if (response.status === 400) {
        const text = await response.text();
        messageDiv.textContent = `Registration failed: ${text}`;
      } else {
        const text = await response.text();
        messageDiv.textContent = `Unexpected response (${response.status}): ${text}`;
      }
    } catch (error) {
      console.error("Network error:", error);
      messageDiv.textContent = "Could not connect to the server. Please check your internet connection and try again.";
    }
  });
});
