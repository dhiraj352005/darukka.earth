import axios from 'axios'

// Backend URL from environment variable
const API_URL = import.meta.env.VITE_API_URL

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
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getCurrentUser: () => api.get('/auth/me'),
}

// Project endpoints
export const projectAPI = {
  getAll: () => api.get('/projects/'),
  getById: (id) => api.get(`/projects/${id}/`),
  create: (projectData) => api.post('/projects/', projectData),
  delete: (id) => api.delete(`/projects/${id}/`),
}

// Site endpoints
export const siteAPI = {
  getAll: () => api.get('/sites/'),
  getById: (id) => api.get(`/sites/${id}/`),
  create: (siteData) => api.post('/sites/', siteData),
  createBulk: (sitesData) => api.post('/sites/bulk/', sitesData),
  delete: (id) => api.delete(`/sites/${id}/`),
}

export default api
