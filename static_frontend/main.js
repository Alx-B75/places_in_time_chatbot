document.addEventListener("DOMContentLoaded", function () {
  const authForm = document.getElementById("auth-form");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const messageDiv = document.getElementById("message");
  const formTitle = document.getElementById("form-title");
  const toggleAuthLink = document.getElementById("toggle-auth");
  const submitButton = document.getElementById("submit-button");

  let isRegisterMode = false;

  const API_BASE_URL = "https://your-backend.onrender.com"; // Replace this with your actual Render backend URL

  function updateUIForMode() {
    messageDiv.textContent = "";

    if (isRegisterMode) {
      formTitle.textContent = "Register";
      submitButton.textContent = "Register";
      toggleAuthLink.textContent = "Already have an account? Login";
    } else {
      formTitle.textContent = "Login";
      submitButton.textContent = "Login";
      toggleAuthLink.textContent = "Don't have an account? Register";
    }
  }

  updateUIForMode();

  toggleAuthLink.addEventListener("click", (e) => {
    e.preventDefault();
    isRegisterMode = !isRegisterMode;
    updateUIForMode();
  });

  if (authForm) {
    authForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = usernameInput.value.trim();
      const password = passwordInput.value;
      messageDiv.textContent = "";

      if (!username || !password) {
        messageDiv.textContent = "Please enter both username and password.";
        return;
      }

      let url = "";
      let successMessage = "";
      let failureMessage = "";

      if (isRegisterMode) {
        url = `${API_BASE_URL}/register`;
        successMessage = "Registration successful! Please log in.";
        failureMessage = "Registration failed.";
      } else {
        url = `${API_BASE_URL}/login`;
        successMessage = "Login successful!";
        failureMessage = "Login failed. Check your username and password.";
      }

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username,
            password
          }),
        });

        if (response.ok) {
          if (isRegisterMode) {
            messageDiv.textContent = successMessage;
            isRegisterMode = false;
            updateUIForMode();
            usernameInput.value = '';
            passwordInput.value = '';
          } else {
            const data = await response.json();
            if (data.user_id) {
              localStorage.setItem("user_id", data.user_id);
              window.location.href = "/dashboard.html";
            } else {
              messageDiv.textContent = "Login successful, but user ID not received.";
            }
          }
        } else {
          const data = await response.json();
          messageDiv.textContent = data.detail || failureMessage;
        }
      } catch (error) {
        console.error("Network or server error:", error);
        messageDiv.textContent = "Could not connect to the server. Please try again.";
      }
    });
  }
});
