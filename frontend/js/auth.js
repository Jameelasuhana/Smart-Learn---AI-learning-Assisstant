/* ==========================================================================
   SMART LEARN – Auth & Navigation Manager
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile navbar menu toggle setup
  const mobileBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');

  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
  }

  // Update navbar user profile or logout button
  updateNavState();
});

function updateNavState() {
  const user = getUser();
  const userDisplay = document.getElementById('nav-user-name');
  const logoutBtn = document.getElementById('nav-logout-btn');

  if (userDisplay && user) {
    userDisplay.textContent = user.name;
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      logoutUser();
    });
  }
}

function checkAuthProtection() {
  const token = getToken();
  if (!token) {
    window.location.href = 'login.html';
  }
}

function logoutUser() {
  removeToken();
  showToast('Logged out successfully.', 'info');
  setTimeout(() => {
    window.location.href = 'login.html';
  }, 500);
}
