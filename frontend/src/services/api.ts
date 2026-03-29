import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 创建 axios 实例
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动添加 JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：处理 401 未授权
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// 认证 API
export const authAPI = {
  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
}

// 面板 API
export const dashboardAPI = {
  getOverview: () => api.get('/dashboard/overview'),
  getFinance: (period: 'week' | 'month' = 'month') => api.get('/dashboard/finance', { params: { period } }),
  getHabits: () => api.get('/dashboard/habits'),
  getHabitCalendar: (habitId: number, year: number, month: number) =>
    api.get(`/dashboard/habits/${habitId}/calendar`, { params: { year, month } }),
}

// 聊天 API
export const chatAPI = {
  getHistory: (limit: number = 50) => api.get('/chat/history', { params: { limit } }),
}

// 数据 CRUD API
export const calendarAPI = {
  list: (start?: string, end?: string) => api.get('/data/calendar', { params: { start, end } }),
  create: (data: any) => api.post('/data/calendar', data),
  update: (id: number, data: any) => api.put(`/data/calendar/${id}`, data),
  delete: (id: number) => api.delete(`/data/calendar/${id}`),
}

export const todoAPI = {
  list: (status?: string, priority?: string) => api.get('/data/todos', { params: { status, priority } }),
  create: (data: any) => api.post('/data/todos', data),
  update: (id: number, data: any) => api.put(`/data/todos/${id}`, data),
  delete: (id: number) => api.delete(`/data/todos/${id}`),
}

export const financeAPI = {
  list: (period?: string, type?: string) => api.get('/data/finance', { params: { period, type } }),
  create: (data: any) => api.post('/data/finance', data),
  update: (id: number, data: any) => api.put(`/data/finance/${id}`, data),
  delete: (id: number) => api.delete(`/data/finance/${id}`),
}

export const shoppingAPI = {
  list: (showPurchased?: boolean) => api.get('/data/shopping', { params: { show_purchased: showPurchased } }),
  create: (data: any) => api.post('/data/shopping', data),
  update: (id: number, data: any) => api.put(`/data/shopping/${id}`, data),
  delete: (id: number) => api.delete(`/data/shopping/${id}`),
  clearPurchased: () => api.delete('/data/shopping'),
}

export const notesAPI = {
  list: () => api.get('/data/notes'),
  create: (data: any) => api.post('/data/notes', data),
  update: (id: number, data: any) => api.put(`/data/notes/${id}`, data),
  delete: (id: number) => api.delete(`/data/notes/${id}`),
}

export const readingAPI = {
  list: () => api.get('/data/reading'),
  create: (data: any) => api.post('/data/reading', data),
  update: (id: number, data: any) => api.put(`/data/reading/${id}`, data),
  delete: (id: number) => api.delete(`/data/reading/${id}`),
}

export const healthAPI = {
  list: (d?: string) => api.get('/data/health', { params: { d } }),
  create: (data: any) => api.post('/data/health', data),
  delete: (id: number) => api.delete(`/data/health/${id}`),
}

export const transcribeAPI = {
  transcribe: (audioBlob: Blob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    return api.post('/data/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}
