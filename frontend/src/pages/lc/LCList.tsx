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
  MoreVertical,
  Eye,
  Edit,
  Send,
  FileText,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  AlertCircle,
  Trash2,
  Check,
  X,
  Loader2,
} from 'lucide-react'
import api from '@/api/axios'

// Types
interface LCItem {
  id: number
  lc_number: string
  lc_type: string
  status: string
  state: string
  applicant_name: string
  beneficiary_name: string
  currency: string
  amount: number
  expiry_date: string | null
  created_at: string
}

interface LCListResponse {
  items: LCItem[]
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
  amended: { color: 'text-indigo-600', bg: 'bg-indigo-100', label: 'Amended' },
  documents_received: { color: 'text-teal-600', bg: 'bg-teal-100', label: 'Docs Received' },
  under_examination: { color: 'text-orange-600', bg: 'bg-orange-100', label: 'Under Exam' },
  payment_processed: { color: 'text-green-600', bg: 'bg-green-100', label: 'Payment Done' },
  accepted: { color: 'text-green-600', bg: 'bg-green-100', label: 'Accepted' },
  closed: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Closed' },
  cancelled: { color: 'text-red-600', bg: 'bg-red-100', label: 'Cancelled' },
}

const LC_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'import', label: 'Import LC' },
  { value: 'export', label: 'Export LC' },
  { value: 'standby', label: 'Standby LC' },
  { value: 'transferable', label: 'Transferable LC' },
  { value: 'back_to_back', label: 'Back-to-Back LC' },
  { value: 'confirmed', label: 'Confirmed LC' },
]

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'under_review', label: 'Under Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'issued', label: 'Issued' },
  { value: 'closed', label: 'Closed' },
]

