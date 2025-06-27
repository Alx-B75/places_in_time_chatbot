document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("auth-form");
    const message = document.getElementById("message");
    const toggleBtn = document.getElementById("toggle-auth");
    const formTitle = document.getElementById("form-title");

    let mode = "login";

    function toggleMode() {
        mode = mode === "login" ? "register" : "login";
        formTitle.textContent = mode === "login" ? "Login" : "Register";
        toggleBtn.textContent = mode === "login"
            ? "Don't have an account? Register"
            : "Already have an account? Login";
        message.textContent = "";
    }

    toggleBtn.addEventListener("click", (e) => {
        e.preventDefault();
        toggleMode();
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        if (!username || !password) {
            message.textContent = "Please enter a username and password.";
            return;
        }

        const endpoint = mode === "login" ? "/login" : "/register_user";
        const payload = { username, password };

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (response.redirected) {
                // Login success - assume redirect to threads
                const userId = response.url.split("/").pop();
                localStorage.setItem("user_id", userId);
                window.location.href = "/static_frontend/dashboard.html";
            } else {
                const result = await response.json();
                message.textContent = result.detail || "Unexpected error.";
            }
        } catch (error) {
            message.textContent = "Error: " + error.message;
        }
    });
});
