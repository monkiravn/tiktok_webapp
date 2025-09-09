import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../services/api'
import { authService } from '../../services/authService'
import { videoService } from '../../services/videoService'
import { TikTokPanel } from '../tiktok'
import { Card, Badge } from '../../components/ui'

interface User {
    id: number
    username: string
    role: string
    status: string
}

export default function Dashboard() {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)
    const [health, setHealth] = useState<string>('loading...')
    const [file, setFile] = useState<File | null>(null)
    const [uploadResult, setUploadResult] = useState<any>(null)
    const navigate = useNavigate()

    useEffect(() => {
        const token = localStorage.getItem('access_token')
        if (!token) {
            navigate('/login')
            return
        }

        api
            .get('/health')
            .then((res) => setHealth(JSON.stringify(res.data)))
            .catch(() => setHealth('error'))

        authService.getMe()
            .then((data) => {
                setUser(data)
                setLoading(false)
            })
            .catch(() => {
                authService.logout()
                navigate('/login')
            })
    }, [navigate])

    const onUpload = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!file) return
        setUploadResult('Processing...')
        try {
            const { data } = await videoService.uploadVideo(file)
            setUploadResult(data)
        } catch (err: any) {
            setUploadResult(err?.response?.data || { error: 'Upload failed' })
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-neutral-950 text-neutral-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p>Đang tải...</p>
                </div>
            </div>
        )
    }

    if (!user) {
        return null
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-white">Dashboard</h1>
                <Badge variant={user.role === 'admin' ? 'purple' : 'blue'}>
                    {user.role === 'admin' ? 'Admin' : 'User'}
                </Badge>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="p-6">
                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-green-600 flex items-center justify-center">
                            <span className="text-xl">✅</span>
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-1">Trạng thái hệ thống</h3>
                        <p className="text-sm text-green-400">Hoạt động bình thường</p>
                    </div>
                </Card>

                <Card className="p-6">
                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-blue-600 flex items-center justify-center">
                            <span className="text-xl">🎥</span>
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-1">Live Streams</h3>
                        <p className="text-2xl font-bold text-blue-400">0</p>
                        <p className="text-xs text-neutral-400">đang ghi hình</p>
                    </div>
                </Card>

                <Card className="p-6">
                    <div className="text-center">
                        <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-purple-600 flex items-center justify-center">
                            <span className="text-xl">📹</span>
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-1">Videos</h3>
                        <p className="text-2xl font-bold text-purple-400">0</p>
                        <p className="text-xs text-neutral-400">đã lưu trữ</p>
                    </div>
                </Card>
            </div>

            {/* System Health Status */}
            <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4 text-white">Trạng thái hệ thống</h2>
                <div className="bg-neutral-950/50 rounded-lg p-4">
                    <pre className="text-sm whitespace-pre-wrap break-words text-neutral-300 max-h-64 overflow-auto">
                        {health}
                    </pre>
                </div>
            </Card>

            {/* TikTok Panel */}
            <div>
                <TikTokPanel />
            </div>

            {/* Upload Video */}
            <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4 text-white">Tải lên video</h2>
                <form onSubmit={onUpload} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-neutral-300 mb-2">
                            Chọn video để tải lên
                        </label>
                        <input
                            type="file"
                            accept="video/*"
                            onChange={(e) => setFile(e.target.files?.[0] || null)}
                            className="block w-full text-sm text-neutral-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 file:transition-colors"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={!file}
                        className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-neutral-700 disabled:cursor-not-allowed text-white font-medium transition-colors"
                    >
                        Upload Video
                    </button>
                </form>

                {uploadResult && (
                    <div className="mt-6 p-4 rounded-lg bg-neutral-800 border border-neutral-700">
                        <h3 className="font-semibold mb-2 text-white">Kết quả upload:</h3>
                        <pre className="text-sm whitespace-pre-wrap break-words text-neutral-300 max-h-64 overflow-auto">
                            {JSON.stringify(uploadResult, null, 2)}
                        </pre>
                    </div>
                )}
            </Card>
        </div>
    )
}