export default function LCList() {
  const navigate = useNavigate()
  const [lcs, setLcs] = useState<LCItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Pagination
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  
  // Filters
  const [search, setSearch] = useState('')
  const [lcType, setLcType] = useState('')
  const [status, setStatus] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // Action states
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null)
  const [showActionsMenu, setShowActionsMenu] = useState<number | null>(null)

  useEffect(() => {
    fetchLCs()
  }, [page, lcType, status])

  const fetchLCs = async () => {
    setIsLoading(true)
    setError('')
    
    try {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('page_size', '10')
      
      if (search) params.append('search', search)
      if (lcType) params.append('lc_type', lcType)
      if (status) params.append('lc_status', status)
      
      const response = await api.get(`/lc/?${params.toString()}`)
      setLcs(response.data.items)
      setTotal(response.data.total)
      setTotalPages(response.data.total_pages)
    } catch (err: any) {
      console.error('Error fetching LCs:', err)
      setError(err.response?.data?.detail || 'Failed to load Letters of Credit')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchLCs()
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

  const getLcTypeLabel = (type: string) => {
    return LC_TYPES.find(t => t.value === type)?.label || type
  }

  // Action handlers
  const handleEdit = (lcId: number) => {
    navigate(`/lc/${lcId}/edit`)
  }

  const handleDelete = async (lcId: number) => {
    setActionLoading(lcId)
    try {
      await api.delete(`/lc/${lcId}`)
      setShowDeleteConfirm(null)
      fetchLCs() // Refresh the list
    } catch (err: any) {
      console.error('Error deleting LC:', err)
      alert(err.response?.data?.detail || 'Failed to delete Letter of Credit')
    } finally {
      setActionLoading(null)
    }
  }

  const handleSubmit = async (lcId: number) => {
    setActionLoading(lcId)
    try {
      await api.post(`/lc/${lcId}/submit`)
      fetchLCs() // Refresh the list
    } catch (err: any) {
      console.error('Error submitting LC:', err)
      alert(err.response?.data?.detail || 'Failed to submit Letter of Credit')
    } finally {
      setActionLoading(null)
    }
  }

  const handleApprove = async (lcId: number) => {
    setActionLoading(lcId)
    try {
      await api.post(`/lc/${lcId}/approve`)
      fetchLCs() // Refresh the list
    } catch (err: any) {
      console.error('Error approving LC:', err)
      alert(err.response?.data?.detail || 'Failed to approve Letter of Credit')
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (lcId: number) => {
    setActionLoading(lcId)
    try {
      await api.post(`/lc/${lcId}/reject`)
      fetchLCs() // Refresh the list
    } catch (err: any) {
      console.error('Error rejecting LC:', err)
      alert(err.response?.data?.detail || 'Failed to reject Letter of Credit')
    } finally {
      setActionLoading(null)
    }
  }

  const getAvailableActions = (lc: LCItem) => {
    const actions = []
    const currentStatus = lc.status

    // Edit - available for draft status
    if (currentStatus === 'draft') {
      actions.push({ key: 'edit', label: 'Edit', icon: Edit, handler: () => handleEdit(lc.id) })
    }

    // Submit - available for draft status
    if (currentStatus === 'draft') {
      actions.push({ key: 'submit', label: 'Submit', icon: Send, handler: () => handleSubmit(lc.id) })
    }

    // Approve - available for submitted status
    if (currentStatus === 'submitted') {
      actions.push({ key: 'approve', label: 'Approve', icon: Check, handler: () => handleApprove(lc.id) })
    }

    // Reject - available for submitted status
    if (currentStatus === 'submitted') {
      actions.push({ key: 'reject', label: 'Reject', icon: X, handler: () => handleReject(lc.id) })
    }

    // Delete - available for draft status only
    if (currentStatus === 'draft') {
      actions.push({ key: 'delete', label: 'Delete', icon: Trash2, handler: () => setShowDeleteConfirm(lc.id) })
    }

    return actions
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Letter of Credit</h1>
          <p className="text-sm text-secondary-500 mt-1">
            Manage and track all Letters of Credit
          </p>
        </div>
        <Link to="/lc/create" className="btn-primary">
          <Plus className="h-5 w-5 mr-2" />
          Create LC
        </Link>
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
                placeholder="Search by LC number, applicant, or beneficiary..."
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
              onClick={fetchLCs}
              className="btn-outline"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </form>

          {showFilters && (
            <div className="mt-4 pt-4 border-t border-secondary-200 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">LC Type</label>
                <select
                  value={lcType}
                  onChange={(e) => {
                    setLcType(e.target.value)
                    setPage(1)
                  }}
                  className="input"
                >
                  {LC_TYPES.map((type) => (
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
                    setLcType('')
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
          Showing {lcs.length} of {total} Letters of Credit
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
            <p className="mt-2 text-secondary-500">Loading Letters of Credit...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="card border-red-200">
          <div className="card-body text-center py-12">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-secondary-600">{error}</p>
            <button onClick={fetchLCs} className="mt-4 btn-primary">
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* LC Table */}
      {!isLoading && !error && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>LC Number</th>
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
                {lcs.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="text-center py-12">
                      <FileText className="w-12 h-12 text-secondary-300 mx-auto mb-4" />
                      <p className="text-secondary-500">No Letters of Credit found</p>
                      <Link to="/lc/create" className="mt-4 btn-primary inline-block">
                        Create your first LC
                      </Link>
                    </td>
                  </tr>
                ) : (
                  lcs.map((lc) => {
                    const statusConfig = getStatusConfig(lc.status)
                    return (
                      <tr key={lc.id} className="hover:bg-secondary-50">
                        <td>
                          <Link
                            to={`/lc/${lc.id}`}
                            className="font-medium text-primary-600 hover:text-primary-500"
                          >
                            {lc.lc_number}
                          </Link>
                        </td>
                        <td>
                          <span className="badge badge-secondary">
                            {getLcTypeLabel(lc.lc_type)}
                          </span>
                        </td>
                        <td className="max-w-[150px] truncate">
                          <div className="flex items-center">
                            <Building2 className="w-4 h-4 text-secondary-400 mr-2 flex-shrink-0" />
                            <span className="truncate">{lc.applicant_name || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="max-w-[150px] truncate">
                          <div className="flex items-center">
                            <Globe className="w-4 h-4 text-secondary-400 mr-2 flex-shrink-0" />
                            <span className="truncate">{lc.beneficiary_name || 'N/A'}</span>
                          </div>
                        </td>
                        <td className="font-medium">
                          <div className="flex items-center">
                            <DollarSign className="w-4 h-4 text-secondary-400 mr-1" />
                            {formatAmount(Number(lc.amount), lc.currency)}
                          </div>
                        </td>
                        <td>
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 text-secondary-400 mr-2" />
                            {formatDate(lc.expiry_date)}
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${statusConfig.bg} ${statusConfig.color}`}>
                            {statusConfig.label}
                          </span>
                        </td>
                        <td className="text-secondary-500">
                          {formatDate(lc.created_at)}
                        </td>
                        <td>
                          <div className="flex items-center space-x-2">
                            <Link
                              to={`/lc/${lc.id}`}
                              className="p-1 text-secondary-400 hover:text-primary-600"
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </Link>
                            <button
                              onClick={() => handleEdit(lc.id)}
                              className="p-1 text-secondary-400 hover:text-primary-600"
                              title="Edit"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <div className="relative">
                              <button
                                onClick={() => setShowActionsMenu(showActionsMenu === lc.id ? null : lc.id)}
                                className="p-1 text-secondary-400 hover:text-primary-600"
                                title="More Actions"
                              >
                                <MoreVertical className="w-4 h-4" />
                              </button>
                              {showActionsMenu === lc.id && (
                                <div className="absolute right-0 mt-1 w-40 bg-white border border-secondary-200 rounded-md shadow-lg z-10">
                                  {getAvailableActions(lc).map((action) => (
                                    <button
                                      key={action.key}
                                      onClick={() => {
                                        action.handler()
                                        setShowActionsMenu(null)
                                      }}
                                      disabled={actionLoading === lc.id}
                                      className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50 disabled:opacity-50"
                                    >
                                      {actionLoading === lc.id && action.key !== 'edit' ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                      ) : (
                                        <action.icon className="w-4 h-4" />
                                      )}
                                      <span>{action.label}</span>
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>
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
            
            {/* Page Numbers */}
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
              Are you sure you want to delete this Letter of Credit? This action cannot be undone.
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
