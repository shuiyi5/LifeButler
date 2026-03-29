import api from './api'

export const authService = {
  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),

  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password })
    const { token, user } = res.data
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    return { token, user }
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },
}
