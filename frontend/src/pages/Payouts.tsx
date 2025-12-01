import { DollarSign, Download } from 'lucide-react'

const mockPayouts = [
  { id: 1, date: '2025-01-15', amount: 25.5, confirmed: true },
  { id: 2, date: '2025-01-08', amount: 30.2, confirmed: true },
  { id: 3, date: '2025-01-01', amount: 19.8, confirmed: true },
  { id: 4, date: '2024-12-25', amount: 22.1, confirmed: true },
  { id: 5, date: '2024-12-18', amount: 27.9, confirmed: true },
]

export function Payouts() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Payout History</h2>
          <p className="text-gray-500">View your payment transactions</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          <Download className="w-4 h-4" />
          Export Tax Report
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-sm text-gray-500">Total Payouts</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">5</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-sm text-gray-500">Total Amount</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">125.50 TON</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <p className="text-sm text-gray-500">Last Payout</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">2 days ago</p>
        </div>
      </div>

      {/* Payouts Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {mockPayouts.map((payout) => (
              <tr key={payout.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {payout.date}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {payout.amount} TON
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    Confirmed
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-primary-600 hover:text-primary-700 cursor-pointer">
                  View Details
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
