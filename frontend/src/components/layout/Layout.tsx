import { Outlet, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { authService } from '../../services/authService'
import Sidebar from './Sidebar'

type User = { username: string; role: string }

export default function Layout() {
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    authService.getMe()
      .then((data) => setUser({ username: data.username, role: data.role }))
      .catch(() => setUser(null))
  }, [])

  const onLogout = () => {
    authService.logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <Sidebar user={user} onLogout={onLogout} />

      {/* Main content area with sidebar offset */}
      <div className="ml-16">
        <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
