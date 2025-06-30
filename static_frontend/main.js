document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("auth-form");
  const toggle = document.getElementById("toggle-auth");
  const title = document.getElementById("form-title");
  const button = document.getElementById("submit-button");
  const message = document.getElementById("message");

  let isLogin = true;

  toggle.addEventListener("click", (e) => {
    e.preventDefault();
    isLogin = !isLogin;
    title.textContent = isLogin ? "Login" : "Register";
    button.textContent = isLogin ? "Login" : "Register";
    toggle.textContent = isLogin
      ? "Don't have an account? Register"
      : "Already have an account? Login";
    message.textContent = "";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    message.textContent = "";

    const endpoint = isLogin ? "/login" : "/register";
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch("https://places-backend-o8ym.onrender.com" + endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
        redirect: "manual"
      });

      if (response.status === 302 || response.status === 303) {
        window.location.href = "dashboard.html";
      } else {
        const errorText = await response.text();
        message.textContent = `Error (${response.status}): ${errorText}`;
      }
    } catch (error) {
      message.textContent = "Could not connect to the server. Please try again.";
      console.error("Network error:", error);
    }
  });
});
