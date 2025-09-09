import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Badge } from '../ui'

interface SidebarItem {
  id: string
  label: string
  icon: string
  path: string
}

interface SidebarProps {
  user?: {
    username: string
    role: string
  } | null
  onLogout: () => void
}

const getSidebarItems = (userRole?: string): SidebarItem[] => {
  const baseItems: SidebarItem[] = [
    {
      id: 'dashboard',
      label: 'Trang chủ',
      icon: '🏠',
      path: '/'
    },
    {
      id: 'tiktok',
      label: 'TikTok Live',
      icon: '🎥',
      path: '/tiktok'
    },
    {
      id: 'videos',
      label: 'Video',
      icon: '📹',
      path: '/videos'
    },
    {
      id: 'settings',
      label: 'Cài đặt',
      icon: '⚙️',
      path: '/settings'
    }
  ]

  // Add admin-only items
  if (userRole === 'admin') {
    baseItems.splice(4, 0, {
      id: 'users',
      label: 'Quản lý người dùng',
      icon: '👥',
      path: '/users'
    })
  }

  return baseItems
}

export default function Sidebar({ user, onLogout }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const location = useLocation()
  const sidebarItems = getSidebarItems(user?.role)

  return (
    <aside
      className={`fixed left-0 top-0 h-full bg-neutral-900 border-r border-neutral-800 transition-all duration-300 z-30 ${
        isExpanded ? 'w-64' : 'w-16'
      }`}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      {/* Logo/Brand */}
      <div className="h-16 flex items-center justify-center border-b border-neutral-800">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-sm">
            {isExpanded ? 'TR' : 'T'}
          </span>
        </div>
        <div className={`ml-3 overflow-hidden transition-all duration-300 ${
          isExpanded ? 'max-w-xs opacity-100' : 'max-w-0 opacity-0'
        }`}>
          <span className="font-semibold text-white whitespace-nowrap">
            TikTok Re-Upload
          </span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="mt-8 px-2 pb-32">
        <ul className="space-y-2">
          {sidebarItems.map((item) => {
            const isActive = location.pathname === item.path

            return (
              <li key={item.id}>
                <Link
                  to={item.path}
                  className={`flex items-center px-3 py-3 rounded-lg transition-colors duration-200 group ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-neutral-300 hover:bg-neutral-800 hover:text-white'
                  }`}
                >
                  <span className="text-xl flex-shrink-0">{item.icon}</span>
                  <div className={`ml-3 overflow-hidden transition-all duration-300 ${
                    isExpanded ? 'max-w-xs opacity-100' : 'max-w-0 opacity-0'
                  }`}>
                    <span className="font-medium whitespace-nowrap">
                      {item.label}
                    </span>
                  </div>

                  {/* Tooltip for collapsed state */}
                  {!isExpanded && (
                    <div className="absolute left-full ml-2 px-3 py-2 bg-neutral-800 text-white text-sm rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                      {item.label}
                      <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-neutral-800 rotate-45"></div>
                    </div>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Bottom section */}
      <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-neutral-800 space-y-2">
        {/* User info */}
        <div className="flex items-center justify-center">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-neutral-700 flex items-center justify-center flex-shrink-0">
              <span className="text-sm">👤</span>
            </div>
            <div className={`ml-3 overflow-hidden transition-all duration-300 ${
              isExpanded ? 'max-w-xs opacity-100' : 'max-w-0 opacity-0'
            }`}>
              {user && (
                <div className="whitespace-nowrap">
                  <p className="text-sm font-medium text-white">@{user.username}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="blue" className="text-xs">{user.role}</Badge>
                    <span className="text-xs text-green-400">● Online</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Logout button */}
        <button
          onClick={onLogout}
          className="w-full flex items-center px-3 py-2 text-red-400 hover:bg-red-600 hover:text-white rounded-lg transition-colors duration-200 group justify-center"
        >
          <span className="text-lg flex-shrink-0">🚪</span>
          <div className={`ml-3 overflow-hidden transition-all duration-300 ${
            isExpanded ? 'max-w-xs opacity-100' : 'max-w-0 opacity-0'
          }`}>
            <span className="text-sm font-medium whitespace-nowrap">Đăng xuất</span>
          </div>

          {/* Tooltip for collapsed state */}
          {!isExpanded && (
            <div className="absolute left-full ml-2 px-3 py-2 bg-neutral-800 text-white text-sm rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
              Đăng xuất
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-neutral-800 rotate-45"></div>
            </div>
          )}
        </button>
      </div>
    </aside>
  )
}
