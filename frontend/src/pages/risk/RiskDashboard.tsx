import { AlertTriangle, Shield, TrendingUp, TrendingDown, DollarSign, Clock, Activity, RefreshCw } from 'lucide-react'

const riskStats = [
  { name: 'Total Exposure', value: '$12.5M', change: '+2.3%', changeType: 'negative', icon: DollarSign, color: 'bg-red-500' },
  { name: 'Active Risk Alerts', value: '8', change: '-3', changeType: 'positive', icon: AlertTriangle, color: 'bg-yellow-500' },
  { name: 'Compliance Score', value: '94%', change: '+1.2%', changeType: 'positive', icon: Shield, color: 'bg-green-500' },
  { name: 'Default Rate', value: '0.8%', change: '-0.2%', changeType: 'positive', icon: TrendingDown, color: 'bg-blue-500' },
]

const riskAlerts = [
  { id: 1, type: 'Credit', severity: 'high', description: 'LC-2024-0156: Beneficiary country risk elevated', time: '2 hours ago' },
  { id: 2, type: 'Compliance', severity: 'medium', description: 'Document discrepancy detected in LC-2024-0142', time: '4 hours ago' },
  { id: 3, type: 'Operational', severity: 'low', description: 'Expiring LC requires attention: LC-2024-0089', time: '1 day ago' },
  { id: 4, type: 'Market', severity: 'medium', description: 'Currency fluctuation warning for USD/EUR', time: '2 days ago' },
]

const portfolioBreakdown = [
  { name: 'Letter of Credit', value: 45, color: 'bg-blue-500' },
  { name: 'Bank Guarantees', value: 30, color: 'bg-green-500' },
  { name: 'Trade Loans', value: 15, color: 'bg-purple-500' },
  { name: 'Invoice Financing', value: 10, color: 'bg-yellow-500' },
]

export default function RiskDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Risk Dashboard</h1>
          <p className="text-sm text-secondary-500 mt-1">Monitor and manage trade finance risks</p>
        </div>
        <button className="btn-outline flex items-center">
          <RefreshCw className="w-4 h-4 mr-2" /> Refresh
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {riskStats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="card-body flex items-center">
              <div className={`${stat.color} p-3 rounded-lg mr-4`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-secondary-500">{stat.name}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-secondary-900">{stat.value}</p>
                  <span className={`ml-2 text-sm font-medium ${stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.change}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Alerts */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-medium text-secondary-900">Risk Alerts</h3>
            <span className="badge badge-danger">{riskAlerts.length} Active</span>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {riskAlerts.map((alert) => (
                <div key={alert.id} className="flex items-start p-3 bg-secondary-50 rounded-lg">
                  <div className={`p-2 rounded-lg mr-3 ${
                    alert.severity === 'high' ? 'bg-red-100' : 
                    alert.severity === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                  }`}>
                    <AlertTriangle className={`w-4 h-4 ${
                      alert.severity === 'high' ? 'text-red-600' :
                      alert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-secondary-500 uppercase">{alert.type}</span>
                      <span className="text-xs text-secondary-400">{alert.time}</span>
                    </div>
                    <p className="text-sm text-secondary-900 mt-1">{alert.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Portfolio Breakdown */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">Portfolio Breakdown</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {portfolioBreakdown.map((item) => (
                <div key={item.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-secondary-700">{item.name}</span>
                    <span className="text-sm text-secondary-500">{item.value}%</span>
                  </div>
                  <div className="w-full bg-secondary-200 rounded-full h-2">
                    <div className={`${item.color} h-2 rounded-full`} style={{ width: `${item.value}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Additional Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Country Risk */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">Country Risk Exposure</h3>
          </div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>Country</th>
                  <th>Exposure</th>
                  <th>Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { country: 'China', exposure: '$3.2M', risk: 'Medium' },
                  { country: 'Germany', exposure: '$2.8M', risk: 'Low' },
                  { country: 'USA', exposure: '$2.1M', risk: 'Low' },
                  { country: 'India', exposure: '$1.5M', risk: 'Medium' },
                  { country: 'Brazil', exposure: '$0.9M', risk: 'High' },
                ].map((item) => (
                  <tr key={item.country}>
                    <td className="font-medium">{item.country}</td>
                    <td>{item.exposure}</td>
                    <td>
                      <span className={`badge ${
                        item.risk === 'High' ? 'badge-danger' :
                        item.risk === 'Medium' ? 'badge-warning' : 'badge-success'
                      }`}>
                        {item.risk}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Counterparty Risk */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">Top Counterparty Exposures</h3>
          </div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>Counterparty</th>
                  <th>Exposure</th>
                  <th>Rating</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: 'Acme Corp', exposure: '$1.2M', rating: 'A+' },
                  { name: 'Global Trading Co', exposure: '$950K', rating: 'A' },
                  { name: 'Pacific Exports', exposure: '$820K', rating: 'BBB+' },
                  { name: 'Eurotrade GmbH', exposure: '$710K', rating: 'A-' },
                  { name: 'Asian Industries', exposure: '$580K', rating: 'BBB' },
                ].map((item) => (
                  <tr key={item.name}>
                    <td className="font-medium">{item.name}</td>
                    <td>{item.exposure}</td>
                    <td><span className="badge badge-success">{item.rating}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
