document.addEventListener("DOMContentLoaded", () => {
    const authForm = document.getElementById("auth-form");
    const toggleLink = document.getElementById("toggle-auth");
    const formTitle = document.getElementById("form-title");
    let isLogin = true;

    authForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const url = isLogin ? "/login" : "/register_user";
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const contentType = response.headers.get("content-type") || "";
            const data = contentType.includes("application/json")
                ? await response.json()
                : { message: await response.text() };

            if (!response.ok) {
                throw new Error(data.message || "Something went wrong.");
            }

            localStorage.setItem("user_id", data.user_id);
            window.location.href = "dashboard.html";
        } catch (error) {
            document.getElementById("message").textContent = error.message;
        }
    });

    toggleLink.addEventListener("click", (e) => {
        e.preventDefault();
        isLogin = !isLogin;
        formTitle.textContent = isLogin ? "Login" : "Register";
        toggleLink.textContent = isLogin
            ? "Don't have an account? Register"
            : "Already have an account? Login";
    });
});
