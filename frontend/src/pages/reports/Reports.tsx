import { useState, useEffect } from 'react'
import { FileText, Download, Calendar, TrendingUp, DollarSign, Shield, Building2, BarChart3, PieChart, LineChart, Loader2 } from 'lucide-react'
import api from '@/api/axios'

interface Report {
  id: number
  name: string
  type: string
  generatedDate: string
  generatedBy: string
}

export default function Reports() {
  const [isLoading, setIsLoading] = useState(true)
  const [recentReports, setRecentReports] = useState<Report[]>([])
  const [selectedReport, setSelectedReport] = useState('')
  const [dateRange, setDateRange] = useState('last_30_days')

  // Stats
  const [totalReports, setTotalReports] = useState(0)
  const [monthlyGenerated, setMonthlyGenerated] = useState(0)
  const [activeUsers, setActiveUsers] = useState(0)
  const [storageUsed, setStorageUsed] = useState(0)

  useEffect(() => {
    fetchReportsData()
  }, [])

  const fetchReportsData = async () => {
    setIsLoading(true)
    try {
      // Note: Reports API endpoint doesn't exist in backend yet
      // Using sample data for now
      setRecentReports([])
      setTotalReports(0)

      // Users endpoint requires admin permissions - skip to avoid 401 logout
      setActiveUsers(0)

      // Calculate monthly generated reports (mock calculation based on total)
      setMonthlyGenerated(0)
      
      // Storage used (mock - would come from backend in real implementation)
      setStorageUsed(0)

    } catch (error) {
      console.error('Error fetching reports data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const reportTypes = [
    { id: 'lc_summary', name: 'LC Summary Report', description: 'Letter of Credit transaction summary', icon: FileText },
    { id: 'guarantee_summary', name: 'Guarantee Summary', description: 'Bank Guarantee portfolio overview', icon: Shield },
    { id: 'collection_summary', name: 'Collection Report', description: 'Documentary collections analysis', icon: Building2 },
    { id: 'loan_performance', name: 'Loan Performance', description: 'Trade loan portfolio performance', icon: DollarSign },
    { id: 'risk_exposure', name: 'Risk Exposure', description: 'Risk exposure and limits', icon: TrendingUp },
    { id: 'compliance', name: 'Compliance Report', description: 'Regulatory compliance status', icon: FileText },
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
          <h1 className="text-2xl font-bold text-secondary-900">Reports & Analytics</h1>
          <p className="text-sm text-secondary-500 mt-1">Generate and view trade finance reports</p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg mr-4">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Total Reports</p>
              <p className="text-xl font-semibold text-secondary-900">{totalReports}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-green-100 rounded-lg mr-4">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">This Month</p>
              <p className="text-xl font-semibold text-secondary-900">{monthlyGenerated}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg mr-4">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Active Users</p>
              <p className="text-xl font-semibold text-secondary-900">{activeUsers}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg mr-4">
              <PieChart className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Storage Used</p>
              <p className="text-xl font-semibold text-secondary-900">{storageUsed} MB</p>
            </div>
          </div>
        </div>
      </div>

      {/* Report Types */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-secondary-900">Available Reports</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reportTypes.map((report) => (
              <div key={report.id} className="p-4 border border-secondary-200 rounded-lg hover:bg-secondary-50 cursor-pointer transition-colors">
                <div className="flex items-start">
                  <div className="p-2 bg-primary-100 rounded-lg mr-3">
                    <report.icon className="h-5 w-5 text-primary-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-secondary-900">{report.name}</h4>
                    <p className="text-xs text-secondary-500 mt-1">{report.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Reports */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h3 className="text-lg font-medium text-secondary-900">Recent Reports</h3>
          <button className="text-sm text-primary-600 hover:text-primary-500">
            View all
          </button>
        </div>
        <div className="card-body">
          {recentReports.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Report Name</th>
                    <th>Type</th>
                    <th>Generated Date</th>
                    <th>Generated By</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentReports.map((report) => (
                    <tr key={report.id}>
                      <td className="font-medium">{report.name}</td>
                      <td>{report.type}</td>
                      <td className="text-secondary-500">{report.generatedDate}</td>
                      <td>{report.generatedBy}</td>
                      <td>
                        <button className="text-primary-600 hover:text-primary-500">
                          <Download className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-secondary-500">
              No reports generated yet
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
