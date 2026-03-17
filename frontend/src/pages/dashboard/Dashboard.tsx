import { FileText, Shield, DollarSign, AlertTriangle, TrendingUp, Clock } from 'lucide-react'

const stats = [
  {
    name: 'Active LCs',
    value: '24',
    change: '+12%',
    changeType: 'positive',
    icon: FileText,
    color: 'bg-blue-500',
  },
  {
    name: 'Bank Guarantees',
    value: '18',
    change: '+8%',
    changeType: 'positive',
    icon: Shield,
    color: 'bg-green-500',
  },
  {
    name: 'Trade Loans',
    value: '$4.2M',
    change: '+23%',
    changeType: 'positive',
    icon: DollarSign,
    color: 'bg-purple-500',
  },
  {
    name: 'Risk Alerts',
    value: '3',
    change: '-2',
    changeType: 'negative',
    icon: AlertTriangle,
    color: 'bg-red-500',
  },
]

const recentTransactions = [
  { id: 'LC-001', type: 'LC', status: 'Approved', amount: '$250,000', date: '2024-01-15' },
  { id: 'GUA-002', type: 'Guarantee', status: 'Pending', amount: '$50,000', date: '2024-01-14' },
  { id: 'LC-003', type: 'LC', status: 'Under Review', amount: '$750,000', date: '2024-01-14' },
  { id: 'LOAN-004', type: 'Loan', status: 'Disbursed', amount: '$1,200,000', date: '2024-01-13' },
  { id: 'COL-005', type: 'Collection', status: 'Documents Received', amount: '$85,000', date: '2024-01-12' },
]

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">Dashboard</h1>
        <p className="text-sm text-secondary-500">
          Welcome back! Here's what's happening today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="card-body flex items-center">
              <div className={`${stat.color} p-3 rounded-lg mr-4`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-secondary-500">{stat.name}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-secondary-900">
                    {stat.value}
                  </p>
                  <span
                    className={`ml-2 text-sm font-medium ${
                      stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {stat.change}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transaction Volume Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">Transaction Volume</h3>
          </div>
          <div className="card-body">
            <div className="h-64 flex items-center justify-center text-secondary-400">
              <div className="text-center">
                <TrendingUp className="h-12 w-12 mx-auto mb-2" />
                <p>Chart placeholder</p>
              </div>
            </div>
          </div>
        </div>

        {/* Pending Actions */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">Pending Actions</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {[
                { title: 'LC-2024-0156', description: 'Awaiting approval', time: '2 hours ago' },
                { title: 'GUA-2024-0089', description: 'Documents required', time: '4 hours ago' },
                { title: 'LOAN-2024-0234', description: 'Credit review pending', time: '1 day ago' },
              ].map((item, index) => (
                <div key={index} className="flex items-start">
                  <Clock className="h-5 w-5 text-secondary-400 mr-3 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-secondary-900">{item.title}</p>
                    <p className="text-sm text-secondary-500">{item.description}</p>
                  </div>
                  <span className="text-xs text-secondary-400">{item.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h3 className="text-lg font-medium text-secondary-900">Recent Transactions</h3>
          <button className="text-sm text-primary-600 hover:text-primary-500">
            View all
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recentTransactions.map((tx) => (
                <tr key={tx.id}>
                  <td className="font-medium">{tx.id}</td>
                  <td>{tx.type}</td>
                  <td>
                    <span
                      className={`badge ${
                        tx.status === 'Approved' || tx.status === 'Disbursed'
                          ? 'badge-success'
                          : tx.status === 'Pending' || tx.status === 'Under Review'
                          ? 'badge-warning'
                          : 'badge-info'
                      }`}
                    >
                      {tx.status}
                    </span>
                  </td>
                  <td>{tx.amount}</td>
                  <td className="text-secondary-500">{tx.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
