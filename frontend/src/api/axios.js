import axios from 'axios';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api' // APIのベースURLを設定
});

apiClient.defaults.withCredentials = true;

apiClient.interceptors.request.use(config => {
  if (['POST', 'GET', 'PUT', 'PATCH', 'DELETE'].includes(config.method.toUpperCase())) {
    const token = getCookie('csrftoken');
    if (token) {
      config.headers['X-CSRFToken'] = token;
    }
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default apiClient;