import { Shield, FileText, Clock, CheckCircle, AlertTriangle, RefreshCw, Download, Calendar, User, Building2 } from 'lucide-react'

const complianceStats = [
  { name: 'Compliance Score', value: '94%', change: '+1.2%', icon: Shield, color: 'bg-green-500' },
  { name: 'Pending Reviews', value: '12', change: '-5', icon: Clock, color: 'bg-yellow-500' },
  { name: 'Violations', value: '2', change: '-1', icon: AlertTriangle, color: 'bg-red-500' },
  { name: 'Approved', value: '156', change: '+23', icon: CheckCircle, color: 'bg-blue-500' },
]

const pendingReviews = [
  { id: 'LC-2024-0156', type: 'LC', status: 'Pending Review', submittedBy: 'John Smith', date: '2024-01-15' },
  { id: 'GUA-2024-0089', type: 'Guarantee', status: 'Under Review', submittedBy: 'Jane Doe', date: '2024-01-14' },
  { id: 'LC-2024-0155', type: 'LC', status: 'Awaiting Documents', submittedBy: 'Mike Johnson', date: '2024-01-14' },
]

const recentViolations = [
  { id: 1, type: 'KYC', severity: 'high', description: 'Customer verification incomplete for ACME Corp', date: '2024-01-15' },
  { id: 2, type: 'AML', severity: 'medium', description: 'Transaction pattern flagged for review', date: '2024-01-14' },
]

const auditLogs = [
  { id: 1, action: 'LC Approved', user: 'Sarah Wilson', date: '2024-01-15 14:30', details: 'LC-2024-0152 approved' },
  { id: 2, action: 'Document Uploaded', user: 'Tom Brown', date: '2024-01-15 13:45', details: 'Bill of Lading for LC-2024-0150' },
  { id: 3, action: 'User Login', user: 'Admin User', date: '2024-01-15 12:00', details: 'Successful login from IP 192.168.1.1' },
  { id: 4, action: 'Settings Changed', user: 'System Admin', date: '2024-01-15 10:30', details: 'Updated LC approval thresholds' },
]

export default function ComplianceDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Compliance Dashboard</h1>
          <p className="text-sm text-secondary-500 mt-1">Monitor compliance status and regulatory requirements</p>
        </div>
        <div className="flex space-x-2">
          <button className="btn-outline flex items-center">
            <Download className="w-4 h-4 mr-2" /> Export Report
          </button>
          <button className="btn-outline flex items-center">
            <RefreshCw className="w-4 h-4 mr-2" /> Refresh
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {complianceStats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="card-body flex items-center">
              <div className={`${stat.color} p-3 rounded-lg mr-4`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-secondary-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-secondary-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Reviews */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-medium text-secondary-900">Pending Reviews</h3>
            <span className="badge badge-warning">{pendingReviews.length} Pending</span>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              {pendingReviews.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-secondary-400 mr-3" />
                    <div>
                      <p className="font-medium text-secondary-900">{item.id}</p>
                      <p className="text-xs text-secondary-500">Type: {item.type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-secondary-900">{item.status}</p>
                    <p className="text-xs text-secondary-500">{item.submittedBy} • {item.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Violations */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-medium text-secondary-900">Recent Violations</h3>
            <span className="badge badge-danger">{recentViolations.length} Active</span>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              {recentViolations.map((violation) => (
                <div key={violation.id} className="flex items-start p-3 bg-red-50 rounded-lg">
                  <AlertTriangle className={`w-5 h-5 mr-3 ${violation.severity === 'high' ? 'text-red-600' : 'text-yellow-600'}`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-secondary-500 uppercase">{violation.type}</span>
                      <span className="text-xs text-secondary-400">{violation.date}</span>
                    </div>
                    <p className="text-sm text-secondary-900 mt-1">{violation.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Audit Logs */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-secondary-900">Audit Trail</h3>
        </div>
        <div className="card-body">
          <table className="table">
            <thead>
              <tr>
                <th>Action</th>
                <th>User</th>
                <th>Date & Time</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td className="font-medium">{log.action}</td>
                  <td>
                    <div className="flex items-center">
                      <User className="w-4 h-4 text-secondary-400 mr-2" />
                      {log.user}
                    </div>
                  </td>
                  <td className="text-secondary-500">{log.date}</td>
                  <td className="text-secondary-500">{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
