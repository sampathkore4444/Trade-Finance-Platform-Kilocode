import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus, Search, Download, RefreshCw, ChevronLeft, ChevronRight, Eye, Edit, DollarSign,
  AlertCircle, Banknote, Building2, Trash2, Check, X, Loader2, Send
} from 'lucide-react'
import api from '@/api/axios'

interface LoanItem {
  id: number
  loan_number: string
  loan_type: string
  status: string
  borrower_name: string
  currency: string
  amount: number
  disbursement_date: string | null
  maturity_date: string | null
  created_at: string
}

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  draft: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Draft' },
  submitted: { color: 'text-blue-600', bg: 'bg-blue-100', label: 'Submitted' },
  approved: { color: 'text-green-600', bg: 'bg-green-100', label: 'Approved' },
  rejected: { color: 'text-red-600', bg: 'bg-red-100', label: 'Rejected' },
  disbursed: { color: 'text-purple-600', bg: 'bg-purple-100', label: 'Disbursed' },
  repaid: { color: 'text-teal-600', bg: 'bg-teal-100', label: 'Repaid' },
  overdue: { color: 'text-orange-600', bg: 'bg-orange-100', label: 'Overdue' },
  defaulted: { color: 'text-red-600', bg: 'bg-red-100', label: 'Defaulted' },
  closed: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Closed' },
}

