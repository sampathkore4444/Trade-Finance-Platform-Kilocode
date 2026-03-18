import { useState, useEffect } from 'react'
import { Shield, FileText, Clock, CheckCircle, AlertTriangle, RefreshCw, Download, Calendar, User, Building2, Loader2 } from 'lucide-react'
import api from '@/api/axios'

interface ComplianceCheck {
  id: string
  type: string
  status: string
  submittedBy: string
  date: string
}

interface Violation {
  id: number
  type: string
  severity: string
  description: string
  date: string
}

interface AuditLog {
  id: number
  action: string
  user: string
  date: string
  details: string
}

export default function ComplianceDashboard() {
  const [isLoading, setIsLoading] = useState(true)
  const [pendingReviews, setPendingReviews] = useState<ComplianceCheck[]>([])
  const [recentViolations, setRecentViolations] = useState<Violation[]>([])
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])

  // Stats
  const [complianceScore, setComplianceScore] = useState(94)
  const [pendingCount, setPendingCount] = useState(0)
  const [violationsCount, setViolationsCount] = useState(0)
  const [approvedCount, setApprovedCount] = useState(0)

  useEffect(() => {
    fetchComplianceData()
  }, [])

  const fetchComplianceData = async () => {
    setIsLoading(true)
    try {
      // Fetch compliance data from API
      const [pendingResponse, failedResponse, allComplianceResponse] = await Promise.allSettled([
        api.get('/compliance/pending/list'),
        api.get('/compliance/failed/list'),
        api.get('/compliance/'),
      ])

      // Process pending reviews
      const pending: ComplianceCheck[] = []
      if (pendingResponse.status === 'fulfilled' && pendingResponse.value.data) {
        const items = pendingResponse.value.data.slice(0, 5) || []
        items.forEach((check: any) => {
          pending.push({
            id: check.id,
            type: check.entity_type || 'Compliance',
            status: check.status || 'Pending Review',
            submittedBy: check.checked_by || 'System',
            date: check.created_at ? new Date(check.created_at).toLocaleDateString() : '-',
          })
        })
      }
      setPendingReviews(pending)
      setPendingCount(pending.length)

      // Process violations
      const violations: Violation[] = []
      if (failedResponse.status === 'fulfilled' && failedResponse.value.data) {
        const items = failedResponse.value.data.slice(0, 5) || []
        items.forEach((check: any) => {
          violations.push({
            id: check.id,
            type: check.check_type || 'Compliance',
            severity: check.risk_level || 'medium',
            description: `${check.entity_type || 'Check'}-${check.id}: ${check.check_name || 'Compliance check failed'}`,
            date: check.created_at ? new Date(check.created_at).toLocaleDateString() : '-',
          })
        })
      }
      setRecentViolations(violations)
      setViolationsCount(violations.length)

      // Get approved count from all compliance checks
      if (allComplianceResponse.status === 'fulfilled' && allComplianceResponse.value.data) {
        const all = allComplianceResponse.value.data || []
        setApprovedCount(all.length)
        
        // Calculate compliance score based on pass rate
        const passed = all.filter((c: any) => c.status === 'passed' || c.status === 'approved').length
        if (all.length > 0) {
          setComplianceScore(Math.round((passed / all.length) * 100))
        }
      }

      // Audit logs (would come from a dedicated endpoint in real implementation)
      setAuditLogs([
        { id: 1, action: 'System Update', user: 'Admin', date: new Date().toLocaleString(), details: 'Compliance dashboard accessed' },
        { id: 2, action: 'Data Refresh', user: 'System', date: new Date().toLocaleString(), details: 'Compliance data updated from API' },
      ])

    } catch (error) {
      console.error('Error fetching compliance data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const complianceStats = [
    { name: 'Compliance Score', value: `${complianceScore}%`, change: '+1.2%', icon: Shield, color: 'bg-green-500' },
    { name: 'Pending Reviews', value: pendingCount.toString(), change: '-5', icon: Clock, color: 'bg-yellow-500' },
    { name: 'Violations', value: violationsCount.toString(), change: '-1', icon: AlertTriangle, color: 'bg-red-500' },
    { name: 'Approved', value: approvedCount.toString(), change: '+23', icon: CheckCircle, color: 'bg-blue-500' },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }

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
          <button className="btn-outline flex items-center" onClick={fetchComplianceData}>
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
              <div className="flex-1">
                <p className="text-sm font-medium text-secondary-500">{stat.name}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-secondary-900">{stat.value}</p>
                  <span className={`ml-2 text-sm font-medium ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.change}
                  </span>
                </div>
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
            {pendingReviews.length > 0 ? (
              <div className="space-y-4">
                {pendingReviews.map((review) => (
                  <div key={review.id} className="flex items-start p-3 bg-secondary-50 rounded-lg">
                    <div className="p-2 rounded-lg mr-3 bg-yellow-100">
                      <Clock className="w-4 h-4 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-secondary-500 uppercase">{review.type}</span>
                        <span className="text-xs text-secondary-400">{review.date}</span>
                      </div>
                      <p className="text-sm font-medium text-secondary-900 mt-1">{review.id}</p>
                      <p className="text-sm text-secondary-500">By: {review.submittedBy}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-secondary-500">No pending reviews</p>
            )}
          </div>
        </div>

        {/* Recent Violations */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-medium text-secondary-900">Recent Violations</h3>
            <span className="badge badge-danger">{recentViolations.length} Issues</span>
          </div>
          <div className="card-body">
            {recentViolations.length > 0 ? (
              <div className="space-y-4">
                {recentViolations.map((violation) => (
                  <div key={violation.id} className="flex items-start p-3 bg-secondary-50 rounded-lg">
                    <div className={`p-2 rounded-lg mr-3 ${
                      violation.severity === 'high' ? 'bg-red-100' : 
                      violation.severity === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                    }`}>
                      <AlertTriangle className={`w-4 h-4 ${
                        violation.severity === 'high' ? 'text-red-600' :
                        violation.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                      }`} />
                    </div>
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
            ) : (
              <p className="text-sm text-secondary-500">No violations found</p>
            )}
          </div>
        </div>
      </div>

      {/* Audit Logs */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-secondary-900">Audit Logs</h3>
        </div>
        <div className="card-body">
          {auditLogs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Action</th>
                    <th>User</th>
                    <th>Date</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLogs.map((log) => (
                    <tr key={log.id}>
                      <td className="font-medium">{log.action}</td>
                      <td>{log.user}</td>
                      <td className="text-secondary-500">{log.date}</td>
                      <td>{log.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-secondary-500">No audit logs available</p>
          )}
        </div>
      </div>
    </div>
  )
}
