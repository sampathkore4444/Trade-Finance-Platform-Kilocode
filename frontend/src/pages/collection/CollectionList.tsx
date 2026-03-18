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
  FileText,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  AlertCircle,
  Clock,
  CheckCircle,
  Trash2,
  Check,
  X,
  Loader2,
  Send,
} from 'lucide-react'
import api from '@/api/axios'

// Types
interface CollectionItem {
  id: number
  collection_number: string
  collection_type: string
  status: string
  drawer_name: string
  drawee_name: string
  currency: string
  amount: number
  maturity_date: string | null
  created_at: string
}

interface CollectionListResponse {
  items: CollectionItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  draft: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Draft' },
  submitted: { color: 'text-blue-600', bg: 'bg-blue-100', label: 'Submitted' },
  sent: { color: 'text-purple-600', bg: 'bg-purple-100', label: 'Sent' },
  accepted: { color: 'text-green-600', bg: 'bg-green-100', label: 'Accepted' },
  paid: { color: 'text-green-600', bg: 'bg-green-100', label: 'Paid' },
  rejected: { color: 'text-red-600', bg: 'bg-red-100', label: 'Rejected' },
  overdue: { color: 'text-orange-600', bg: 'bg-orange-100', label: 'Overdue' },
  returned: { color: 'text-red-600', bg: 'bg-red-100', label: 'Returned' },
  closed: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Closed' },
}

const COLLECTION_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'documents_against_acceptance', label: 'Documents Against Acceptance (DA)' },
  { value: 'documents_against_payment', label: 'Documents Against Payment (DP)' },
]

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'sent', label: 'Sent' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'paid', label: 'Paid' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'overdue', label: 'Overdue' },
]

