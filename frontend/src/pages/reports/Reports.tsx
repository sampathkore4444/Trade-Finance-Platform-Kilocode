import { useState } from 'react'
import { FileText, Download, Calendar, TrendingUp, DollarSign, Shield, Building2, BarChart3, PieChart, LineChart } from 'lucide-react'

const reportTypes = [
  { id: 'lc_summary', name: 'LC Summary Report', description: 'Letter of Credit transaction summary', icon: FileText },
  { id: 'guarantee_summary', name: 'Guarantee Summary', description: 'Bank Guarantee portfolio overview', icon: Shield },
  { id: 'collection_summary', name: 'Collection Report', description: 'Documentary collections analysis', icon: Building2 },
  { id: 'loan_performance', name: 'Loan Performance', description: 'Trade loan portfolio performance', icon: DollarSign },
  { id: 'risk_exposure', name: 'Risk Exposure', description: 'Risk exposure and limits', icon: TrendingUp },
  { id: 'compliance', name: 'Compliance Report', description: 'Regulatory compliance status', icon: FileText },
]

const recentReports = [
  { id: 1, name: 'LC Monthly Summary - January 2024', type: 'LC Summary', generatedDate: '2024-01-15', generatedBy: 'System' },
  { id: 2, name: 'Risk Exposure Report Q4 2023', type: 'Risk Exposure', generatedDate: '2024-01-10', generatedBy: 'Admin' },
  { id: 3, name: 'Compliance Status Report', type: 'Compliance', generatedDate: '2024-01-05', generatedBy: 'System' },
]

export default function Reports() {
  const [selectedReport, setSelectedReport] = useState('')
  const [dateRange, setDateRange] = useState('last_30_days')

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
              <p className="text-xl font-semibold text-secondary-900">156</p>
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
              <p className="text-xl font-semibold text-secondary-900">23</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg mr-4">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Scheduled</p>
              <p className="text-xl font-semibold text-secondary-900">8</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg mr-4">
              <Calendar className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">This Week</p>
              <p className="text-xl font-semibold text-secondary-900">5</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Types */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-secondary-900">Generate New Report</h3>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {reportTypes.map((report) => (
                  <button
                    key={report.id}
                    onClick={() => setSelectedReport(report.id)}
                    className={`flex items-start p-4 border rounded-lg text-left transition-all ${
                      selectedReport === report.id
                        ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                        : 'border-secondary-200 hover:border-secondary-300 hover:bg-secondary-50'
                    }`}
                  >
                    <report.icon className={`w-6 h-6 mr-3 ${selectedReport === report.id ? 'text-primary-600' : 'text-secondary-400'}`} />
                    <div>
                      <p className="font-medium text-secondary-900">{report.name}</p>
                      <p className="text-sm text-secondary-500">{report.description}</p>
                    </div>
                  </button>
                ))}
              </div>

              {selectedReport && (
                <div className="mt-6 pt-6 border-t border-secondary-200">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="label">Date Range</label>
                      <select
                        value={dateRange}
                        onChange={(e) => setDateRange(e.target.value)}
                        className="input"
                      >
                        <option value="last_7_days">Last 7 Days</option>
                        <option value="last_30_days">Last 30 Days</option>
                        <option value="last_90_days">Last 90 Days</option>
                        <option value="this_month">This Month</option>
                        <option value="this_quarter">This Quarter</option>
                        <option value="this_year">This Year</option>
                        <option value="custom">Custom Range</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <button className="btn-primary w-full">
                        <Download className="w-4 h-4 mr-2" />
                        Generate Report
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Reports */}
        <div className="space-y-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-secondary-900">Recent Reports</h3>
            </div>
            <div className="card-body">
              <div className="space-y-3">
                {recentReports.map((report) => (
                  <div key={report.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-secondary-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-secondary-900">{report.name}</p>
                        <p className="text-xs text-secondary-500">{report.type}</p>
                      </div>
                    </div>
                    <button className="text-primary-600 hover:text-primary-500">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
              <button className="btn-outline w-full mt-4">
                View All Reports
              </button>
            </div>
          </div>

          {/* Scheduled Reports */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-secondary-900">Scheduled Reports</h3>
            </div>
            <div className="card-body">
              <div className="space-y-3">
                {[
                  { name: 'Weekly LC Summary', frequency: 'Every Monday', nextRun: '2024-01-22' },
                  { name: 'Monthly Compliance', frequency: '1st of month', nextRun: '2024-02-01' },
                  { name: 'Quarterly Risk', frequency: 'Quarterly', nextRun: '2024-04-01' },
                ].map((schedule, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-secondary-900">{schedule.name}</p>
                      <p className="text-xs text-secondary-500">{schedule.frequency}</p>
                    </div>
                    <span className="text-xs text-secondary-400">Next: {schedule.nextRun}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
