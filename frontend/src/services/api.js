import axios from 'axios';

// Use environment variable for API base URL - NO fallback to localhost in production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  console.error('VITE_API_BASE_URL environment variable is not set!');
  throw new Error('VITE_API_BASE_URL environment variable is required. Please set it in your .env file or Vercel environment variables.');
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include credentials for CORS
});

// Request interceptor for adding auth tokens
api.interceptors.request.use(
  (config) => {
    // Use 'token' which is what AuthContext stores
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      console.error('API Error:', message);
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', error.request);
      return Promise.reject(new Error('Network error. Please check your connection.'));
    } else {
      // Something else happened
      console.error('Error:', error.message);
      return Promise.reject(error);
    }
  }
);

// Auth API endpoints
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/api/register', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/api/login', credentials);
    return response.data;
  },
};

// User API endpoints
export const userAPI = {
  getUsers: async () => {
    const response = await api.get('/api/users');
    return response.data;
  },
};

// Site API endpoints
export const siteAPI = {
  getAll: async () => {
    const response = await api.get('/api/sites');
    return response;
  },
  getById: async (id) => {
    const response = await api.get(`/api/sites/${id}`);
    return response;
  },
  create: async (siteData) => {
    const response = await api.post('/api/sites', siteData);
    return response;
  },
  update: async (id, siteData) => {
    const response = await api.put(`/api/sites/${id}`, siteData);
    return response;
  },
  delete: async (id) => {
    const response = await api.delete(`/api/sites/${id}`);
    return response;
  },
};

// Project API endpoints
export const projectAPI = {
  getAll: async () => {
    const response = await api.get('/api/projects');
    return response;
  },
  getById: async (id) => {
    const response = await api.get(`/api/projects/${id}`);
    return response;
  },
  create: async (projectData) => {
    const response = await api.post('/api/projects', projectData);
    return response;
  },
  update: async (id, projectData) => {
    const response = await api.put(`/api/projects/${id}`, projectData);
    return response;
  },
  delete: async (id) => {
    const response = await api.delete(`/api/projects/${id}`);
    return response;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
