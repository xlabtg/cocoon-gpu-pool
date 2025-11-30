import { Activity, Cpu, DollarSign, TrendingUp } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

// Mock data for demonstration
const mockMetrics = [
  { time: '00:00', utilization: 65, revenue: 2.5 },
  { time: '04:00', utilization: 72, revenue: 3.2 },
  { time: '08:00', utilization: 85, revenue: 4.1 },
  { time: '12:00', utilization: 91, revenue: 4.8 },
  { time: '16:00', utilization: 87, revenue: 4.3 },
  { time: '20:00', utilization: 78, revenue: 3.7 },
]

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Pool Overview</h2>
        <p className="text-gray-500">Monitor your GPU pool performance</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Workers"
          value="2"
          icon={Cpu}
          trend="+0%"
          trendUp={false}
        />
        <StatCard
          title="Total Revenue"
          value="125.50 TON"
          icon={DollarSign}
          trend="+12.5%"
          trendUp={true}
        />
        <StatCard
          title="Avg GPU Utilization"
          value="87%"
          icon={Activity}
          trend="+5.2%"
          trendUp={true}
        />
        <StatCard
          title="Total Requests"
          value="15,234"
          icon={TrendingUp}
          trend="+8.1%"
          trendUp={true}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* GPU Utilization Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            GPU Utilization (24h)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="utilization"
                stroke="#3b82f6"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Revenue Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Revenue (24h)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#10b981"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Activity
        </h3>
        <div className="space-y-3">
          <ActivityItem
            type="payment"
            message="Payment received: 25.50 TON"
            time="2 hours ago"
          />
          <ActivityItem
            type="worker"
            message="Worker-1 came online"
            time="4 hours ago"
          />
          <ActivityItem
            type="alert"
            message="High GPU temperature on Worker-0 resolved"
            time="6 hours ago"
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendUp,
}: {
  title: string
  value: string
  icon: any
  trend: string
  trendUp: boolean
}) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          <p className={`text-sm mt-1 ${trendUp ? 'text-green-600' : 'text-gray-500'}`}>
            {trend} vs last week
          </p>
        </div>
        <div className="p-3 bg-primary-50 rounded-full">
          <Icon className="w-6 h-6 text-primary-600" />
        </div>
      </div>
    </div>
  )
}

function ActivityItem({
  type,
  message,
  time,
}: {
  type: string
  message: string
  time: string
}) {
  const colors = {
    payment: 'bg-green-100 text-green-800',
    worker: 'bg-blue-100 text-blue-800',
    alert: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50">
      <div className={`p-2 rounded ${colors[type as keyof typeof colors]}`}>
        <Activity className="w-4 h-4" />
      </div>
      <div className="flex-1">
        <p className="text-sm text-gray-900">{message}</p>
        <p className="text-xs text-gray-500 mt-1">{time}</p>
      </div>
    </div>
  )
}
