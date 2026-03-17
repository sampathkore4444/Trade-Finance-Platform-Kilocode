import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  Ship,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Send,
  Edit,
  Download,
  Upload,
  MoreVertical,
  Printer,
  Mail,
  RefreshCw,
  Shield,
  Activity,
} from 'lucide-react'
import api from '@/api/axios'

// Types
interface LCDetailData {
  id: number
  lc_number: string
  lc_type: string
  status: string
  state: string
  
  // Applicant
  applicant_name: string
  applicant_address: string
  applicant_country: string
  
  // Beneficiary
  beneficiary_name: string
  beneficiary_address: string
  beneficiary_country: string
  
  // Banks
  issuing_bank_name: string
  issuing_bank_bic: string
  issuing_bank_address: string
  advising_bank_name: string
  advising_bank_bic: string
  
  // Amount
  currency: string
  amount: number
  tolerance_percent: number
  
  // Dates
  issue_date: string | null
  expiry_date: string | null
  expiry_place: string
  last_shipment_date: string | null
  
  // Shipment
  shipment_from: string
  shipment_to: string
  partial_shipment: boolean
  transhipment: boolean
  shipping_terms: string
  
  // Description
  description_goods: string
  description_services: string
  additional_conditions: string
  documents_required: string
  
  // Status tracking
  approved_by: number | null
  approved_at: string | null
  approval_comments: string | null
  rejected_by: number | null
  rejected_at: string | null
  rejection_reason: string | null
  
  // References
  internal_reference: string
  external_reference: string
  
  // Options
  is_revokable: boolean
  is_confirmed: boolean
  ucp_version: string
  terms_conditions: string
  
  // Metadata
  created_by: number | null
  assigned_to: number | null
  created_at: string
  updated_at: string | null
  
  // Relationships
  amendments: any[]
  documents: any[]
}

const STATUS_CONFIG: Record<string, { color: string; bg: string; icon: any }> = {
  draft: { color: 'text-secondary-600', bg: 'bg-secondary-100', icon: FileText },
  submitted: { color: 'text-blue-600', bg: 'bg-blue-100', icon: Send },
  under_review: { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: Clock },
  approved: { color: 'text-green-600', bg: 'bg-green-100', icon: CheckCircle },
  rejected: { color: 'text-red-600', bg: 'bg-red-100', icon: XCircle },
  issued: { color: 'text-purple-600', bg: 'bg-purple-100', icon: Send },
  amended: { color: 'text-indigo-600', bg: 'bg-indigo-100', icon: Edit },
  documents_received: { color: 'text-teal-600', bg: 'bg-teal-100', icon: Upload },
  under_examination: { color: 'text-orange-600', bg: 'bg-orange-100', icon: Activity },
  payment_processed: { color: 'text-green-600', bg: 'bg-green-100', icon: DollarSign },
  accepted: { color: 'text-green-600', bg: 'bg-green-100', icon: CheckCircle },
  closed: { color: 'text-secondary-600', bg: 'bg-secondary-100', icon: Shield },
  cancelled: { color: 'text-red-600', bg: 'bg-red-100', icon: XCircle },
}

const LC_TYPE_LABELS: Record<string, string> = {
  import: 'Import LC',
  export: 'Export LC',
  standby: 'Standby LC',
  transferable: 'Transferable LC',
  back_to_back: 'Back-to-Back LC',
  confirmed: 'Confirmed LC',
}

const TABS = [
  { id: 'details', label: 'LC Details', icon: FileText },
  { id: 'documents', label: 'Documents', icon: Upload },
  { id: 'amendments', label: 'Amendments', icon: Edit },
  { id: 'timeline', label: 'Timeline', icon: Clock },
]

