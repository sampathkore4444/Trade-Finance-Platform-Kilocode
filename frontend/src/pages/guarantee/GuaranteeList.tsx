import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Plus,
  Search,
  Filter,
  Download,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Eye,
  Edit,
  Shield,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  AlertCircle,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Trash2,
  Check,
  X,
  Loader2,
  Send,
} from 'lucide-react'
import api from '@/api/axios'

// Types
interface GuaranteeItem {
  id: number
  guarantee_number: string
  guarantee_type: string
  status: string
  state: string
  applicant_name: string
  beneficiary_name: string
  currency: string
  amount: number
  expiry_date: string | null
  created_at: string
}

interface GuaranteeListResponse {
  items: GuaranteeItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  draft: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Draft' },
  submitted: { color: 'text-blue-600', bg: 'bg-blue-100', label: 'Submitted' },
  under_review: { color: 'text-yellow-600', bg: 'bg-yellow-100', label: 'Under Review' },
  approved: { color: 'text-green-600', bg: 'bg-green-100', label: 'Approved' },
  rejected: { color: 'text-red-600', bg: 'bg-red-100', label: 'Rejected' },
  issued: { color: 'text-purple-600', bg: 'bg-purple-100', label: 'Issued' },
  active: { color: 'text-green-600', bg: 'bg-green-100', label: 'Active' },
  expired: { color: 'text-orange-600', bg: 'bg-orange-100', label: 'Expired' },
  claimed: { color: 'text-red-600', bg: 'bg-red-100', label: 'Claimed' },
  released: { color: 'text-teal-600', bg: 'bg-teal-100', label: 'Released' },
  cancelled: { color: 'text-red-600', bg: 'bg-red-100', label: 'Cancelled' },
}

const GUARANTEE_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'bid_bond', label: 'Bid Bond' },
  { value: 'performance_bond', label: 'Performance Bond' },
  { value: 'advance_payment_guarantee', label: 'Advance Payment Guarantee' },
  { value: 'payment_guarantee', label: 'Payment Guarantee' },
  { value: 'warranty_guarantee', label: 'Warranty Guarantee' },
  { value: 'customs_guarantee', label: 'Customs Guarantee' },
  { value: 'judicial_guarantee', label: 'Judicial Guarantee' },
  { value: 'financial_guarantee', label: 'Financial Guarantee' },
]

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'under_review', label: 'Under Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'issued', label: 'Issued' },
  { value: 'active', label: 'Active' },
  { value: 'expired', label: 'Expired' },
  { value: 'claimed', label: 'Claimed' },
  { value: 'released', label: 'Released' },
]

