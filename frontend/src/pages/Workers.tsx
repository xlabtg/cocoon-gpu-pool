import { Cpu, Activity } from 'lucide-react'

export function Workers() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">GPU Workers</h2>
        <p className="text-gray-500">Manage and monitor your GPU workers</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <WorkerCard
          name="Worker-0"
          instance={0}
          status="healthy"
          gpuUtil={92}
          temperature={68}
          revenue={65.3}
        />
        <WorkerCard
          name="Worker-1"
          instance={1}
          status="healthy"
          gpuUtil={82}
          temperature={71}
          revenue={60.2}
        />
      </div>
    </div>
  )
}

function WorkerCard({
  name,
  instance,
  status,
  gpuUtil,
  temperature,
  revenue,
}: {
  name: string
  instance: number
  status: string
  gpuUtil: number
  temperature: number
  revenue: number
}) {
  const statusColors = {
    healthy: 'bg-green-100 text-green-800',
    degraded: 'bg-yellow-100 text-yellow-800',
    down: 'bg-red-100 text-red-800',
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-primary-50 rounded-full">
            <Cpu className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{name}</h3>
            <p className="text-sm text-gray-500">Instance {instance}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[status as keyof typeof statusColors]}`}>
          {status}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-gray-500">GPU Util</p>
          <p className="text-xl font-bold text-gray-900">{gpuUtil}%</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Temp</p>
          <p className="text-xl font-bold text-gray-900">{temperature}°C</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Revenue</p>
          <p className="text-xl font-bold text-gray-900">{revenue} TON</p>
        </div>
      </div>
    </div>
  )
}
