document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("form-login");
  const registerForm = document.getElementById("form-register");
  const toggleLogin = document.getElementById("btn-toggle-login");
  const toggleRegister = document.getElementById("btn-toggle-register");

  toggleLogin.addEventListener("click", () => {
    loginForm.style.display = "block";
    registerForm.style.display = "none";
  });

  toggleRegister.addEventListener("click", () => {
    loginForm.style.display = "none";
    registerForm.style.display = "block";
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("/login_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const result = await response.json();
      localStorage.setItem("user_id", result.user_id);
      window.location.href = "dashboard.html";
    } else {
      alert("Login failed. Please try again.");
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;

    const response = await fetch("/register_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const result = await response.json();
      localStorage.setItem("user_id", result.user_id);
      window.location.href = "dashboard.html";
    } else {
      alert("Registration failed. Username may already exist.");
    }
  });
});
