import axios from 'axios';

const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (email, username, password) =>
    api.post('/auth/register', { email, username, password }),

  login: (email, password) =>
    api.post('/auth/login', { email, password }),
};

export const userAPI = {
  getCurrentUser: () => api.get('/users/me'),

  getUserById: (userId) => api.get(`/users/${userId}`),

  updateProfile: (username, email) =>
    api.put('/users/me/profile', { username, email }),

  listUsers: () => api.get('/users'),

  deleteUser: (userId) => api.delete(`/users/${userId}`),
};

export const taskAPI = {
  createTask: (title, description, status) =>
    api.post('/tasks', { title, description, status }),

  getTasks: (skip = 0, limit = 10, status = null) => {
    const params = new URLSearchParams();
    params.append('skip', skip);
    params.append('limit', limit);
    if (status) params.append('status_filter', status);
    return api.get(`/tasks?${params}`);
  },

  getTaskById: (taskId) => api.get(`/tasks/${taskId}`),

  updateTask: (taskId, title, description, status, isCompleted) =>
    api.put(`/tasks/${taskId}`, {
      title,
      description,
      status,
      is_completed: isCompleted,
    }),

  deleteTask: (taskId) => api.delete(`/tasks/${taskId}`),
};

export default api;
