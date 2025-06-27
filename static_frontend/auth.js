let mode = 'login'; // or 'register'

const form = document.getElementById('auth-form');
const toggle = document.getElementById('toggle-mode');
const title = document.getElementById('form-title');
const button = document.getElementById('submit-button');

toggle.addEventListener('click', () => {
  if (mode === 'login') {
    mode = 'register';
    title.textContent = 'Register';
    button.textContent = 'Register';
    toggle.textContent = 'Already have an account? Login';
  } else {
    mode = 'login';
    title.textContent = 'Login';
    button.textContent = 'Login';
    toggle.textContent = "Don't have an account? Register";
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const name = document.getElementById('name').value;
  const password = document.getElementById('password').value;

  const endpoint = mode === 'login' ? '/login_user' : '/register_user';

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, password }),
    redirect: 'follow'
  });

  if (response.redirected) {
    window.location.href = response.url;
  } else {
    alert('Authentication failed. Please check your credentials.');
  }
});
