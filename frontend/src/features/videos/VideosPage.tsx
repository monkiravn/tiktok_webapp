import { Card, Button } from '../../components/ui'

export default function VideosPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Quản lý Video</h1>
        <Button variant="primary" size="lg">
          Tải lên video
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-4">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-blue-600 flex items-center justify-center">
              <span className="text-xl">📹</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Tổng video</h3>
            <p className="text-2xl font-bold text-blue-400">0</p>
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-green-600 flex items-center justify-center">
              <span className="text-xl">✅</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Đã xử lý</h3>
            <p className="text-2xl font-bold text-green-400">0</p>
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-yellow-600 flex items-center justify-center">
              <span className="text-xl">⏳</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-1">Đang xử lý</h3>
            <p className="text-2xl font-bold text-yellow-400">0</p>
          </div>
        </Card>
      </div>

      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Danh sách Video</h2>
          <div className="flex items-center gap-2">
            <select className="px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="all">Tất cả</option>
              <option value="processed">Đã xử lý</option>
              <option value="processing">Đang xử lý</option>
              <option value="failed">Thất bại</option>
            </select>
            <Button variant="secondary" size="sm">
              Lọc
            </Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-neutral-700">
                <th className="text-left py-3 px-4 text-neutral-300 font-medium">Tên file</th>
                <th className="text-left py-3 px-4 text-neutral-300 font-medium">Kích thước</th>
                <th className="text-left py-3 px-4 text-neutral-300 font-medium">Trạng thái</th>
                <th className="text-left py-3 px-4 text-neutral-300 font-medium">Ngày tạo</th>
                <th className="text-left py-3 px-4 text-neutral-300 font-medium">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={5} className="text-center py-8 text-neutral-400">
                  Chưa có video nào
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