export default function LCDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [lc, setLc] = useState<LCDetailData | null>(null)
  const [activeTab, setActiveTab] = useState('details')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isActionLoading, setIsActionLoading] = useState(false)
  const [showActionModal, setShowActionModal] = useState(false)
  const [actionType, setActionType] = useState('')
  const [actionComment, setActionComment] = useState('')

  useEffect(() => {
    fetchLCDetails()
  }, [id])

  const fetchLCDetails = async () => {
    if (!id) return
    
    setIsLoading(true)
    setError('')
    
    try {
      const response = await api.get(`/lc/${id}`)
      setLc(response.data)
    } catch (err: any) {
      console.error('Error fetching LC details:', err)
      setError(err.response?.data?.detail || 'Failed to load LC details')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAction = async () => {
    if (!id || !actionType) return
    
    setIsActionLoading(true)
    try {
      const endpoint = `/lc/${id}/${actionType}`
      const payload = actionType === 'reject' 
        ? { reason: actionComment }
        : { comments: actionComment }
      
      await api.post(endpoint, payload)
      await fetchLCDetails()
      setShowActionModal(false)
      setActionComment('')
    } catch (err: any) {
      console.error('Action error:', err)
      alert(err.response?.data?.detail || 'Action failed')
    } finally {
      setIsActionLoading(false)
    }
  }

  const getStatusConfig = (status: string) => {
    return STATUS_CONFIG[status] || { color: 'text-secondary-600', bg: 'bg-secondary-100', icon: FileText }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const formatDateTime = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount)
  }

  const getAvailableActions = () => {
    if (!lc) return []
    const actions: { id: string; label: string; variant: 'primary' | 'danger' }[] = []
    
    switch (lc.status) {
      case 'draft':
        actions.push({ id: 'submit', label: 'Submit for Review', variant: 'primary' })
        break
      case 'submitted':
        actions.push({ id: 'approve', label: 'Approve', variant: 'primary' })
        actions.push({ id: 'reject', label: 'Reject', variant: 'danger' })
        break
      case 'under_review':
        actions.push({ id: 'approve', label: 'Approve', variant: 'primary' })
        actions.push({ id: 'reject', label: 'Reject', variant: 'danger' })
        break
      case 'approved':
        actions.push({ id: 'issue', label: 'Issue LC', variant: 'primary' })
        break
      case 'issued':
        actions.push({ id: 'receive_documents', label: 'Receive Documents', variant: 'primary' })
        actions.push({ id: 'amend', label: 'Amend LC', variant: 'primary' })
        break
      case 'documents_received':
        actions.push({ id: 'examine', label: 'Examine Documents', variant: 'primary' })
        break
      case 'under_examination':
        actions.push({ id: 'accept', label: 'Accept Documents', variant: 'primary' })
        actions.push({ id: 'reject_docs', label: 'Reject Documents', variant: 'danger' })
        break
      case 'accepted':
        actions.push({ id: 'payment', label: 'Process Payment', variant: 'primary' })
        break
      case 'payment_processed':
        actions.push({ id: 'close', label: 'Close LC', variant: 'primary' })
        break
    }
    
    return actions
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-2 text-secondary-500">Loading LC details...</p>
        </div>
      </div>
    )
  }

  if (error || !lc) {
    return (
      <div className="space-y-6">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/lc')}
            className="mr-4 p-2 text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-2xl font-bold text-secondary-900">Error</h1>
        </div>
        <div className="card">
          <div className="card-body text-center py-12">
            <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-secondary-600">{error || 'LC not found'}</p>
            <button
              onClick={() => navigate('/lc')}
              className="mt-4 btn-primary"
            >
              Back to LC List
            </button>
          </div>
        </div>
      </div>
    )
  }

  const statusConfig = getStatusConfig(lc.status)
  const availableActions = getAvailableActions()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start">
          <button
            onClick={() => navigate('/lc')}
            className="mr-4 p-2 text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-secondary-900">{lc.lc_number}</h1>
              <span className={`badge ${statusConfig.bg} ${statusConfig.color}`}>
                {lc.status.replace(/_/g, ' ').toUpperCase()}
              </span>
              <span className="badge badge-secondary">{LC_TYPE_LABELS[lc.lc_type] || lc.lc_type}</span>
            </div>
            <p className="text-sm text-secondary-500 mt-1">
              Created {formatDateTime(lc.created_at)} • Last updated {formatDateTime(lc.updated_at)}
            </p>
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button className="btn-outline flex items-center">
            <Printer className="w-4 h-4 mr-2" />
            Print
          </button>
          <button className="btn-outline flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button className="btn-outline flex items-center">
            <Mail className="w-4 h-4 mr-2" />
            Send
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg mr-4">
              <DollarSign className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Amount</p>
              <p className="text-lg font-semibold text-secondary-900">
                {formatAmount(Number(lc.amount), lc.currency)}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-green-100 rounded-lg mr-4">
              <Building2 className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Applicant</p>
              <p className="text-lg font-semibold text-secondary-900 truncate">
                {lc.applicant_name || 'N/A'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg mr-4">
              <Globe className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Beneficiary</p>
              <p className="text-lg font-semibold text-secondary-900 truncate">
                {lc.beneficiary_name || 'N/A'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg mr-4">
              <Calendar className="h-6 w-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-secondary-500">Expiry Date</p>
              <p className="text-lg font-semibold text-secondary-900">
                {formatDate(lc.expiry_date)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Workflow Actions */}
      {availableActions.length > 0 && (
        <div className="card border-primary-200 bg-primary-50">
          <div className="card-header bg-transparent">
            <h3 className="text-lg font-semibold text-secondary-900">Workflow Actions</h3>
          </div>
          <div className="card-body flex flex-wrap gap-3">
            {availableActions.map((action) => (
              <button
                key={action.id}
                onClick={() => {
                  setActionType(action.id)
                  setShowActionModal(true)
                }}
                className={`btn ${
                  action.variant === 'primary' ? 'btn-primary' : 'btn-danger'
                }`}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-secondary-200">
        <nav className="flex space-x-8">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'details' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Party Details */}
          <div className="card">
            <div className="card-header bg-blue-50">
              <h3 className="text-lg font-semibold text-secondary-900">Applicant & Beneficiary</h3>
            </div>
            <div className="card-body space-y-4">
              <div>
                <p className="text-xs font-medium text-secondary-500 uppercase">Applicant</p>
                <p className="text-sm font-medium text-secondary-900">{lc.applicant_name}</p>
                <p className="text-sm text-secondary-600">{lc.applicant_address}</p>
                <p className="text-sm text-secondary-500">{lc.applicant_country}</p>
              </div>
              <hr className="border-secondary-200" />
              <div>
                <p className="text-xs font-medium text-secondary-500 uppercase">Beneficiary</p>
                <p className="text-sm font-medium text-secondary-900">{lc.beneficiary_name}</p>
                <p className="text-sm text-secondary-600">{lc.beneficiary_address}</p>
                <p className="text-sm text-secondary-500">{lc.beneficiary_country}</p>
              </div>
            </div>
          </div>

          {/* Bank Details */}
          <div className="card">
            <div className="card-header bg-green-50">
              <h3 className="text-lg font-semibold text-secondary-900">Bank Details</h3>
            </div>
            <div className="card-body space-y-4">
              <div>
                <p className="text-xs font-medium text-secondary-500 uppercase">Issuing Bank</p>
                <p className="text-sm font-medium text-secondary-900">{lc.issuing_bank_name}</p>
                <p className="text-sm text-secondary-500">SWIFT: {lc.issuing_bank_bic}</p>
                <p className="text-sm text-secondary-600">{lc.issuing_bank_address}</p>
              </div>
              {lc.advising_bank_name && (
                <>
                  <hr className="border-secondary-200" />
                  <div>
                    <p className="text-xs font-medium text-secondary-500 uppercase">Advising Bank</p>
                    <p className="text-sm font-medium text-secondary-900">{lc.advising_bank_name}</p>
                    <p className="text-sm text-secondary-500">SWIFT: {lc.advising_bank_bic}</p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Amount & Terms */}
          <div className="card">
            <div className="card-header bg-yellow-50">
              <h3 className="text-lg font-semibold text-secondary-900">Amount & Terms</h3>
            </div>
            <div className="card-body space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">Amount</p>
                  <p className="text-lg font-semibold text-secondary-900">
                    {formatAmount(Number(lc.amount), lc.currency)}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">Tolerance</p>
                  <p className="text-lg font-semibold text-secondary-900">
                    ±{lc.tolerance_percent}%
                  </p>
                </div>
              </div>
              <hr className="border-secondary-200" />
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">Expiry Date</p>
                  <p className="text-sm text-secondary-900">{formatDate(lc.expiry_date)}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">Expiry Place</p>
                  <p className="text-sm text-secondary-900">{lc.expiry_place}</p>
                </div>
              </div>
              <hr className="border-secondary-200" />
              <div>
                <p className="text-xs font-medium text-secondary-500 uppercase">UCP Version</p>
                <p className="text-sm text-secondary-900">{lc.ucp_version}</p>
              </div>
            </div>
          </div>

          {/* Shipment Details */}
          <div className="card">
            <div className="card-header bg-teal-50">
              <h3 className="text-lg font-semibold text-secondary-900">Shipment Details</h3>
            </div>
            <div className="card-body space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">From</p>
                  <p className="text-sm text-secondary-900">{lc.shipment_from}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">To</p>
                  <p className="text-sm text-secondary-900">{lc.shipment_to}</p>
                </div>
              </div>
              <hr className="border-secondary-200" />
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">Last Shipment</p>
                  <p className="text-sm text-secondary-900">{formatDate(lc.last_shipment_date)}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-secondary-500 uppercase">Incoterms</p>
                  <p className="text-sm text-secondary-900">{lc.shipping_terms || 'N/A'}</p>
                </div>
              </div>
              <hr className="border-secondary-200" />
              <div className="flex space-x-6">
                <label className="flex items-center">
                  <span className={`badge ${lc.partial_shipment ? 'badge-success' : 'badge-secondary'}`}>
                    Partial Shipment: {lc.partial_shipment ? 'Allowed' : 'Not Allowed'}
                  </span>
                </label>
                <label className="flex items-center">
                  <span className={`badge ${lc.transhipment ? 'badge-success' : 'badge-secondary'}`}>
                    Transhipment: {lc.transhipment ? 'Allowed' : 'Not Allowed'}
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="card lg:col-span-2">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-secondary-900">Description of Goods</h3>
            </div>
            <div className="card-body">
              <p className="text-sm text-secondary-700 whitespace-pre-wrap">
                {lc.description_goods || 'No description provided'}
              </p>
            </div>
          </div>

          {/* Documents Required */}
          {lc.documents_required && (
            <div className="card lg:col-span-2">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">Documents Required</h3>
              </div>
              <div className="card-body">
                <p className="text-sm text-secondary-700 whitespace-pre-wrap">
                  {lc.documents_required}
                </p>
              </div>
            </div>
          )}

          {/* Additional Conditions */}
          {lc.additional_conditions && (
            <div className="card lg:col-span-2">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">Additional Conditions</h3>
              </div>
              <div className="card-body">
                <p className="text-sm text-secondary-700 whitespace-pre-wrap">
                  {lc.additional_conditions}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'documents' && (
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-semibold text-secondary-900">LC Documents</h3>
            <button className="btn-primary flex items-center">
              <Upload className="w-4 h-4 mr-2" />
              Upload Document
            </button>
          </div>
          <div className="card-body">
            {lc.documents && lc.documents.length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Document Type</th>
                    <th>File Name</th>
                    <th>Uploaded By</th>
                    <th>Upload Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {lc.documents.map((doc: any) => (
                    <tr key={doc.id}>
                      <td className="font-medium">{doc.document_type}</td>
                      <td>{doc.file_name}</td>
                      <td>{doc.uploaded_by_name || 'N/A'}</td>
                      <td>{formatDateTime(doc.uploaded_at)}</td>
                      <td>
                        <span className="badge badge-success">Received</span>
                      </td>
                      <td>
                        <button className="text-primary-600 hover:text-primary-500">
                          <Download className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="text-center py-12">
                <Upload className="w-12 h-12 text-secondary-300 mx-auto mb-4" />
                <p className="text-secondary-500">No documents uploaded yet</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'amendments' && (
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-semibold text-secondary-900">LC Amendments</h3>
            <button className="btn-primary flex items-center">
              <Edit className="w-4 h-4 mr-2" />
              Request Amendment
            </button>
          </div>
          <div className="card-body">
            {lc.amendments && lc.amendments.length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Amendment No.</th>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {lc.amendments.map((amendment: any) => (
                    <tr key={amendment.id}>
                      <td className="font-medium">AM-{amendment.amendment_number}</td>
                      <td>{formatDate(amendment.amendment_date)}</td>
                      <td>{amendment.description}</td>
                      <td>
                        <span className="badge badge-success">{amendment.status}</span>
                      </td>
                      <td>
                        <button className="text-primary-600 hover:text-primary-500">
                          <Download className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="text-center py-12">
                <Edit className="w-12 h-12 text-secondary-300 mx-auto mb-4" />
                <p className="text-secondary-500">No amendments have been made</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'timeline' && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900">Activity Timeline</h3>
          </div>
          <div className="card-body">
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-secondary-200" />
              <div className="space-y-6">
                <div className="relative flex items-start">
                  <div className="absolute left-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  </div>
                  <div className="ml-12">
                    <p className="text-sm font-medium text-secondary-900">LC Created</p>
                    <p className="text-xs text-secondary-500">{formatDateTime(lc.created_at)}</p>
                  </div>
                </div>
                {lc.approved_at && (
                  <div className="relative flex items-start">
                    <div className="absolute left-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    </div>
                    <div className="ml-12">
                      <p className="text-sm font-medium text-secondary-900">LC Approved</p>
                      <p className="text-xs text-secondary-500">{formatDateTime(lc.approved_at)}</p>
                      {lc.approval_comments && (
                        <p className="text-sm text-secondary-600 mt-1">{lc.approval_comments}</p>
                      )}
                    </div>
                  </div>
                )}
                {lc.issued_at && (
                  <div className="relative flex items-start">
                    <div className="absolute left-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <Send className="w-4 h-4 text-purple-600" />
                    </div>
                    <div className="ml-12">
                      <p className="text-sm font-medium text-secondary-900">LC Issued</p>
                      <p className="text-xs text-secondary-500">{formatDateTime(lc.issued_at)}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Modal */}
      {showActionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-secondary-200">
              <h3 className="text-lg font-semibold text-secondary-900">
                {actionType === 'reject' ? 'Reject LC' : 
                 actionType === 'submit' ? 'Submit LC' :
                 actionType === 'approve' ? 'Approve LC' :
                 actionType === 'issue' ? 'Issue LC' : 'Confirm Action'}
              </h3>
            </div>
            <div className="px-6 py-4">
              <label className="label">
                {actionType === 'reject' ? 'Rejection Reason' : 'Comments (Optional)'}
              </label>
              <textarea
                value={actionComment}
                onChange={(e) => setActionComment(e.target.value)}
                className="input min-h-[100px]"
                placeholder={actionType === 'reject' ? 'Please provide a reason for rejection...' : 'Add any comments...'}
              />
            </div>
            <div className="px-6 py-4 bg-secondary-50 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowActionModal(false)
                  setActionComment('')
                }}
                className="btn-secondary"
                disabled={isActionLoading}
              >
                Cancel
              </button>
              <button
                onClick={handleAction}
                className={`btn ${actionType === 'reject' ? 'btn-danger' : 'btn-primary'}`}
                disabled={isActionLoading}
              >
                {isActionLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  'Confirm'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
