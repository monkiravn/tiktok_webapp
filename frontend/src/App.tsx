import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage, RegisterPage, ProtectedRoute, PublicRoute, AdminRoute } from './features/auth'
import { Dashboard } from './features/dashboard'
import { TikTokPage } from './features/tiktok'
import { VideosPage } from './features/videos'
import { SettingsPage } from './features/settings'
import { UserManagementPage } from './features/users'
import Layout from './components/layout/Layout'

function App() {
  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />

        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Dashboard />} />
          <Route path="/tiktok" element={<TikTokPage />} />
          <Route path="/videos" element={<VideosPage />} />
          <Route path="/users" element={
            <AdminRoute>
              <UserManagementPage />
            </AdminRoute>
          } />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  )
}

export default App
