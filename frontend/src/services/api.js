import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Authentication endpoints
export const authAPI = {
  register: (userData) => api.post('/api/auth/register', userData),
  login: (credentials) => api.post('/api/auth/login', credentials),
  getCurrentUser: () => api.get('/api/auth/me'),
}

// Project endpoints
export const projectAPI = {
  getAll: () => api.get('/api/projects/'),
  getById: (id) => api.get(`/api/projects/${id}/`),
  create: (projectData) => api.post('/api/projects/', projectData),
  delete: (id) => api.delete(`/api/projects/${id}/`),
}

// Site endpoints
export const siteAPI = {
  getAll: () => api.get('/api/sites/'),
  getById: (id) => api.get(`/api/sites/${id}/`),
  create: (siteData) => api.post('/api/sites/', siteData),
  createBulk: (sitesData) => api.post('/api/sites/bulk/', sitesData),
  delete: (id) => api.delete(`/api/sites/${id}/`),
}

export default api
