import { User, Bell, Key } from 'lucide-react'

export function Account() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Account Settings</h2>
        <p className="text-gray-500">Manage your profile and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Section */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-6">
              <User className="w-5 h-5 text-gray-500" />
              <h3 className="text-lg font-semibold text-gray-900">Profile Information</h3>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  TON Wallet Address
                </label>
                <input
                  type="text"
                  readOnly
                  value="UQAbc...xyz"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email (Optional)
                </label>
                <input
                  type="email"
                  placeholder="your@email.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telegram Username
                </label>
                <input
                  type="text"
                  placeholder="@username"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                Save Changes
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-3 mb-6">
              <Bell className="w-5 h-5 text-gray-500" />
              <h3 className="text-lg font-semibold text-gray-900">Notification Preferences</h3>
            </div>
            <div className="space-y-3">
              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm text-gray-700">Payment notifications</span>
              </label>
              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm text-gray-700">Worker alerts</span>
              </label>
              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm text-gray-700">Performance reports</span>
              </label>
            </div>
          </div>
        </div>

        {/* Stats Sidebar */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Stats</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Member Since</p>
                <p className="text-lg font-semibold text-gray-900">Jan 2025</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Workers</p>
                <p className="text-lg font-semibold text-gray-900">2</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Earnings</p>
                <p className="text-lg font-semibold text-gray-900">125.50 TON</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
