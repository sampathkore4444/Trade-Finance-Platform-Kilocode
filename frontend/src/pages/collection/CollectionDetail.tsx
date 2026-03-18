import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Save, Send, Check, X, Trash2, Edit, FileText,
  Building2, Calendar, User, Clock, AlertCircle, Loader2
} from 'lucide-react'
import api from '@/api/axios'

interface CollectionDetail {
  id: string
  collection_number: string
  collection_type: string
  status: string
  applicant_name: string
  applicant_address: string
  applicant_country: string
  beneficiary_name: string
  beneficiary_address: string
  beneficiary_country: string
  remitting_bank_name: string
  remitting_bank_bic: string
  collecting_bank_name: string
  collecting_bank_bic: string
  presenting_bank_name: string
  presenting_bank_bic: string
  currency: string
  amount: number
  issue_date: string | null
  due_date: string | null
  documents_description: string
  invoice_number: string
  internal_reference: string
  created_at: string
  updated_at: string | null
}

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  draft: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Draft' },
  submitted: { color: 'text-blue-600', bg: 'bg-blue-100', label: 'Submitted' },
  approved: { color: 'text-green-600', bg: 'bg-green-100', label: 'Approved' },
  rejected: { color: 'text-red-600', bg: 'bg-red-100', label: 'Rejected' },
  accepted: { color: 'text-purple-600', bg: 'bg-purple-100', label: 'Accepted' },
  paid: { color: 'text-green-600', bg: 'bg-green-100', label: 'Paid' },
  cancelled: { color: 'text-red-600', bg: 'bg-red-100', label: 'Cancelled' },
}

