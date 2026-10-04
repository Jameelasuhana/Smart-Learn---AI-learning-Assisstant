/* ==========================================================================
   SMART LEARN – API Client Helper Module
   ========================================================================== */

const API_BASE_URL = window.API_BASE_URL || 'https://smart-learn-ai-learning-assisstant.onrender.com';

function getToken() {
  return localStorage.getItem('smart_learn_token');
}

function setToken(token) {
  localStorage.setItem('smart_learn_token', token);
}

function removeToken() {
  localStorage.removeItem('smart_learn_token');
  localStorage.removeItem('smart_learn_user');
}

function getUser() {
  const userStr = localStorage.getItem('smart_learn_user');
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    return null;
  }
}

function setUser(user) {
  localStorage.setItem('smart_learn_user', JSON.stringify(user));
}

function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'fa-info-circle';
  if (type === 'success') icon = 'fa-check-circle';
  if (type === 'danger' || type === 'error') icon = 'fa-exclamation-circle';
  
  toast.innerHTML = `<i class="fas ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}

async function apiRequest(endpoint, method = 'GET', data = null, requiresAuth = true) {
  const headers = {
    'Content-Type': 'application/json'
  };

  if (requiresAuth) {
    const token = getToken();
    if (!token) {
      removeToken();
      window.location.href = 'login.html';
      throw new Error('Authentication required. Please log in.');
    }
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    if (response.status === 401 && requiresAuth) {
      removeToken();
      showToast('Session expired. Please log in again.', 'danger');
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 1000);
      throw new Error('Session expired.');
    }

    const resData = await response.json();

    if (!response.ok) {
      const errMsg = resData.detail || resData.message || 'An error occurred during request.';
      throw new Error(errMsg);
    }

    return resData;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}
