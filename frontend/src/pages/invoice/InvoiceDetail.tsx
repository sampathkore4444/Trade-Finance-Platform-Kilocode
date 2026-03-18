import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Save, Send, Check, X, DollarSign, Trash2, Edit, FileText,
  Building2, Calendar, User, Clock, AlertCircle, Loader2
} from 'lucide-react'
import api from '@/api/axios'

interface InvoiceDetail {
  id: number
  invoice_number: string
  invoice_type: string
  invoice_status: string
  financing_status: string
  seller_name: string
  seller_address: string
  buyer_name: string
  buyer_address: string
  currency: string
  invoice_amount: number
  financed_amount: number | null
  outstanding_amount: number | null
  due_date: string | null
  invoice_date: string | null
  financing_start_date: string | null
  financing_end_date: string | null
  repaid_amount: number | null
  payment_date: string | null
  payment_amount: number | null
  internal_reference: string | null
  created_at: string
  updated_at: string | null
}

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  draft: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Draft' },
  submitted: { color: 'text-blue-600', bg: 'bg-blue-100', label: 'Submitted' },
  approved: { color: 'text-green-600', bg: 'bg-green-100', label: 'Approved' },
  rejected: { color: 'text-red-600', bg: 'bg-red-100', label: 'Rejected' },
  financed: { color: 'text-purple-600', bg: 'bg-purple-100', label: 'Financed' },
  repaid: { color: 'text-teal-600', bg: 'bg-teal-100', label: 'Repaid' },
  paid: { color: 'text-green-600', bg: 'bg-green-100', label: 'Paid' },
  cancelled: { color: 'text-red-600', bg: 'bg-red-100', label: 'Cancelled' },
}

