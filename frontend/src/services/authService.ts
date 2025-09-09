import { api } from './api'
import type { User } from '../types'

export const authService = {
  login: async (credentials: { username: string; password: string }) => {
    return api.post('/auth/login', credentials)
  },

  register: async (userData: { username: string; password: string }) => {
    return api.post('/auth/register', userData)
  },

  getMe: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
  }
}
