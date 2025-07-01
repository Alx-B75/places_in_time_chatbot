const form = document.getElementById("auth-form");
const toggleLink = document.getElementById("toggle-auth");
const formTitle = document.getElementById("form-title");
const submitButton = document.getElementById("submit-button");
const messageDiv = document.getElementById("message");

let isLogin = true;

const BACKEND_URL = "https://places-backend-o8ym.onrender.com";

toggleLink.addEventListener("click", (e) => {
  e.preventDefault();
  isLogin = !isLogin;

  formTitle.textContent = isLogin ? "Login" : "Register";
  submitButton.textContent = isLogin ? "Login" : "Register";
  toggleLink.textContent = isLogin
    ? "Don't have an account? Register"
    : "Already have an account? Login";
  messageDiv.textContent = "";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(form);
  const endpoint = isLogin ? "/login" : "/register";

  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: "POST",
      body: formData,
      redirect: "follow",
    });

    if (response.redirected) {
      window.location.href = response.url;
    } else if (!response.ok) {
      const text = await response.text();
      let errorMessage = "Login or registration failed.";
      if (response.status === 401) {
        errorMessage = "Invalid username or password.";
      } else if (response.status === 400 && text.includes("Username and password required")) {
        errorMessage = "Please enter both a username and password.";
      } else if (response.status === 400 || text.includes("UNIQUE constraint failed")) {
        errorMessage = "Username already exists.";
      } else {
        errorMessage = `Unexpected server response (${response.status}).`;
      }
      messageDiv.textContent = errorMessage;
    } else {
      messageDiv.textContent = "Success, redirecting...";
    }
  } catch (err) {
    messageDiv.textContent = "Could not connect to the server. Please try again.";
  }
});
