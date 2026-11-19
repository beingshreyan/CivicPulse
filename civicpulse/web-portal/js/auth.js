document.addEventListener('DOMContentLoaded', () => {
  renderNavbarAuth();
  initAuthForms();
});

function renderNavbarAuth() {
  const navArea = document.getElementById('nav-auth-area');
  if (!navArea) return;

  const user = ApiClient.getUser();
  if (user) {
    navArea.innerHTML = `
      <span class="user-pill">${escapeHtml(user.name || user.email)}</span>
      <a href="report.html" class="btn btn-accent btn-sm">+ Report an Issue</a>
      <button id="logout-btn" class="btn btn-outline btn-sm" style="background: transparent; color: #fff; border-color: rgba(255,255,255,0.35);">
        Logout
      </button>
    `;
    document.getElementById('logout-btn').addEventListener('click', () => {
      ApiClient.clearSession();
      window.location.href = 'index.html';
    });
  }
}

function initAuthForms() {
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const alertBox = document.getElementById('auth-alert');

  if (!loginForm || !registerForm) return;

  const showAlert = (msg, type = 'error') => {
    alertBox.textContent = msg;
    alertBox.className = `alert-box alert-${type}`;
    alertBox.style.display = 'block';
  };

  tabLogin.addEventListener('click', () => {
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
    alertBox.style.display = 'none';
  });

  tabRegister.addEventListener('click', () => {
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    registerForm.style.display = 'block';
    loginForm.style.display = 'none';
    alertBox.style.display = 'none';
  });

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    try {
      const res = await ApiClient.login(email, password);
      ApiClient.setSession(res.access_token, res.user || { email });
      window.location.href = 'index.html';
    } catch (err) {
      showAlert(err.message || 'Invalid credentials.');
    }
  });

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;

    try {
      await ApiClient.register(name, email, password);
      showAlert('Account created! You can now sign in.', 'success');
      tabLogin.click();
    } catch (err) {
      showAlert(err.message || 'Registration failed.');
    }
  });
}

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}