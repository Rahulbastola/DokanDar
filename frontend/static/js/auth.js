function redirectForRole(role) {
  if (role === 'admin') window.location.href = 'vendor.html';
  else if (role === 'super_admin') window.location.href = 'admin-dashboard.html';
  else window.location.href = 'products.html';
}

const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    try {
      const data = await apiFetch('/auth/login/', {
        method: 'POST',
        body: { username: formData.get('username'), password: formData.get('password') },
      });
      Auth.setSession(data.access, data.refresh, data.user);
      redirectForRole(data.user.role);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}

const registerForm = document.getElementById('register-form');
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const payload = Object.fromEntries(formData.entries());
    try {
      const data = await apiFetch('/auth/register/', { method: 'POST', body: payload });
      showToast(data.detail, 'success');
      setTimeout(() => { window.location.href = 'login.html'; }, 1500);
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}
