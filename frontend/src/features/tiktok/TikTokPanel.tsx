import { useEffect, useState } from 'react'
import { api } from '../../services/api'
import { Button, Badge, Card, CardHeader, CardTitle, CardContent, useToast } from '../../components/ui'

type TikTokUser = {
  id: string
  username: string
  room_id?: string | null
  monitoring_status: string
  live_status: string
  last_check?: string | null
  error_message?: string | null
  last_recording?: string | null
  recording_start_time?: string | null
}

type Status = {
  active: boolean
  users: TikTokUser[]
}

export default function TikTokPanel() {
  const [status, setStatus] = useState<Status | null>(null)
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const { addToast } = useToast()

  const load = async () => {
    try {
      const { data } = await api.get<Status>('/tiktok_live/status')
      setStatus(data)
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 5000)
    return () => clearInterval(id)
  }, [])

  const start = async () => {
    setLoading(true)
    try {
      await api.post('/tiktok_live/start')
      await load()
      addToast({ title: 'Đã bắt đầu', description: 'Dịch vụ theo dõi đang chạy', variant: 'success' })
    } catch (e: any) {
      addToast({ title: 'Không thể bắt đầu', description: e?.response?.data?.detail || 'Đã xảy ra lỗi', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }
  const stop = async () => {
    setLoading(true)
    try {
      await api.post('/tiktok_live/stop')
      await load()
      addToast({ title: 'Đã dừng', description: 'Dịch vụ theo dõi đã tạm dừng', variant: 'info' })
    } catch (e: any) {
      addToast({ title: 'Không thể dừng', description: e?.response?.data?.detail || 'Đã xảy ra lỗi', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }
  const addUser = async () => {
    const u = username.trim()
    if (!u) return
    setLoading(true)
    try {
      await api.post('/tiktok_live/users', { username: u })
      setUsername('')
      await load()
      addToast({ title: 'Đã thêm người dùng', description: `@${u} đã được thêm`, variant: 'success' })
    } catch (e: any) {
      addToast({ title: 'Không thể thêm', description: e?.response?.data?.detail || 'Đã xảy ra lỗi', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }
  const removeUser = async (id: string) => {
    setLoading(true)
    try {
      await api.delete(`/tiktok_live/users/${id}`)
      await load()
      addToast({ title: 'Đã xóa người dùng', variant: 'success' })
    } catch (e: any) {
      addToast({ title: 'Không thể xóa', description: e?.response?.data?.detail || 'Đã xảy ra lỗi', variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-4 sm:p-6">
      <CardHeader className="mb-4">
        <CardTitle>Theo dõi TikTok Live</CardTitle>
        <div className="space-x-2">
          <Button variant="secondary" size="sm" onClick={load}>Làm mới</Button>
          <Button variant="primary" size="sm" onClick={start} disabled={loading}>Bắt đầu</Button>
          <Button variant="danger" size="sm" onClick={stop} disabled={loading}>Dừng</Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4 text-sm flex items-center gap-2">
          <span>Trạng thái:</span>
          <Badge variant={status?.active ? 'green' : 'neutral'}>{status?.active ? 'Đang chạy' : 'Tạm dừng'}</Badge>
        </div>
        <div className="flex gap-2 mb-4">
          <input
            className="flex-1 px-3 py-2 rounded-lg bg-neutral-800 border border-neutral-700 text-sm"
            placeholder="Thêm username (không có @)"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <Button size="md" onClick={addUser} disabled={loading}>Thêm</Button>
        </div>
        <div className="space-y-2 text-sm max-h-80 overflow-auto">
          {status?.users?.length ? (
            status.users.map(u => (
              <div key={u.id} className="flex items-center justify-between p-3 rounded-lg bg-neutral-800 border border-neutral-700">
                <div>
                  <div className="font-medium">@{u.username}</div>
                  <div className="mt-1 flex flex-wrap items-center gap-2">
                    <Badge variant="blue">{u.live_status}</Badge>
                    <Badge variant="purple">{u.monitoring_status}</Badge>
                    {u.last_check && (
                      <Badge variant="neutral">Lần kiểm tra: {u.last_check}</Badge>
                    )}
                  </div>
                  {u.error_message && <div className="text-red-400 mt-1">{u.error_message}</div>}
                </div>
                <Button variant="danger" size="sm" onClick={() => removeUser(u.id)}>Xóa</Button>
              </div>
            ))
          ) : (
            <div className="text-neutral-400">Chưa có người dùng nào được theo dõi</div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
