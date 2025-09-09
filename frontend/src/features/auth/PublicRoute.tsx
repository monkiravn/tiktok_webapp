import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { api } from '../../services/api'

interface PublicRouteProps {
  children: React.ReactNode
}

export default function PublicRoute({ children }: PublicRouteProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      setIsAuthenticated(false)
      setLoading(false)
      return
    }

    api
      .get('/auth/me')
      .then(() => {
        setIsAuthenticated(true)
        setLoading(false)
      })
      .catch(() => {
        localStorage.removeItem('access_token')
        setIsAuthenticated(false)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Đang kiểm tra...</p>
        </div>
      </div>
    )
  }

  if (isAuthenticated === true) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
