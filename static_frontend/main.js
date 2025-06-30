const BASE_URL = 'https://places-backend-o8ym.onrender.com';

const form = document.getElementById('auth-form');
const toggleLink = document.getElementById('toggle-auth');
const formTitle = document.getElementById('form-title');
const submitButton = document.getElementById('submit-button');
const messageDiv = document.getElementById('message');

let isLogin = true;

toggleLink.addEventListener('click', (e) => {
  e.preventDefault();
  isLogin = !isLogin;
  formTitle.textContent = isLogin ? 'Login' : 'Register';
  submitButton.textContent = isLogin ? 'Login' : 'Register';
  toggleLink.textContent = isLogin
    ? "Don't have an account? Register"
    : 'Already have an account? Login';
  messageDiv.textContent = '';
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = form.username.value;
  const password = form.password.value;

  const endpoint = isLogin ? '/login' : '/register';

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Accept': 'text/html',
      },
      body: new URLSearchParams({
        username,
        password,
      }),
      redirect: 'follow',
    });

    if (response.redirected) {
      window.location.href = response.url;
    } else if (response.status >= 400) {
      const text = await response.text();
      messageDiv.textContent = `Login failed. Server said: ${text}`;
    } else {
      messageDiv.textContent = 'Unexpected response. Please try again.';
    }
  } catch (error) {
    console.error(error);
    messageDiv.textContent = 'Could not connect to the server. Please try again.';
  }
});