export default function InvoiceDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionType, setActionType] = useState<string>('')
  const [showActionModal, setShowActionModal] = useState(false)
  const [actionReason, setActionReason] = useState('')

  // Form state for editing
  const [formData, setFormData] = useState({
    seller_name: '',
    seller_address: '',
    buyer_name: '',
    buyer_address: '',
    invoice_amount: '',
    currency: 'USD',
    due_date: '',
    internal_reference: '',
  })

  useEffect(() => {
    if (id) fetchInvoice()
  }, [id])

  const fetchInvoice = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await api.get(`/invoice/invoices/${id}`)
      setInvoice(response.data)
      setFormData({
        seller_name: response.data.seller_name || '',
        seller_address: response.data.seller_address || '',
        buyer_name: response.data.buyer_name || '',
        buyer_address: response.data.buyer_address || '',
        invoice_amount: response.data.invoice_amount?.toString() || '',
        currency: response.data.currency || 'USD',
        due_date: response.data.due_date ? response.data.due_date.split('T')[0] : '',
        internal_reference: response.data.internal_reference || '',
      })
    } catch (err: any) {
      console.error('Error fetching invoice:', err)
      setError(err.response?.data?.detail || 'Failed to load invoice')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async () => {
    if (!invoice) return
    setActionLoading(true)
    try {
      await api.put(`/invoice/invoices/${invoice.id}`, formData)
      setIsEditing(false)
      fetchInvoice()
    } catch (err: any) {
      console.error('Error updating invoice:', err)
      setError(err.response?.data?.detail || 'Failed to update invoice')
    } finally {
      setActionLoading(false)
    }
  }

  const handleAction = async () => {
    if (!invoice || !actionType) return
    setActionLoading(true)
    try {
      const endpoint = `/invoice/invoices/${invoice.id}/${actionType}`
      if (actionType === 'reject' || actionType === 'cancel') {
        await api.post(endpoint, { reason: actionReason })
      } else if (actionType === 'settle') {
        await api.post(endpoint, { settlement_amount: invoice.invoice_amount })
      } else {
        await api.post(endpoint)
      }
      setShowActionModal(false)
      setActionType('')
      setActionReason('')
      fetchInvoice()
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
    if (!invoice) return []
    const actions: { key: string; label: string; icon: any; variant: string; handler: () => void }[] = []
    const currentStatus = invoice.invoice_status

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
        { key: 'disburse', label: 'Disburse Funds', icon: DollarSign, variant: 'primary', handler: () => openActionModal('disburse') }
      )
    } else if (currentStatus === 'financed') {
      actions.push(
        { key: 'settle', label: 'Settle Invoice', icon: Check, variant: 'primary', handler: () => openActionModal('settle') }
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

  if (error && !invoice) {
    return (
      <div className="card border-red-200">
        <div className="card-body text-center py-12">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">{error}</p>
          <button onClick={() => navigate('/invoice')} className="btn-secondary mt-4">
            Back to List
          </button>
        </div>
      </div>
    )
  }

  if (!invoice) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/invoice')} className="btn-secondary p-2">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">Invoice {invoice.invoice_number}</h1>
            <p className="text-sm text-secondary-500 mt-1">Invoice Financing Details</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`badge ${getStatusConfig(invoice.invoice_status).bg} ${getStatusConfig(invoice.invoice_status).color}`}>
            {getStatusConfig(invoice.invoice_status).label}
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

      {/* Invoice Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold">Invoice Information</h2>
            </div>
            <div className="card-body">
              {isEditing ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Seller Name</label>
                    <input
                      type="text"
                      value={formData.seller_name}
                      onChange={(e) => setFormData({ ...formData, seller_name: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label">Buyer Name</label>
                    <input
                      type="text"
                      value={formData.buyer_name}
                      onChange={(e) => setFormData({ ...formData, buyer_name: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="label">Seller Address</label>
                    <textarea
                      value={formData.seller_address}
                      onChange={(e) => setFormData({ ...formData, seller_address: e.target.value })}
                      className="input"
                      rows={2}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="label">Buyer Address</label>
                    <textarea
                      value={formData.buyer_address}
                      onChange={(e) => setFormData({ ...formData, buyer_address: e.target.value })}
                      className="input"
                      rows={2}
                    />
                  </div>
                  <div>
                    <label className="label">Invoice Amount</label>
                    <input
                      type="number"
                      value={formData.invoice_amount}
                      onChange={(e) => setFormData({ ...formData, invoice_amount: e.target.value })}
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
                      <option value="JPY">JPY</option>
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
                    <Building2 className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Seller</p>
                      <p className="font-medium">{invoice.seller_name || 'N/A'}</p>
                      <p className="text-sm text-secondary-500">{invoice.seller_address || ''}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Buyer</p>
                      <p className="font-medium">{invoice.buyer_name || 'N/A'}</p>
                      <p className="text-sm text-secondary-500">{invoice.buyer_address || ''}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Invoice Date</p>
                      <p className="font-medium">{formatDate(invoice.invoice_date)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-secondary-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-secondary-500">Due Date</p>
                      <p className="font-medium">{formatDate(invoice.due_date)}</p>
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
                <p className="text-sm text-secondary-500">Invoice Amount</p>
                <p className="text-2xl font-bold text-primary-600">
                  {formatAmount(invoice.invoice_amount, invoice.currency)}
                </p>
              </div>
              {invoice.financed_amount && (
                <div>
                  <p className="text-sm text-secondary-500">Financed Amount</p>
                  <p className="text-xl font-semibold text-purple-600">
                    {formatAmount(invoice.financed_amount, invoice.currency)}
                  </p>
                </div>
              )}
              {invoice.outstanding_amount && (
                <div>
                  <p className="text-sm text-secondary-500">Outstanding Amount</p>
                  <p className="text-lg font-semibold text-orange-600">
                    {formatAmount(invoice.outstanding_amount, invoice.currency)}
                  </p>
                </div>
              )}
              {invoice.repaid_amount && (
                <div>
                  <p className="text-sm text-secondary-500">Repaid Amount</p>
                  <p className="text-lg font-semibold text-green-600">
                    {formatAmount(invoice.repaid_amount, invoice.currency)}
                  </p>
                </div>
              )}
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
                  <p className="text-sm">{formatDate(invoice.created_at)}</p>
                </div>
              </div>
              {invoice.financing_start_date && (
                <div className="flex items-center gap-3">
                  <DollarSign className="w-4 h-4 text-secondary-400" />
                  <div>
                    <p className="text-sm text-secondary-500">Financing Start</p>
                    <p className="text-sm">{formatDate(invoice.financing_start_date)}</p>
                  </div>
                </div>
              )}
              {invoice.payment_date && (
                <div className="flex items-center gap-3">
                  <Check className="w-4 h-4 text-secondary-400" />
                  <div>
                    <p className="text-sm text-secondary-500">Payment Date</p>
                    <p className="text-sm">{formatDate(invoice.payment_date)}</p>
                  </div>
                </div>
              )}
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
              {actionType === 'submit' && 'Submit Invoice for Approval'}
              {actionType === 'approve' && 'Approve Invoice'}
              {actionType === 'reject' && 'Reject Invoice'}
              {actionType === 'disburse' && 'Disburse Funds'}
              {actionType === 'settle' && 'Settle Invoice'}
              {actionType === 'cancel' && 'Cancel Invoice'}
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

            {actionType === 'settle' && invoice && (
              <div className="mb-4">
                <p className="text-sm text-secondary-600 mb-2">
                  Settlement Amount: {formatAmount(invoice.invoice_amount, invoice.currency)}
                </p>
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
                  actionType === 'disburse' ? 'Disburse' :
                  actionType === 'settle' ? 'Settle' :
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