export default function GuaranteeList() {
  const navigate = useNavigate()
  const [guarantees, setGuarantees] = useState<GuaranteeItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Pagination
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  
  // Filters
  const [search, setSearch] = useState('')
  const [guaranteeType, setGuaranteeType] = useState('')
  const [status, setStatus] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // Action states
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null)

  useEffect(() => {
    fetchGuarantees()
  }, [page, guaranteeType, status])

  const fetchGuarantees = async () => {
    setIsLoading(true)
    setError('')
    
    try {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('page_size', '10')
      
      if (search) params.append('search', search)
      if (guaranteeType) params.append('guarantee_type', guaranteeType)
      if (status) params.append('status', status)
      
      const response = await api.get(`/guarantee/?${params.toString()}`)
      setGuarantees(response.data.items)
      setTotal(response.data.total)
      setTotalPages(response.data.total_pages)
    } catch (err: any) {
      console.error('Error fetching guarantees:', err)
      setError(err.response?.data?.detail || 'Failed to load Bank Guarantees')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchGuarantees()
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const getStatusConfig = (status: string) => {
    return STATUS_CONFIG[status] || { color: 'text-secondary-600', bg: 'bg-secondary-100', label: status }
  }

  const getGuaranteeTypeLabel = (type: string) => {
    return GUARANTEE_TYPES.find(t => t.value === type)?.label || type
  }

  // Action handlers
  const handleView = (guaranteeId: number) => {
    navigate(`/guarantee/${guaranteeId}`)
  }

  const handleEdit = (guaranteeId: number) => {
    navigate(`/guarantee/${guaranteeId}`)
  }

  const handleDelete = async (guaranteeId: number) => {
    setActionLoading(guaranteeId)
    try {
      await api.delete(`/guarantee/${guaranteeId}`)
      setShowDeleteConfirm(null)
      fetchGuarantees()
    } catch (err: any) {
      console.error('Error deleting Guarantee:', err)
      alert(err.response?.data?.detail || 'Failed to delete Bank Guarantee')
    } finally {
      setActionLoading(null)
    }
  }

  const handleSubmit = async (guaranteeId: number) => {
    setActionLoading(guaranteeId)
    try {
      await api.post(`/guarantee/${guaranteeId}/submit`)
      fetchGuarantees()
    } catch (err: any) {
      console.error('Error submitting Guarantee:', err)
      alert(err.response?.data?.detail || 'Failed to submit Bank Guarantee')
    } finally {
      setActionLoading(null)
    }
  }

  const handleApprove = async (guaranteeId: number) => {
    setActionLoading(guaranteeId)
    try {
      await api.post(`/guarantee/${guaranteeId}/approve`)
      fetchGuarantees()
    } catch (err: any) {
      console.error('Error approving Guarantee:', err)
      alert(err.response?.data?.detail || 'Failed to approve Bank Guarantee')
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (guaranteeId: number) => {
    setActionLoading(guaranteeId)
    try {
      await api.post(`/guarantee/${guaranteeId}/reject`)
      fetchGuarantees()
    } catch (err: any) {
      console.error('Error rejecting Guarantee:', err)
      alert(err.response?.data?.detail || 'Failed to reject Bank Guarantee')
    } finally {
      setActionLoading(null)
    }
  }

  const getAvailableActions = (guarantee: GuaranteeItem) => {
    const actions = []
    const currentStatus = guarantee.status

    // Edit - for draft
    if (currentStatus === 'draft') {
      actions.push({ key: 'edit', label: 'Edit', icon: Edit, handler: () => handleEdit(guarantee.id) })
    }

    // Submit - for draft
    if (currentStatus === 'draft') {
      actions.push({ key: 'submit', label: 'Submit', icon: Send, handler: () => handleSubmit(guarantee.id) })
    }

    // View - available for all
    actions.push({ key: 'view', label: 'View', icon: Eye, handler: () => handleView(guarantee.id) })

    // Approve - for submitted
    if (currentStatus === 'submitted') {
      actions.push({ key: 'approve', label: 'Approve', icon: Check, handler: () => handleApprove(guarantee.id) })
    }

    // Reject - for submitted
    if (currentStatus === 'submitted') {
      actions.push({ key: 'reject', label: 'Reject', icon: X, handler: () => handleReject(guarantee.id) })
    }

    // Delete - for draft
    if (currentStatus === 'draft') {
      actions.push({ key: 'delete', label: 'Delete', icon: Trash2, handler: () => setShowDeleteConfirm(guarantee.id) })
    }

    return actions
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Bank Guarantees</h1>
          <p className="text-sm text-secondary-500 mt-1">
            Manage and track all Bank Guarantees
          </p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/guarantee/new')}>
          <Plus className="h-5 w-5 mr-2" />
          Create Guarantee
        </button>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by guarantee number, applicant, or beneficiary..."
                className="input pl-10"
              />
            </div>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'}`}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>
            <button type="submit" className="btn-primary">
              <Search className="w-4 h-4 mr-2" />
              Search
            </button>
            <button
              type="button"
              onClick={fetchGuarantees}
              className="btn-outline"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </form>

          {showFilters && (
            <div className="mt-4 pt-4 border-t border-secondary-200 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Guarantee Type</label>
                <select
                  value={guaranteeType}
                  onChange={(e) => {
                    setGuaranteeType(e.target.value)
                    setPage(1)
                  }}
                  className="input"
                >
                  {GUARANTEE_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Status</label>
                <select
                  value={status}
                  onChange={(e) => {
                    setStatus(e.target.value)
                    setPage(1)
                  }}
                  className="input"
                >
                  {STATUS_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => {
                    setGuaranteeType('')
                    setStatus('')
                    setSearch('')
                    setPage(1)
                  }}
                  className="btn-outline w-full"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-secondary-500">
          Showing {guarantees.length} of {total} Bank Guarantees
        </p>
        <button className="btn-outline flex items-center text-sm">
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="card">
          <div className="card-body text-center py-12">
            <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="mt-2 text-secondary-500">Loading Bank Guarantees...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="card border-red-200">
          <div className="card-body text-center py-12">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-secondary-600">{error}</p>
            <button onClick={fetchGuarantees} className="mt-4 btn-primary">
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Guarantee Table */}
      {!isLoading && !error && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Guarantee Number</th>
                  <th>Type</th>
                  <th>Applicant</th>
                  <th>Beneficiary</th>
                  <th>Amount</th>
                  <th>Expiry Date</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {guarantees.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="text-center py-12">
                      <Shield className="w-12 h-12 text-secondary-300 mx-auto mb-4" />
                      <p className="text-secondary-500">No Bank Guarantees found</p>
                      <button className="mt-4 btn-primary inline-block">
                        Create your first Guarantee
                      </button>
                    </td>
                  </tr>
                ) : (
                  guarantees.map((guarantee) => {
                    const statusConfig = getStatusConfig(guarantee.status)
                    return (
                      <tr key={guarantee.id} className="hover:bg-secondary-50">
                        <td>
                          <button
                            onClick={() => handleView(guarantee.id)}
                            className="font-medium text-primary-600 hover:underline"
                          >
                            {guarantee.guarantee_number}
                          </button>
                        </td>
                        <td>
                          <span className="badge badge-secondary">
                            {getGuaranteeTypeLabel(guarantee.guarantee_type)}
                          </span>
                        </td>
                        <td className="max-w-[150px] truncate">
                          <div className="flex items-center">
                            <Building2 className="w-4 h-4 text-secondary-400 mr-2 flex-shrink-0" />
                            <span className="truncate">{guarantee.applicant_name || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="max-w-[150px] truncate">
                          <div className="flex items-center">
                            <Globe className="w-4 h-4 text-secondary-400 mr-2 flex-shrink-0" />
                            <span className="truncate">{guarantee.beneficiary_name || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="font-medium">
                          <div className="flex items-center">
                            <DollarSign className="w-4 h-4 text-secondary-400 mr-1" />
                            {formatAmount(Number(guarantee.amount), guarantee.currency)}
                          </div>
                        </td>
                        <td>
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 text-secondary-400 mr-2" />
                            {formatDate(guarantee.expiry_date)}
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${statusConfig.bg} ${statusConfig.color}`}>
                            {statusConfig.label}
                          </span>
                        </td>
                        <td className="text-secondary-500">
                          {formatDate(guarantee.created_at)}
                        </td>
                        <td>
                          <div className="flex items-center space-x-1">
                            {getAvailableActions(guarantee).slice(0, 6).map((action) => (
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
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-secondary-500">
            Page {page} of {totalPages}
          </p>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="btn-outline btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum: number
              if (totalPages <= 5) {
                pageNum = i + 1
              } else if (page <= 3) {
                pageNum = i + 1
              } else if (page >= totalPages - 2) {
                pageNum = totalPages - 4 + i
              } else {
                pageNum = page - 2 + i
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`w-8 h-8 rounded text-sm ${
                    page === pageNum
                      ? 'bg-primary-600 text-white'
                      : 'btn-outline hover:bg-secondary-100'
                  }`}
                >
                  {pageNum}
                </button>
              )
            })}
            
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="btn-outline btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Confirm Delete</h3>
            <p className="text-secondary-600 mb-6">
              Are you sure you want to delete this Bank Guarantee? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="btn-outline"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(showDeleteConfirm)}
                disabled={actionLoading === showDeleteConfirm}
                className="btn-danger"
              >
                {actionLoading === showDeleteConfirm ? (
                  <span className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Deleting...</span>
                  </span>
                ) : (
                  'Delete'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
