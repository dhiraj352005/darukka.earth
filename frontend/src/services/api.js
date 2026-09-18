import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Check if we're in production (Vercel) or local
const isProduction = !API_URL.includes('localhost')
const apiPrefix = isProduction ? '/api' : ''

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
  register: (userData) => api.post(`${apiPrefix}/auth/register`, userData),
  login: (credentials) => api.post(`${apiPrefix}/auth/login`, credentials),
  getCurrentUser: () => api.get(`${apiPrefix}/auth/me`),
}

// Project endpoints
export const projectAPI = {
  getAll: () => api.get(`${apiPrefix}/projects/`),
  getById: (id) => api.get(`${apiPrefix}/projects/${id}/`),
  create: (projectData) => api.post(`${apiPrefix}/projects/`, projectData),
  delete: (id) => api.delete(`${apiPrefix}/projects/${id}/`),
}

// Site endpoints
export const siteAPI = {
  getAll: () => api.get(`${apiPrefix}/sites/`),
  getById: (id) => api.get(`${apiPrefix}/sites/${id}/`),
  create: (siteData) => api.post(`${apiPrefix}/sites/`, siteData),
  createBulk: (sitesData) => api.post(`${apiPrefix}/sites/bulk/`, sitesData),
  delete: (id) => api.delete(`${apiPrefix}/sites/${id}/`),
}

export default api