export default function LoanList() {
  const navigate = useNavigate()
  const [loans, setLoans] = useState<LoanItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')

  // Action states
  const [actionLoading, setActionLoading] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [selectedLoan, setSelectedLoan] = useState<LoanItem | null>(null)
  const [showActionModal, setShowActionModal] = useState(false)
  const [actionType, setActionType] = useState<string>('')
  const [actionReason, setActionReason] = useState('')

  useEffect(() => { fetchLoans() }, [page, status])

  const fetchLoans = async () => {
    setIsLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('page_size', '10')
      if (search) params.append('search', search)
      if (status) params.append('status', status)
      const response = await api.get(`/loan/loans/?${params.toString()}`)
      setLoans(response.data.items)
      setTotal(response.data.total)
      setTotalPages(response.data.total_pages)
    } catch (err: any) {
      console.error('Error fetching loans:', err)
      setError(err.response?.data?.detail || 'Failed to load Trade Loans')
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (d: string | null) => d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A'
  const formatAmount = (a: number, c: string) => new Intl.NumberFormat('en-US', { style: 'currency', currency: c, minimumFractionDigits: 0 }).format(a)
  const getStatusConfig = (s: string) => STATUS_CONFIG[s] || { color: 'text-secondary-600', bg: 'bg-secondary-100', label: s }

  // Action handlers
  const handleDelete = async () => {
    if (!selectedLoan) return
    setActionLoading(true)
    try {
      await api.delete(`/loan/loans/${selectedLoan.id}`)
      setShowDeleteConfirm(false)
      setSelectedLoan(null)
      fetchLoans()
    } catch (err: any) {
      console.error('Error deleting Loan:', err)
      alert(err.response?.data?.detail || 'Failed to delete Trade Loan')
    } finally {
      setActionLoading(false)
    }
  }

  const handleAction = async () => {
    if (!selectedLoan || !actionType) return
    setActionLoading(true)
    try {
      const endpoint = `/loan/loans/${selectedLoan.id}/${actionType}`
      if (actionType === 'reject') {
        await api.post(endpoint, { reason: actionReason })
      } else {
        await api.post(endpoint)
      }
      setShowActionModal(false)
      setSelectedLoan(null)
      setActionType('')
      setActionReason('')
      fetchLoans()
    } catch (err: any) {
      console.error('Error performing action:', err)
      alert(err.response?.data?.detail || `Failed to ${actionType}`)
    } finally {
      setActionLoading(false)
    }
  }

  const openActionModal = (loan: LoanItem, action: string) => {
    setSelectedLoan(loan)
    setActionType(action)
    setShowActionModal(true)
  }

  const getAvailableActions = (loan: LoanItem) => {
    const actions = []
    const currentStatus = loan.status

    if (currentStatus === 'draft') {
      actions.push({ key: 'edit', label: 'Edit', icon: Edit, handler: () => navigate(`/loan/${loan.id}`) })
    }

    if (currentStatus === 'draft') {
      actions.push({ key: 'submit', label: 'Submit', icon: Send, handler: () => openActionModal(loan, 'submit') })
    }

    // View - available for all
    actions.push({ key: 'view', label: 'View Details', icon: Eye, handler: () => navigate(`/loan/${loan.id}`) })

    if (currentStatus === 'submitted') {
      actions.push({ key: 'approve', label: 'Approve', icon: Check, handler: () => openActionModal(loan, 'approve') })
    }

    if (currentStatus === 'submitted') {
      actions.push({ key: 'reject', label: 'Reject', icon: X, handler: () => openActionModal(loan, 'reject') })
    }

    if (currentStatus === 'draft') {
      actions.push({ key: 'delete', label: 'Delete', icon: Trash2, handler: () => { setSelectedLoan(loan); setShowDeleteConfirm(true) } })
    }

    return actions
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Trade Loans</h1>
          <p className="text-sm text-secondary-500 mt-1">Manage Trade Finance Loans</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/loan/new')}><Plus className="h-5 w-5 mr-2" />Create Loan</button>
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={(e) => { e.preventDefault(); setPage(1); fetchLoans() }} className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
              <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search loans..." className="input pl-10" />
            </div>
            <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }} className="input w-auto">
              <option value="">All Status</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
            </select>
            <button type="submit" className="btn-primary"><Search className="w-4 h-4 mr-2" />Search</button>
            <button type="button" onClick={fetchLoans} className="btn-outline"><RefreshCw className="w-4 h-4" /></button>
          </form>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-secondary-500">Showing {loans.length} of {total} Loans</p>
        <button className="btn-outline text-sm"><Download className="w-4 h-4 mr-2" />Export</button>
      </div>

      {isLoading && <div className="card"><div className="card-body text-center py-12"><div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" /></div></div>}
      {error && !isLoading && <div className="card border-red-200"><div className="card-body text-center py-12"><AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" /><p>{error}</p></div></div>}

      {!isLoading && !error && (
        <div className="card overflow-hidden">
          <table className="table">
            <thead><tr><th>Loan No.</th><th>Type</th><th>Borrower</th><th>Amount</th><th>Disbursed</th><th>Maturity</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {loans.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-12"><Banknote className="w-12 h-12 text-secondary-300 mx-auto mb-4" /><p className="text-secondary-500">No Loans found</p></td></tr>
              ) : loans.map((loan) => (
                <tr key={loan.id} className="hover:bg-secondary-50">
                  <td className="font-medium text-primary-600">{loan.loan_number}</td>
                  <td><span className="badge badge-secondary">{loan.loan_type}</span></td>
                  <td><div className="flex items-center"><Building2 className="w-4 h-4 text-secondary-400 mr-2" />{loan.borrower_name || 'N/A'}</div></td>
                  <td className="font-medium"><DollarSign className="w-4 h-4 inline mr-1" />{formatAmount(Number(loan.amount), loan.currency)}</td>
                  <td>{formatDate(loan.disbursement_date)}</td>
                  <td>{formatDate(loan.maturity_date)}</td>
                  <td><span className={`badge ${getStatusConfig(loan.status).bg} ${getStatusConfig(loan.status).color}`}>{getStatusConfig(loan.status).label}</span></td>
                  <td>
                    <div className="flex items-center space-x-1">
                      {getAvailableActions(loan).slice(0, 6).map((action) => (
                        <button
                          key={action.key}
                          onClick={action.handler}
                          className="p-1 text-secondary-400 hover:text-primary-600"
                          title={action.label}
                        >
                          <action.icon className="w-4 h-4" />
                        </button>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-secondary-500">Page {page} of {totalPages}</p>
          <div className="flex space-x-2">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-outline btn-sm disabled:opacity-50"><ChevronLeft className="w-4 h-4" /></button>
            <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="btn-outline btn-sm disabled:opacity-50"><ChevronRight className="w-4 h-4" /></button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mr-4">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-secondary-900">Confirm Delete</h3>
                <p className="text-secondary-500 text-sm">This action cannot be undone.</p>
              </div>
            </div>
            <p className="text-secondary-600 mb-6">Are you sure you want to delete this Trade Loan? This will permanently remove the record from the system.</p>
            <div className="flex justify-end space-x-3">
              <button onClick={() => { setShowDeleteConfirm(false); setSelectedLoan(null) }} className="btn-outline" disabled={actionLoading}>Cancel</button>
              <button onClick={handleDelete} className="btn-danger" disabled={actionLoading}>
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Trash2 className="w-4 h-4 mr-2" />}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Action Modal */}
      {showActionModal && selectedLoan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">
              {actionType === 'submit' && 'Submit Loan for Approval'}
              {actionType === 'approve' && 'Approve Loan'}
              {actionType === 'reject' && 'Reject Loan'}
            </h3>
            
            {actionType === 'reject' && (
              <div className="mb-4">
                <label className="label">Reason</label>
                <textarea
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  className="input"
                  rows={3}
                  placeholder="Enter reason for rejection..."
                  required
                />
              </div>
            )}

            <div className="flex justify-end gap-3">
              <button
                onClick={() => { setShowActionModal(false); setSelectedLoan(null); setActionType(''); setActionReason('') }}
                className="btn-secondary"
                disabled={actionLoading}
              >
                Cancel
              </button>
              <button
                onClick={handleAction}
                className={`btn ${actionType === 'reject' ? 'btn-danger' : 'btn-primary'}`}
                disabled={actionLoading || (actionType === 'reject' && !actionReason)}
              >
                {actionLoading ? 'Processing...' : 
                  actionType === 'submit' ? 'Submit' :
                  actionType === 'approve' ? 'Approve' :
                  actionType === 'reject' ? 'Reject' : 'Confirm'
                }
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
