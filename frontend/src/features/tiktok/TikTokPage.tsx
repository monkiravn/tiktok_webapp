import { Card, Button } from '../../components/ui'

export default function TikTokPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">TikTok Live Recording</h1>
        <Button variant="primary" size="lg">
          Bắt đầu ghi hình
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Cấu hình Live Stream</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                TikTok Username
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Nhập username TikTok"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Chất lượng video
              </label>
              <select className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="720p">720p</option>
                <option value="1080p">1080p</option>
              </select>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Trạng thái</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-neutral-300">Trạng thái ghi hình:</span>
              <span className="px-2 py-1 bg-red-600 text-white text-sm rounded">Offline</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-neutral-300">Thời gian ghi:</span>
              <span className="text-white">00:00:00</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-neutral-300">Kích thước file:</span>
              <span className="text-white">0 MB</span>
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4 text-white">Lịch sử ghi hình</h2>
        <div className="text-neutral-400 text-center py-8">
          Chưa có video nào được ghi hình
        </div>
      </Card>
    </div>
  )
}
