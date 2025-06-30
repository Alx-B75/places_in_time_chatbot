document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");

    const apiBaseUrl = "https://places-backend-o8ym.onrender.com";

    async function registerUser(event) {
        event.preventDefault();
        const formData = new FormData(registerForm);
        const username = formData.get("username");
        const password = formData.get("password");

        try {
            const response = await fetch(`${apiBaseUrl}/register`, {
                method: "POST",
                body: new URLSearchParams({ username, password }),
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                redirect: "follow"
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
                alert(data.detail || "Registration failed.");
            }
        } catch (error) {
            console.error("Registration error:", error);
            alert("Could not connect to the server. Please try again.");
        }
    }

    async function loginUser(event) {
        event.preventDefault();
        const formData = new FormData(loginForm);
        const username = formData.get("username");
        const password = formData.get("password");

        try {
            const response = await fetch(`${apiBaseUrl}/login`, {
                method: "POST",
                body: new URLSearchParams({ username, password }),
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                redirect: "follow"
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
                alert(data.detail || "Login failed.");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("Could not connect to the server. Please try again.");
        }
    }

    if (registerForm) {
        registerForm.addEventListener("submit", registerUser);
    }

    if (loginForm) {
        loginForm.addEventListener("submit", loginUser);
    }
});
