import { useEffect, useState } from 'react'
import { userService } from '../../services/userService'
import { Button, Badge, Card, useToast } from '../../components/ui'

type User = {
  id: number
  username: string
  role: string
  status: string
}

export default function UserManagementPage() {
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [pendingUsers, setPendingUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { addToast } = useToast()

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [all, pending] = await Promise.all([
        userService.getAllUsers(),
        userService.getPendingUsers(),
      ])
      setAllUsers(all)
      setPendingUsers(pending)
    } catch (e: any) {
      const msg = e?.response?.data?.detail || 'Failed to load users'
      setError(msg)
      addToast({ title: 'Không tải được danh sách', description: msg, variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const approve = async (userId: number) => {
    try {
      await userService.approveUser(userId)
      await load()
      addToast({ title: 'Đã phê duyệt', variant: 'success' })
    } catch (e: any) {
      addToast({ title: 'Phê duyệt thất bại', description: e?.response?.data?.detail || 'Approve failed', variant: 'error' })
    }
  }

  const removeUser = async (userId: number) => {
    if (!confirm('Xóa người dùng này?')) return
    try {
      await userService.deleteUser(userId)
      await load()
      addToast({ title: 'Đã xóa người dùng', variant: 'success' })
    } catch (e: any) {
      addToast({ title: 'Xóa thất bại', description: e?.response?.data?.detail || 'Delete failed', variant: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Quản lý người dùng</h1>
        <Button variant="secondary" size="lg" onClick={load} disabled={loading}>
          {loading ? 'Đang tải...' : 'Làm mới'}
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-blue-600 flex items-center justify-center">
              <span className="text-xl">👥</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Tổng người dùng</h3>
            <p className="text-2xl font-bold text-blue-400">{allUsers.length}</p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-yellow-600 flex items-center justify-center">
              <span className="text-xl">⏳</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Chờ phê duyệt</h3>
            <p className="text-2xl font-bold text-yellow-400">{pendingUsers.length}</p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-green-600 flex items-center justify-center">
              <span className="text-xl">✅</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Đã phê duyệt</h3>
            <p className="text-2xl font-bold text-green-400">
              {allUsers.filter(u => u.status === 'approved').length}
            </p>
          </div>
        </Card>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-900/50 border border-red-700 text-red-300">
          <h3 className="font-semibold mb-2">Lỗi tải dữ liệu</h3>
          <p>{error}</p>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Pending Users */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Chờ phê duyệt</h2>
            <Badge variant="yellow">{pendingUsers.length}</Badge>
          </div>
          <div className="space-y-3">
            {pendingUsers.length === 0 ? (
              <div className="text-center py-8 text-neutral-400">
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
                <p>Không có người dùng chờ phê duyệt</p>
              </div>
            ) : (
              pendingUsers.map((u) => (
                <div key={u.id} className="flex items-center justify-between p-4 rounded-lg bg-neutral-800 border border-neutral-700">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-yellow-600 flex items-center justify-center">
                      <span className="text-white font-semibold">{u.username.charAt(0).toUpperCase()}</span>
                    </div>
                    <div>
                      <div className="font-medium text-white">@{u.username}</div>
                      <div className="text-sm text-neutral-400">Chờ phê duyệt</div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="primary" size="sm" onClick={() => approve(u.id)}>
                      Phê duyệt
                    </Button>
                    <Button variant="danger" size="sm" onClick={() => removeUser(u.id)}>
                      Xóa
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* All Users */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Tất cả người dùng</h2>
            <Badge variant="blue">{allUsers.length}</Badge>
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {allUsers.length === 0 ? (
              <div className="text-center py-8 text-neutral-400">
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
                <p>Chưa có người dùng</p>
              </div>
            ) : (
              allUsers.map((u) => (
                <div key={u.id} className="flex items-center justify-between p-4 rounded-lg bg-neutral-800 border border-neutral-700">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      u.role === 'admin' ? 'bg-purple-600' : u.status === 'approved' ? 'bg-green-600' : 'bg-gray-600'
                    }`}>
                      <span className="text-white font-semibold">{u.username.charAt(0).toUpperCase()}</span>
                    </div>
                    <div>
                      <div className="font-medium text-white">@{u.username}</div>
                      <div className="flex items-center space-x-2 text-sm">
                        <Badge variant={u.role === 'admin' ? 'purple' : 'blue'}>
                          {u.role === 'admin' ? 'Admin' : 'User'}
                        </Badge>
                        <Badge variant={u.status === 'approved' ? 'green' : 'yellow'}>
                          {u.status === 'approved' ? 'Đã duyệt' : 'Chờ duyệt'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <Button variant="danger" size="sm" onClick={() => removeUser(u.id)}>
                    Xóa
                  </Button>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
