document.addEventListener("DOMContentLoaded", function () {
  const authForm = document.getElementById("auth-form");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const messageDiv = document.getElementById("message");
  const formTitle = document.getElementById("form-title");
  const toggleAuthLink = document.getElementById("toggle-auth");
  const submitButton = document.getElementById("submit-button");

  // Initial state: User is on the login page by default.
  let isRegisterMode = false;

  // Function to update the UI elements based on the current mode
  function updateUIForMode() {
    messageDiv.textContent = ""; // Clear any previous messages

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

  // Set initial UI state when the page loads
  updateUIForMode();

  // Add event listener to toggle between login and register modes
  toggleAuthLink.addEventListener("click", (e) => {
    e.preventDefault(); // Prevent default link behavior
    isRegisterMode = !isRegisterMode; // Toggle the mode
    updateUIForMode(); // Update the UI to reflect the new mode
  });

  // Handle form submission
  if (authForm) {
    authForm.addEventListener("submit", async (e) => {
      e.preventDefault(); // Prevent default form submission

      const username = usernameInput.value.trim();
      const password = passwordInput.value;
      messageDiv.textContent = ""; // Clear any previous messages

      if (!username || !password) {
        messageDiv.textContent = "Please enter both username and password.";
        return;
      }

      let url = "";
      let successMessage = "";
      let failureMessage = "";

      if (isRegisterMode) {
        url = "/register_user"; // Backend endpoint for registration
        successMessage = "Registration successful! Please log in.";
        failureMessage = "Registration failed.";
      } else {
        url = "/login_user"; // Backend endpoint for login
        successMessage = "Login successful!"; // This message will often be bypassed by redirect
        failureMessage = "Login failed. Check your username and password.";
      }

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        });

        const data = await response.json(); // Parse the JSON response from the backend

        if (response.ok) {
          if (isRegisterMode) {
            messageDiv.textContent = successMessage;
            // After successful registration, automatically switch to login mode
            isRegisterMode = false;
            updateUIForMode();
            usernameInput.value = ''; // Clear username
            passwordInput.value = ''; // Clear password
          } else { // Login mode
            if (data.user_id) {
              localStorage.setItem("user_id", data.user_id); // Store user_id
              window.location.href = "/static_frontend/dashboard.html"; // Redirect to dashboard
            } else {
              // This case implies response.ok but no user_id, which shouldn't happen with a proper login endpoint
              messageDiv.textContent = "Login successful, but user ID not received.";
            }
          }
        } else {
          // Display error message from backend or a generic one
          messageDiv.textContent = data.detail || failureMessage;
        }
      } catch (error) {
        console.error("Network or server error:", error);
        messageDiv.textContent = "Could not connect to the server. Please try again.";
      }
    });
  }
});