/**
 * CertiNexus AI — API Client
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE
  }

  getToken() {
    return localStorage.getItem('certinexus_token')
  }

  setToken(token) {
    localStorage.setItem('certinexus_token', token)
  }

  setRefreshToken(token) {
    localStorage.setItem('certinexus_refresh_token', token)
  }

  clearTokens() {
    localStorage.removeItem('certinexus_token')
    localStorage.removeItem('certinexus_refresh_token')
  }

  async request(path, options = {}) {
    const url = `${this.baseUrl}${path}`
    const headers = { ...options.headers }

    const token = this.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }

    const response = await fetch(url, { ...options, headers })

    if (response.status === 401) {
      this.clearTokens()
      window.location.href = '/login'
      throw new Error('Unauthorized')
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || 'Request failed')
    }

    return response.json()
  }

  // Auth
  async register(data) {
    const result = await this.request('/auth/register', {
      method: 'POST', body: JSON.stringify(data)
    })
    this.setToken(result.access_token)
    this.setRefreshToken(result.refresh_token)
    return result
  }

  async login(data) {
    const result = await this.request('/auth/login', {
      method: 'POST', body: JSON.stringify(data)
    })
    this.setToken(result.access_token)
    this.setRefreshToken(result.refresh_token)
    return result
  }

  logout() { this.clearTokens() }

  // Users
  getMe() { return this.request('/users/me') }
  updateMe(data) {
    return this.request('/users/me', { method: 'PATCH', body: JSON.stringify(data) })
  }

  // Certificates
  async uploadCertificate(file) {
    const formData = new FormData()
    formData.append('file', file)
    return this.request('/certificates/upload', { method: 'POST', body: formData })
  }
  getCertificates() { return this.request('/certificates') }
  getCertificate(id) { return this.request(`/certificates/${id}`) }
  updateCertificate(id, data) {
    return this.request(`/certificates/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
  }
  deleteCertificate(id) {
    return this.request(`/certificates/${id}`, { method: 'DELETE' })
  }
  getProcessingStatus(id) { return this.request(`/certificates/${id}/processing-status`) }

  // Analytics
  getAnalytics() { return this.request('/analytics') }

  // Portfolio
  getPortfolio() { return this.request('/portfolio') }
  updatePortfolio(data) {
    return this.request('/portfolio', { method: 'PATCH', body: JSON.stringify(data) })
  }
  getPublicPortfolio(username) { return this.request(`/portfolio/public/${username}`) }

  // Search
  searchCertificates(query, category) {
    const params = new URLSearchParams()
    if (query) params.set('q', query)
    if (category) params.set('category', category)
    return this.request(`/search?${params}`)
  }

  // Resume
  getResumeData() { return this.request('/resume/data') }
  generateResume(data) {
    return this.request('/resume/generate', { method: 'POST', body: JSON.stringify(data) })
  }

  // Admin / ML Research
  getDatasetStats() { return this.request('/admin/dataset-statistics') }
  getModelPerformance() { return this.request('/admin/model-performance') }
  getExperiments() { return this.request('/admin/experiments') }
  getModelComparison() { return this.request('/admin/model-comparison') }
  getConfusionMatrix() { return this.request('/admin/confusion-matrix') }
  getErrorAnalysis() { return this.request('/admin/error-analysis') }
}

export const api = new ApiClient()
export default api
