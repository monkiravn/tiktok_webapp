import { Card, Button } from '../../components/ui'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Cài đặt</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Cài đặt chung</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Ngôn ngữ
              </label>
              <select className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="vi">Tiếng Việt</option>
                <option value="en">English</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Múi giờ
              </label>
              <select className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="Asia/Ho_Chi_Minh">GMT+7 (Việt Nam)</option>
                <option value="UTC">UTC</option>
              </select>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="notifications"
                className="mr-2 w-4 h-4 text-blue-600 bg-neutral-800 border-neutral-700 rounded focus:ring-blue-500"
              />
              <label htmlFor="notifications" className="text-neutral-300">
                Bật thông báo
              </label>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Cài đặt TikTok</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Thư mục lưu video
              </label>
              <div className="flex">
                <input
                  type="text"
                  className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-l-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="/path/to/videos"
                />
                <Button variant="secondary" size="md" className="rounded-l-none">
                  Chọn
                </Button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Chất lượng mặc định
              </label>
              <select className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="720p">720p</option>
                <option value="1080p">1080p</option>
              </select>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="auto-record"
                className="mr-2 w-4 h-4 text-blue-600 bg-neutral-800 border-neutral-700 rounded focus:ring-blue-500"
              />
              <label htmlFor="auto-record" className="text-neutral-300">
                Tự động ghi hình khi có live stream
              </label>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Tài khoản</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Tên người dùng
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="username"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-2">
                Email
              </label>
              <input
                type="email"
                className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="email@example.com"
              />
            </div>
            <Button variant="primary" size="md">
              Cập nhật thông tin
            </Button>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-white">Bảo mật</h2>
          <div className="space-y-4">
            <Button variant="secondary" size="md" className="w-full">
              Đổi mật khẩu
            </Button>
            <Button variant="secondary" size="md" className="w-full">
              Bật xác thực 2 bước
            </Button>
            <hr className="border-neutral-700" />
            <Button variant="danger" size="md" className="w-full">
              Đăng xuất tất cả thiết bị
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
