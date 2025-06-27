document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");

    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }

    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }
});

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;

    try {
        const response = await fetch("/register_user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const contentType = response.headers.get("content-type") || "";
        let data;

        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {
            data = { message: await response.text() };
        }

        if (!response.ok) {
            throw new Error(data.message || "Registration failed.");
        }

        localStorage.setItem("user_id", data.user_id);
        window.location.href = "dashboard.html";
    } catch (error) {
        document.getElementById("message").textContent = error.message;
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const contentType = response.headers.get("content-type") || "";
        let data;

        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {
            data = { message: await response.text() };
        }

        if (!response.ok) {
            throw new Error(data.message || "Login failed.");
        }

        localStorage.setItem("user_id", data.user_id);
        window.location.href = "dashboard.html";
    } catch (error) {
        document.getElementById("message").textContent = error.message;
    }
}
