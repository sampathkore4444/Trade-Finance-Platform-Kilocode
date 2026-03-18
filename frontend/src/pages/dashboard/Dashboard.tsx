import { useState, useEffect } from 'react'
import { FileText, Shield, DollarSign, AlertTriangle, TrendingUp, Clock, Loader2 } from 'lucide-react'
import api from '@/api/axios'

interface DashboardStats {
  activeLCs: number
  lcChange: string
  guarantees: number
  guaranteeChange: string
  loans: number
  loanChange: string
  riskAlerts: number
  riskChange: string
}

interface Transaction {
  id: string
  type: string
  status: string
  amount: string
  date: string
}

interface PendingAction {
  id: string
  description: string
  time: string
}

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats>({
    activeLCs: 0,
    lcChange: '+0%',
    guarantees: 0,
    guaranteeChange: '+0%',
    loans: 0,
    loanChange: '+0%',
    riskAlerts: 0,
    riskChange: '0',
  })
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([])
  const [pendingActions, setPendingActions] = useState<PendingAction[]>([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setIsLoading(true)
    try {
      // Fetch data from all modules in parallel
      const [lcResponse, guaranteeResponse, loanResponse, collectionResponse, invoiceResponse] = await Promise.allSettled([
        api.get('/lc/?page_size=100'),
        api.get('/guarantee/?page_size=100'),
        api.get('/loan/loans/?page_size=100'),
        api.get('/collection/collections/?page_size=100'),
        api.get('/invoice/invoices/?page_size=100'),
      ])

      // Calculate stats from responses
      let activeLCs = 0
      let guarantees = 0
      let totalLoans = 0

      if (lcResponse.status === 'fulfilled' && lcResponse.value.data) {
        const lcs = lcResponse.value.data.items || []
        activeLCs = lcs.length
      }

      if (guaranteeResponse.status === 'fulfilled' && guaranteeResponse.value.data) {
        const guars = guaranteeResponse.value.data.items || []
        guarantees = guars.length
      }

      if (loanResponse.status === 'fulfilled' && loanResponse.value.data) {
        const loans = loanResponse.value.data.items || []
        totalLoans = loans.reduce((sum: number, loan: any) => sum + (loan.principal_amount || 0), 0)
      }

      setStats({
        activeLCs,
        lcChange: '+12%',
        guarantees,
        guaranteeChange: '+8%',
        loans: totalLoans,
        loanChange: '+23%',
        riskAlerts: 3,
        riskChange: '-2',
      })

      // Build recent transactions from all modules
      const transactions: Transaction[] = []

      if (lcResponse.status === 'fulfilled' && lcResponse.value.data) {
        const lcs = lcResponse.value.data.items || []
        lcs.slice(0, 3).forEach((lc: any) => {
          transactions.push({
            id: lc.lc_number,
            type: 'LC',
            status: lc.status || 'Draft',
            amount: new Intl.NumberFormat('en-US', { style: 'currency', currency: lc.currency || 'USD' }).format(lc.amount || 0),
            date: lc.created_at ? new Date(lc.created_at).toLocaleDateString() : '-',
          })
        })
      }

      if (guaranteeResponse.status === 'fulfilled' && guaranteeResponse.value.data) {
        const guars = guaranteeResponse.value.data.items || []
        guars.slice(0, 2).forEach((guar: any) => {
          transactions.push({
            id: guar.guarantee_number,
            type: 'Guarantee',
            status: guar.status || 'Draft',
            amount: new Intl.NumberFormat('en-US', { style: 'currency', currency: guar.currency || 'USD' }).format(guar.guarantee_amount || 0),
            date: guar.created_at ? new Date(guar.created_at).toLocaleDateString() : '-',
          })
        })
      }

      if (loanResponse.status === 'fulfilled' && loanResponse.value.data) {
        const loans = loanResponse.value.data.items || []
        loans.slice(0, 2).forEach((loan: any) => {
          transactions.push({
            id: loan.loan_number,
            type: 'Loan',
            status: loan.status || 'Draft',
            amount: new Intl.NumberFormat('en-US', { style: 'currency', currency: loan.currency || 'USD' }).format(loan.principal_amount || 0),
            date: loan.created_at ? new Date(loan.created_at).toLocaleDateString() : '-',
          })
        })
      }

      // Sort by date (most recent first) and take top 5
      transactions.sort((a, b) => {
        if (a.date === '-' || b.date === '-') return 0
        return new Date(b.date).getTime() - new Date(a.date).getTime()
      })

      setRecentTransactions(transactions.slice(0, 5))

      // Set pending actions (mock logic - in real app would come from backend)
      setPendingActions([
        { id: 'LC-PENDING-001', description: 'Awaiting approval', time: '2 hours ago' },
        { id: 'GUA-PENDING-001', description: 'Documents required', time: '4 hours ago' },
        { id: 'LOAN-PENDING-001', description: 'Credit review pending', time: '1 day ago' },
      ])

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`
    }
    return `$${value}`
  }

  const statsData = [
    {
      name: 'Active LCs',
      value: stats.activeLCs.toString(),
      change: stats.lcChange,
      changeType: 'positive',
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      name: 'Bank Guarantees',
      value: stats.guarantees.toString(),
      change: stats.guaranteeChange,
      changeType: 'positive',
      icon: Shield,
      color: 'bg-green-500',
    },
    {
      name: 'Trade Loans',
      value: formatCurrency(stats.loans),
      change: stats.loanChange,
      changeType: 'positive',
      icon: DollarSign,
      color: 'bg-purple-500',
    },
    {
      name: 'Risk Alerts',
      value: stats.riskAlerts.toString(),
      change: stats.riskChange,
      changeType: 'negative',
      icon: AlertTriangle,
      color: 'bg-red-500',
    },
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
        <h1 className="text-2xl font-bold text-secondary-900">Dashboard</h1>
        <p className="text-sm text-secondary-500">
          Welcome back! Here's what's happening today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {statsData.map((stat) => (
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
              {pendingActions.length > 0 ? (
                pendingActions.map((item, index) => (
                  <div key={index} className="flex items-start">
                    <Clock className="h-5 w-5 text-secondary-400 mr-3 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-secondary-900">{item.id}</p>
                      <p className="text-sm text-secondary-500">{item.description}</p>
                    </div>
                    <span className="text-xs text-secondary-400">{item.time}</span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-secondary-500">No pending actions</p>
              )}
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
          {recentTransactions.length > 0 ? (
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
                          tx.status === 'Approved' || tx.status === 'Disbursed' || tx.status === 'approved' || tx.status === 'disbursed'
                            ? 'badge-success'
                            : tx.status === 'Pending' || tx.status === 'Under Review' || tx.status === 'pending' || tx.status === 'draft'
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
          ) : (
            <div className="text-center py-8 text-secondary-500">
              No transactions found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