export default function CollectionDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [collection, setCollection] = useState<CollectionDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionType, setActionType] = useState<string>('')
  const [showActionModal, setShowActionModal] = useState(false)
  const [actionReason, setActionReason] = useState('')

  // Form state for editing
  const [formData, setFormData] = useState({
    applicant_name: '',
    applicant_address: '',
    applicant_country: '',
    beneficiary_name: '',
    beneficiary_address: '',
    beneficiary_country: '',
    remitting_bank_name: '',
    remitting_bank_bic: '',
    collecting_bank_name: '',
    collecting_bank_bic: '',
    presenting_bank_name: '',
    presenting_bank_bic: '',
    amount: '',
    currency: 'USD',
    due_date: '',
    documents_description: '',
    invoice_number: '',
    internal_reference: '',
  })

  useEffect(() => {
    if (id) fetchCollection()
  }, [id])

  const fetchCollection = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await api.get(`/collection/collections/${Number(id)}`)
      setCollection(response.data)
      setFormData({
        applicant_name: response.data.applicant_name || '',
        applicant_address: response.data.applicant_address || '',
        applicant_country: response.data.applicant_country || '',
        beneficiary_name: response.data.beneficiary_name || '',
        beneficiary_address: response.data.beneficiary_address || '',
        beneficiary_country: response.data.beneficiary_country || '',
        remitting_bank_name: response.data.remitting_bank_name || '',
        remitting_bank_bic: response.data.remitting_bank_bic || '',
        collecting_bank_name: response.data.collecting_bank_name || '',
        collecting_bank_bic: response.data.collecting_bank_bic || '',
        presenting_bank_name: response.data.presenting_bank_name || '',
        presenting_bank_bic: response.data.presenting_bank_bic || '',
        amount: response.data.amount?.toString() || '',
        currency: response.data.currency || 'USD',
        due_date: response.data.due_date ? response.data.due_date.split('T')[0] : '',
        documents_description: response.data.documents_description || '',
        invoice_number: response.data.invoice_number || '',
        internal_reference: response.data.internal_reference || '',
      })
    } catch (err: any) {
      console.error('Error fetching collection:', err)
      setError(err.response?.data?.detail || 'Failed to load collection')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async () => {
    if (!collection) return
    setActionLoading(true)
    try {
      await api.put(`/collection/collections/${Number(collection.id)}`, formData)
      setIsEditing(false)
      fetchCollection()
    } catch (err: any) {
      console.error('Error updating collection:', err)
      setError(err.response?.data?.detail || 'Failed to update collection')
    } finally {
      setActionLoading(false)
    }
  }

  const handleAction = async () => {
    if (!collection || !actionType) return
    setActionLoading(true)
    try {
      const endpoint = `/collection/collections/${Number(collection.id)}/${actionType}`
      if (actionType === 'reject' || actionType === 'cancel') {
        await api.post(endpoint, { reason: actionReason })
      } else {
        await api.post(endpoint)
      }
      setShowActionModal(false)
      setActionType('')
      setActionReason('')
      fetchCollection()
    } catch (err: any) {
      console.error('Error performing action:', err)
      setError(err.response?.data?.detail || `Failed to ${actionType}`)
    } finally {
      setActionLoading(false)
    }
  }

  const openActionModal = (action: string) => {
    setActionType(action)
    setShowActionModal(true)
  }

  const getStatusConfig = (status: string) => STATUS_CONFIG[status] || { color: 'text-secondary-600', bg: 'bg-secondary-100', label: status }

  const formatDate = (date: string | null) => date ? new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A'

  const formatAmount = (amount: number, currency: string) => new Intl.NumberFormat('en-US', { style: 'currency', currency, minimumFractionDigits: 0 }).format(amount)

  const getAvailableActions = () => {
    if (!collection) return []
    const actions: { key: string; label: string; icon: any; variant: string; handler: () => void }[] = []
    const currentStatus = collection.status

    if (currentStatus === 'draft') {
      actions.push(
        { key: 'edit', label: 'Edit', icon: Edit, variant: 'secondary', handler: () => setIsEditing(true) },
        { key: 'submit', label: 'Submit', icon: Send, variant: 'primary', handler: () => openActionModal('submit') },
        { key: 'cancel', label: 'Cancel', icon: Trash2, variant: 'danger', handler: () => openActionModal('cancel') }
      )
    } else if (currentStatus === 'submitted') {
      actions.push(
        { key: 'approve', label: 'Approve', icon: Check, variant: 'primary', handler: () => openActionModal('approve') },
        { key: 'reject', label: 'Reject', icon: X, variant: 'danger', handler: () => openActionModal('reject') },
        { key: 'cancel', label: 'Cancel', icon: Trash2, variant: 'danger', handler: () => openActionModal('cancel') }
      )
    } else if (currentStatus === 'approved') {
      actions.push(
        { key: 'process', label: 'Process', icon: Check, variant: 'primary', handler: () => openActionModal('process') }
      )
    } else if (currentStatus === 'accepted') {
      actions.push(
        { key: 'complete', label: 'Complete', icon: Check, variant: 'primary', handler: () => openActionModal('complete') }
      )
    }

    return actions
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error && !collection) {
    return (
      <div className="card border-red-200">
        <div className="card-body text-center py-12">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">{error}</p>
          <button onClick={() => navigate('/collection')} className="btn-secondary mt-4">
            Back to List
          </button>
        </div>
      </div>
    )
  }

  if (!collection) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/collection')} className="btn-secondary p-2">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">Collection {collection.collection_number}</h1>
            <p className="text-sm text-secondary-500 mt-1">Documentary Collection Details</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`badge ${getStatusConfig(collection.status).bg} ${getStatusConfig(collection.status).color}`}>
            {getStatusConfig(collection.status).label}
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      {!isEditing && (
        <div className="flex gap-2">
          {getAvailableActions().map((action) => (
            <button
              key={action.key}
              onClick={action.handler}
              className={`btn ${action.variant === 'danger' ? 'btn-danger' : action.variant === 'primary' ? 'btn-primary' : 'btn-secondary'}`}
            >
              <action.icon className="w-4 h-4 mr-2" />
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Collection Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold">Collection Information</h2>
            </div>
            <div className="card-body">
              {isEditing ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Applicant Name</label>
                    <input
                      type="text"
                      value={formData.applicant_name}
                      onChange={(e) => setFormData({ ...formData, applicant_name: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label">Beneficiary Name</label>
                    <input
                      type="text"
                      value={formData.beneficiary_name}
                      onChange={(e) => setFormData({ ...formData, beneficiary_name: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label">Amount</label>
                    <input
                      type="number"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label">Currency</label>
                    <select
                      value={formData.currency}
                      onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                      className="input"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Due Date</label>
                    <input
                      type="date"
                      value={formData.due_date}
                      onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label">Internal Reference</label>
                    <input
                      type="text"
                      value={formData.internal_reference}
                      onChange={(e) => setFormData({ ...formData, internal_reference: e.target.value })}
                      className="input"
                    />
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Applicant (Drawer/Seller)</p>
                      <p className="font-medium">{collection.applicant_name || 'N/A'}</p>
                      <p className="text-sm text-secondary-500">{collection.applicant_country || ''}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Beneficiary (Drawee/Buyer)</p>
                      <p className="font-medium">{collection.beneficiary_name || 'N/A'}</p>
                      <p className="text-sm text-secondary-500">{collection.beneficiary_country || ''}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Building2 className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Remitting Bank</p>
                      <p className="font-medium">{collection.remitting_bank_name || 'N/A'}</p>
                      <p className="text-sm text-secondary-500">{collection.remitting_bank_bic || ''}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Building2 className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Collecting Bank</p>
                      <p className="font-medium">{collection.collecting_bank_name || 'N/A'}</p>
                      <p className="text-sm text-secondary-500">{collection.collecting_bank_bic || ''}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Issue Date</p>
                      <p className="font-medium">{formatDate(collection.issue_date)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Due Date</p>
                      <p className="font-medium">{formatDate(collection.due_date)}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Amount Card */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold">Financial Details</h2>
            </div>
            <div className="card-body space-y-4">
              <div>
                <p className="text-sm text-secondary-500">Collection Amount</p>
                <p className="text-2xl font-bold text-primary-600">
                  {formatAmount(collection.amount, collection.currency)}
                </p>
              </div>
              <div>
                <p className="text-sm text-secondary-500">Collection Type</p>
                <p className="font-medium">{collection.collection_type === 'da_dp' ? 'D/P' : 'D/A'}</p>
              </div>
            </div>
          </div>

          {/* Timeline Card */}
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold">Timeline</h2>
            </div>
            <div className="card-body space-y-3">
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4 text-secondary-400" />
                <div>
                  <p className="text-sm text-secondary-500">Created</p>
                  <p className="text-sm">{formatDate(collection.created_at)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Mode Footer */}
      {isEditing && (
        <div className="flex justify-end gap-2">
          <button onClick={() => setIsEditing(false)} className="btn-secondary">Cancel</button>
          <button onClick={handleSave} disabled={actionLoading} className="btn-primary">
            {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
            Save Changes
          </button>
        </div>
      )}

      {/* Action Modal */}
      {showActionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">
              {actionType === 'submit' && 'Submit Collection for Approval'}
              {actionType === 'approve' && 'Approve Collection'}
              {actionType === 'reject' && 'Reject Collection'}
              {actionType === 'process' && 'Process Collection'}
              {actionType === 'complete' && 'Complete Collection'}
              {actionType === 'cancel' && 'Cancel Collection'}
            </h3>
            
            {(actionType === 'reject' || actionType === 'cancel') && (
              <div className="mb-4">
                <label className="label">Reason</label>
                <textarea
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  className="input"
                  rows={3}
                  placeholder={`Enter reason for ${actionType}...`}
                  required
                />
              </div>
            )}

            <div className="flex justify-end gap-3">
              <button
                onClick={() => { setShowActionModal(false); setActionType(''); setActionReason('') }}
                className="btn-secondary"
                disabled={actionLoading}
              >
                Cancel
              </button>
              <button
                onClick={handleAction}
                className={`btn ${actionType === 'reject' || actionType === 'cancel' ? 'btn-danger' : 'btn-primary'}`}
                disabled={actionLoading || ((actionType === 'reject' || actionType === 'cancel') && !actionReason)}
              >
                {actionLoading ? 'Processing...' : 
                  actionType === 'submit' ? 'Submit' :
                  actionType === 'approve' ? 'Approve' :
                  actionType === 'reject' ? 'Reject' :
                  actionType === 'process' ? 'Process' :
                  actionType === 'complete' ? 'Complete' :
                  actionType === 'cancel' ? 'Cancel' : 'Confirm'
                }
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
