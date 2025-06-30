document.addEventListener("DOMContentLoaded", () => {
    const backendUrl = "https://places-backend-o8ym.onrender.com";

    const authForm = document.getElementById("auth-form");
    const toggleAuth = document.getElementById("toggle-auth");
    const formTitle = document.getElementById("form-title");
    const submitButton = document.getElementById("submit-button");
    const messageDiv = document.getElementById("message");

    let isLogin = true;

    authForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        messageDiv.textContent = "";

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const endpoint = isLogin ? "/login" : "/register";
        const url = `${backendUrl}${endpoint}`;

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const text = await response.text();
                messageDiv.textContent = isLogin
                    ? "Login failed. Please check your credentials."
                    : "Registration failed. Try another username.";
                return;
            }

            if (isLogin) {
                const result = await response.json();
                window.location.href = "dashboard.html";
            } else {
                messageDiv.textContent = "Registration successful! Please log in.";
                // Switch to login mode
                isLogin = true;
                formTitle.textContent = "Login";
                submitButton.textContent = "Login";
                toggleAuth.textContent = "Don't have an account? Register";
            }
        } catch (error) {
            console.error("Error:", error);
            messageDiv.textContent = "Could not connect to the server. Please try again.";
        }
    });

    toggleAuth.addEventListener("click", (e) => {
        e.preventDefault();
        isLogin = !isLogin;
        formTitle.textContent = isLogin ? "Login" : "Register";
        submitButton.textContent = isLogin ? "Login" : "Register";
        toggleAuth.textContent = isLogin
            ? "Don't have an account? Register"
            : "Already have an account? Login";
        messageDiv.textContent = "";
    });
});
