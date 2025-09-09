import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { authService } from '../../services/authService'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      setIsAuthenticated(false)
      setLoading(false)
      return
    }

    authService.getMe()
      .then(() => {
        setIsAuthenticated(true)
        setLoading(false)
      })
      .catch(() => {
        authService.logout()
        setIsAuthenticated(false)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Đang xác thực...</p>
        </div>
      </div>
    )
  }

  if (isAuthenticated === false) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