export default function CollectionList() {
  const navigate = useNavigate()
  const [collections, setCollections] = useState<CollectionItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [collectionType, setCollectionType] = useState('')
  const [status, setStatus] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // Action states
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null)

  useEffect(() => {
    fetchCollections()
  }, [page, collectionType, status])

  const fetchCollections = async () => {
    setIsLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('page_size', '10')
      if (search) params.append('search', search)
      if (collectionType) params.append('collection_type', collectionType)
      if (status) params.append('status', status)
      
      const response = await api.get(`/collection/collections/?${params.toString()}`)
      setCollections(response.data.items)
      setTotal(response.data.total)
      setTotalPages(response.data.total_pages)
    } catch (err: any) {
      console.error('Error fetching collections:', err)
      setError(err.response?.data?.detail || 'Failed to load Documentary Collections')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchCollections()
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency, minimumFractionDigits: 0 }).format(amount)
  }

  const getStatusConfig = (status: string) => {
    return STATUS_CONFIG[status] || { color: 'text-secondary-600', bg: 'bg-secondary-100', label: status }
  }

  // Action handlers
  const handleView = (collectionId: number) => {
    navigate(`/collection/${collectionId}`)
  }

  const handleEdit = (collectionId: number) => {
    navigate(`/collection/${collectionId}`)
  }

  const handleDelete = async (collectionId: number) => {
    setActionLoading(collectionId)
    try {
      await api.delete(`/collection/collections/${collectionId}`)
      setShowDeleteConfirm(null)
      fetchCollections()
    } catch (err: any) {
      console.error('Error deleting Collection:', err)
      alert(err.response?.data?.detail || 'Failed to delete Documentary Collection')
    } finally {
      setActionLoading(null)
    }
  }

  const handleSubmit = async (collectionId: number) => {
    setActionLoading(collectionId)
    try {
      await api.post(`/collection/collections/${collectionId}/submit`)
      fetchCollections()
    } catch (err: any) {
      console.error('Error submitting Collection:', err)
      alert(err.response?.data?.detail || 'Failed to submit Documentary Collection')
    } finally {
      setActionLoading(null)
    }
  }

  const handleApprove = async (collectionId: number) => {
    setActionLoading(collectionId)
    try {
      await api.post(`/collection/collections/${collectionId}/approve`)
      fetchCollections()
    } catch (err: any) {
      console.error('Error approving Collection:', err)
      alert(err.response?.data?.detail || 'Failed to approve Documentary Collection')
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (collectionId: number) => {
    setActionLoading(collectionId)
    try {
      await api.post(`/collection/collections/${collectionId}/reject`)
      fetchCollections()
    } catch (err: any) {
      console.error('Error rejecting Collection:', err)
      alert(err.response?.data?.detail || 'Failed to reject Documentary Collection')
    } finally {
      setActionLoading(null)
    }
  }

  const getAvailableActions = (collection: CollectionItem) => {
    const actions = []
    const currentStatus = collection.status

    // Edit - for draft
    if (currentStatus === 'draft') {
      actions.push({ key: 'edit', label: 'Edit', icon: Edit, handler: () => handleEdit(collection.id) })
    }

    // Submit - for draft
    if (currentStatus === 'draft') {
      actions.push({ key: 'submit', label: 'Submit', icon: Send, handler: () => handleSubmit(collection.id) })
    }

    // View - available for all
    actions.push({ key: 'view', label: 'View', icon: Eye, handler: () => handleView(collection.id) })

    // Approve - for submitted
    if (currentStatus === 'submitted') {
      actions.push({ key: 'approve', label: 'Approve', icon: Check, handler: () => handleApprove(collection.id) })
    }

    // Reject - for submitted
    if (currentStatus === 'submitted') {
      actions.push({ key: 'reject', label: 'Reject', icon: X, handler: () => handleReject(collection.id) })
    }

    // Delete - for draft
    if (currentStatus === 'draft') {
      actions.push({ key: 'delete', label: 'Delete', icon: Trash2, handler: () => setShowDeleteConfirm(collection.id) })
    }

    return actions
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Documentary Collections</h1>
          <p className="text-sm text-secondary-500 mt-1">Manage Documentary Collections (D/A, D/P)</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/collection/new')}>
          <Plus className="h-5 w-5 mr-2" />Create Collection
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
              <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by collection number..." className="input pl-10" />
            </div>
            <button type="button" onClick={() => setShowFilters(!showFilters)} className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'}`}>
              <Filter className="w-4 h-4 mr-2" />Filters
            </button>
            <button type="submit" className="btn-primary"><Search className="w-4 h-4 mr-2" />Search</button>
            <button type="button" onClick={fetchCollections} className="btn-outline"><RefreshCw className="w-4 h-4" /></button>
          </form>
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-secondary-200 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Collection Type</label>
                <select value={collectionType} onChange={(e) => { setCollectionType(e.target.value); setPage(1) }} className="input">
                  {COLLECTION_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Status</label>
                <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }} className="input">
                  {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
              <div className="flex items-end">
                <button onClick={() => { setCollectionType(''); setStatus(''); setSearch(''); setPage(1) }} className="btn-outline w-full">Clear Filters</button>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-secondary-500">Showing {collections.length} of {total} Collections</p>
        <button className="btn-outline flex items-center text-sm"><Download className="w-4 h-4 mr-2" />Export CSV</button>
      </div>

      {isLoading && (
        <div className="card">
          <div className="card-body text-center py-12">
            <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="mt-2 text-secondary-500">Loading Collections...</p>
          </div>
        </div>
      )}

      {error && !isLoading && (
        <div className="card border-red-200">
          <div className="card-body text-center py-12">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-secondary-600">{error}</p>
          </div>
        </div>
      )}

      {!isLoading && !error && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Collection No.</th>
                  <th>Type</th>
                  <th>Drawer</th>
                  <th>Drawee</th>
                  <th>Amount</th>
                  <th>Maturity</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {collections.length === 0 ? (
                  <tr><td colSpan={9} className="text-center py-12"><FileText className="w-12 h-12 text-secondary-300 mx-auto mb-4" /><p className="text-secondary-500">No Collections found</p></td></tr>
                ) : (
                  collections.map((c) => {
                    const statusConfig = getStatusConfig(c.status)
                    return (
                      <tr key={c.id} className="hover:bg-secondary-50">
                        <td className="font-medium text-primary-600">{c.collection_number}</td>
                        <td><span className="badge badge-secondary">{c.collection_type === 'documents_against_acceptance' ? 'D/A' : 'D/P'}</span></td>
                        <td className="max-w-[150px] truncate"><div className="flex items-center"><Building2 className="w-4 h-4 text-secondary-400 mr-2" /><span className="truncate">{c.drawer_name || 'N/A'}</span></div></td>
                        <td className="max-w-[150px] truncate"><div className="flex items-center"><Globe className="w-4 h-4 text-secondary-400 mr-2" /><span className="truncate">{c.drawee_name || 'N/A'}</span></div></td>
                        <td className="font-medium"><div className="flex items-center"><DollarSign className="w-4 h-4 text-secondary-400 mr-1" />{formatAmount(Number(c.amount), c.currency)}</div></td>
                        <td><div className="flex items-center"><Calendar className="w-4 h-4 text-secondary-400 mr-2" />{formatDate(c.maturity_date)}</div></td>
                        <td><span className={`badge ${statusConfig.bg} ${statusConfig.color}`}>{statusConfig.label}</span></td>
                        <td className="text-secondary-500">{formatDate(c.created_at)}</td>
                        <td>
                          <div className="flex items-center space-x-1">
                            {getAvailableActions(c).slice(0, 6).map((action) => (
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

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-secondary-500">Page {page} of {totalPages}</p>
          <div className="flex items-center space-x-2">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-outline btn-sm disabled:opacity-50"><ChevronLeft className="w-4 h-4" /></button>
            <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="btn-outline btn-sm disabled:opacity-50"><ChevronRight className="w-4 h-4" /></button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Confirm Delete</h3>
            <p className="text-secondary-600 mb-6">
              Are you sure you want to delete this Documentary Collection? This action cannot be undone.
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
