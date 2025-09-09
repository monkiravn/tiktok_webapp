import { api } from './api'
import type { User } from '../types'

export const userService = {
  getAllUsers: async (): Promise<User[]> => {
    const response = await api.get('/users/')
    return response.data
  },

  getPendingUsers: async (): Promise<User[]> => {
    const response = await api.get('/users/pending')
    return response.data
  },

  approveUser: async (userId: number) => {
    return api.put(`/users/${userId}/approve`)
  },

  deleteUser: async (userId: number) => {
    return api.delete(`/users/${userId}`)
  }
}
