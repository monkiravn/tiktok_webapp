import { useState, useEffect } from 'react'
import { authService } from '../services/authService'
import type { User } from '../types'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }

    authService.getMe()
      .then(setUser)
      .catch((err) => {
        setError(err.message)
        localStorage.removeItem('access_token')
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (credentials: { username: string; password: string }) => {
    try {
      setLoading(true)
      const response = await authService.login(credentials)
      localStorage.setItem('access_token', response.data.access_token)
      const userData = await authService.getMe()
      setUser(userData)
      return { success: true }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
      return { success: false, error: err.response?.data?.detail || 'Login failed' }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    authService.logout()
    setUser(null)
  }

  return {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin'
  }
}
