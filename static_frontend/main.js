document.addEventListener("DOMContentLoaded", () => {
  let mode = "login"; // Can be 'login' or 'register'

  const formTitle = document.getElementById("form-title");
  const authForm = document.getElementById("auth-form");
  const submitButton = document.getElementById("submit-button");
  const toggleLink = document.getElementById("toggle-link");
  const messageArea = document.getElementById("message-area");

  toggleLink.addEventListener("click", (e) => {
    e.preventDefault();
    if (mode === "login") {
      mode = "register";
      formTitle.textContent = "Register";
      submitButton.textContent = "Register";
      toggleLink.textContent = "Already have an account? Login here";
    } else {
      mode = "login";
      formTitle.textContent = "Login";
      submitButton.textContent = "Login";
      toggleLink.textContent = "Don't have an account? Register here";
    }
    messageArea.textContent = "";
  });

  authForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const endpoint = mode === "login" ? "/login_user" : "/register_user";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: new URLSearchParams({ username, password }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      if (response.redirected) {
        window.location.href = response.url;
      } else {
        const text = await response.text();
        messageArea.textContent = text.includes("successfully")
          ? "✅ Success"
          : `⚠️ ${text}`;
      }
    } catch (err) {
      messageArea.textContent = "❌ Network error. Try again.";
    }
  });
});

