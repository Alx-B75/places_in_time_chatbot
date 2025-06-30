document.addEventListener("DOMContentLoaded", () => {
  const authForm = document.getElementById("auth-form");
  const toggleLink = document.getElementById("toggle-auth");
  const formTitle = document.getElementById("form-title");
  const submitButton = document.getElementById("submit-button");
  const message = document.getElementById("message");

  let isLogin = true;

  toggleLink.addEventListener("click", (e) => {
    e.preventDefault();
    isLogin = !isLogin;

    formTitle.textContent = isLogin ? "Login" : "Register";
    submitButton.textContent = isLogin ? "Login" : "Register";
    toggleLink.textContent = isLogin
      ? "Don't have an account? Register"
      : "Already have an account? Login";
    message.textContent = "";
  });

  authForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = authForm.username.value;
    const password = authForm.password.value;
    const url = isLogin
      ? "https://places-backend-o8ym.onrender.com/login"
      : "https://places-backend-o8ym.onrender.com/register";

    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
        redirect: "follow"
      });

      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      if (!response.ok) {
        const data = await response.json();
        message.textContent = data.detail || "Something went wrong.";
      } else {
        message.textContent = isLogin
          ? "Logged in successfully!"
          : "Registration successful!";
      }
    } catch (error) {
      message.textContent = "Could not connect to the server. Please try again.";
    }
  });
});
