import { useState, useEffect } from 'react'
import api from '@/api/axios'
import { 
  Upload, 
  FileText, 
  Download, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  Search, 
  Loader2,
  File,
  X
} from 'lucide-react'

interface Document {
  id: number
  file_name: string
  stored_filename?: string
  document_type: string | null
  entity_type: string | null
  entity_id: number | null
  status: string
  mime_type: string
  file_size: number
  created_at: string
  uploaded_by: string | null
  verified_at?: string | null
  verified_by?: string | null
  rejection_reason?: string | null
}

interface LC {
  id: string
  lc_number: string
}

interface Guarantee {
  id: string
  guarantee_number: string
}

interface Collection {
  id: string
  collection_number: string
}

interface Loan {
  id: string
  loan_number: string
}

interface Invoice {
  id: string
  invoice_number: string
}

const documentTypes = [
  { value: '', label: 'All Types' },
  { value: 'bill_of_lading', label: 'Bill of Lading' },
  { value: 'commercial_invoice', label: 'Commercial Invoice' },
  { value: 'certificate_of_origin', label: 'Certificate of Origin' },
  { value: 'insurance_certificate', label: 'Insurance Certificate' },
  { value: 'packing_list', label: 'Packing List' },
  { value: 'inspection_certificate', label: 'Inspection Certificate' },
  { value: 'customs_declaration', label: 'Customs Declaration' },
  { value: 'draft', label: 'Draft' },
  { value: 'other', label: 'Other' },
]

const statusFilters = [
  { value: '', label: 'All Status' },
  { value: 'pending', label: 'Pending' },
  { value: 'verified', label: 'Verified' },
  { value: 'rejected', label: 'Rejected' },
]

const entityFilters = [
  { value: '', label: 'All Entities' },
  { value: 'LC', label: 'Letter of Credit' },
  { value: 'Guarantee', label: 'Bank Guarantee' },
  { value: 'Collection', label: 'Documentary Collection' },
  { value: 'Loan', label: 'Trade Loan' },
  { value: 'Invoice', label: 'Invoice Finance' },
]

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterEntity, setFilterEntity] = useState('')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteDocId, setDeleteDocId] = useState<number | null>(null)
  const [rejectReason, setRejectReason] = useState('')
  const [rejectDocId, setRejectDocId] = useState<number | null>(null)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadType, setUploadType] = useState('')
  const [uploadEntityType, setUploadEntityType] = useState('')
  const [uploadEntityId, setUploadEntityId] = useState('')
  
  // Entity options for dropdown
  const [lcs, setLcs] = useState<LC[]>([])
  const [guarantees, setGuarantees] = useState<Guarantee[]>([])
  const [collections, setCollections] = useState<Collection[]>([])
  const [loans, setLoans] = useState<Loan[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])

  useEffect(() => {
    fetchDocuments()
    fetchEntities()
  }, [filterType, filterStatus, filterEntity])

  const fetchEntities = async () => {
    try {
      const results = await Promise.allSettled([
        api.get('/lc/'),
        api.get('/guarantee/'),
        api.get('/collection/collections/'),
        api.get('/loan/loans/'),
        api.get('/invoice/invoices/')
      ])
      
      if (results[0].status === 'fulfilled') setLcs(results[0].value.data.items || [])
      if (results[1].status === 'fulfilled') setGuarantees(results[1].value.data.items || [])
      if (results[2].status === 'fulfilled') setCollections(results[2].value.data.items || [])
      if (results[3].status === 'fulfilled') setLoans(results[3].value.data.items || [])
      if (results[4].status === 'fulfilled') setInvoices(results[4].value.data.items || [])
    } catch (error) {
      console.error('Error fetching entities:', error)
    }
  }

  const getEntityOptions = () => {
    switch (uploadEntityType) {
      case 'LC':
        return lcs.map(lc => ({ value: lc.id, label: lc.lc_number }))
      case 'Guarantee':
        return guarantees.map(g => ({ value: g.id, label: g.guarantee_number }))
      case 'Collection':
        return collections.map(c => ({ value: c.id, label: c.collection_number }))
      case 'Loan':
        return loans.map(l => ({ value: l.id, label: l.loan_number }))
      case 'Invoice':
        return invoices.map(i => ({ value: i.id, label: i.invoice_number }))
      default:
        return []
    }
  }

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filterType) params.append('document_type', filterType)
      if (filterStatus) params.append('status', filterStatus)
      if (filterEntity) params.append('entity_type', filterEntity)
      
      const response = await api.get(`/documents/?${params.toString()}`)
      setDocuments(response.data)
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async () => {
    if (!uploadFile) return
    
    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', uploadFile)
      if (uploadType) formData.append('document_type', uploadType)
      if (uploadEntityType) formData.append('entity_type', uploadEntityType)
      if (uploadEntityId) formData.append('entity_id', uploadEntityId)

      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setShowUploadModal(false)
      setUploadFile(null)
      setUploadType('')
      setUploadEntityType('')
      setUploadEntityId('')
      fetchDocuments()
    } catch (error) {
      console.error('Error uploading document:', error)
      alert('Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const handleDownload = async (doc: Document) => {
    try {
      const response = await api.get(`/documents/${doc.id}/download`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', doc.file_name)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error downloading document:', error)
    }
  }

  const handleVerify = async (docId: number) => {
    try {
      await api.post(`/documents/${docId}/verify`)
      fetchDocuments()
    } catch (error) {
      console.error('Error verifying document:', error)
    }
  }

  const handleReject = async (docId: number) => {
    setRejectDocId(docId)
    setShowRejectModal(true)
  }

  const confirmReject = async () => {
    if (!rejectReason.trim() || !rejectDocId) return
    
    try {
      await api.post(`/documents/${rejectDocId}/reject`, { reason: rejectReason })
      fetchDocuments()
      setShowRejectModal(false)
      setRejectReason('')
      setRejectDocId(null)
    } catch (error) {
      console.error('Error rejecting document:', error)
    }
  }

  const handleDelete = async (docId: number) => {
    setDeleteDocId(docId)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (!deleteDocId) return
    
    try {
      await api.delete(`/documents/${deleteDocId}`)
      fetchDocuments()
      setShowDeleteModal(false)
      setDeleteDocId(null)
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }

  const filteredDocuments = documents.filter(doc => 
    (doc.file_name || '').toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'verified':
        return <span className="badge badge-success">Verified</span>
      case 'rejected':
        return <span className="badge badge-danger">Rejected</span>
      default:
        return <span className="badge badge-warning">Pending</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Documents</h1>
          <p className="text-secondary-500 mt-1">Manage all trade finance documents</p>
        </div>
        <button 
          onClick={() => setShowUploadModal(true)}
          className="btn-primary flex items-center"
        >
          <Upload className="w-5 h-5 mr-2" />
          Upload Document
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>

            {/* Document Type Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="input"
            >
              {documentTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>

            {/* Status Filter */}
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input"
            >
              {statusFilters.map(status => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </select>

            {/* Entity Filter */}
            <select
              value={filterEntity}
              onChange={(e) => setFilterEntity(e.target.value)}
              className="input"
            >
              {entityFilters.map(entity => (
                <option key={entity.value} value={entity.value}>{entity.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Documents Table */}
      <div className="card">
        <div className="card-body p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
            </div>
          ) : filteredDocuments.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-secondary-300 mx-auto mb-4" />
              <p className="text-secondary-500">No documents found</p>
              <button 
                onClick={() => setShowUploadModal(true)}
                className="btn-primary mt-4"
              >
                Upload Your First Document
              </button>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Type</th>
                  <th>Linked Entity</th>
                  <th>Size</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <div className="flex items-center">
                        <File className="w-5 h-5 text-secondary-400 mr-3" />
                        <span className="font-medium">{doc.file_name}</span>
                      </div>
                    </td>
                    <td>
                      <span className="text-secondary-600 capitalize">
                        {doc.document_type?.replace(/_/g, ' ') || 'N/A'}
                      </span>
                    </td>
                    <td>
                      <div>
                        <span className="text-secondary-600">{doc.entity_type || 'N/A'}</span>
                        {doc.entity_id && (
                          <span className="text-secondary-400 text-sm ml-1">#{doc.entity_id}</span>
                        )}
                      </div>
                    </td>
                    <td className="text-secondary-600">{formatFileSize(doc.file_size)}</td>
                    <td>{getStatusBadge(doc.status)}</td>
                    <td className="text-secondary-600">{formatDate(doc.created_at)}</td>
                    <td>
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleDownload(doc)}
                          className="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        {doc.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleVerify(Number(doc.id))}
                              className="p-2 text-secondary-600 hover:text-green-600 hover:bg-green-50 rounded"
                              title="Verify"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleReject(Number(doc.id))}
                              className="p-2 text-secondary-600 hover:text-red-600 hover:bg-red-50 rounded"
                              title="Reject"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => handleDelete(Number(doc.id))}
                          className="p-2 text-secondary-600 hover:text-red-600 hover:bg-red-50 rounded"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="flex justify-between items-center p-4 border-b">
              <h2 className="text-lg font-semibold">Upload Document</h2>
              <button 
                onClick={() => setShowUploadModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4 space-y-4">
              {/* File Input */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Select File
                </label>
                <input
                  type="file"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="input"
                />
              </div>

              {/* Document Type */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Document Type
                </label>
                <select
                  value={uploadType}
                  onChange={(e) => setUploadType(e.target.value)}
                  className="input"
                >
                  {documentTypes.filter(t => t.value).map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              {/* Entity Type */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Link to Trade Finance Entity (Optional)
                </label>
                <select
                  value={uploadEntityType}
                  onChange={(e) => {
                    setUploadEntityType(e.target.value)
                    setUploadEntityId('')
                  }}
                  className="input"
                >
                  {entityFilters.filter(e => e.value).map(entity => (
                    <option key={entity.value} value={entity.value}>{entity.label}</option>
                  ))}
                </select>
              </div>

              {/* Entity Reference - Dropdown with actual records */}
              {uploadEntityType && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Select {uploadEntityType} Reference Number
                  </label>
                  <select
                    value={uploadEntityId}
                    onChange={(e) => setUploadEntityId(e.target.value)}
                    className="input"
                  >
                    <option value="">-- Select Reference --</option>
                    {getEntityOptions().map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                  {getEntityOptions().length === 0 && (
                    <p className="text-xs text-secondary-500 mt-1">
                      No {uploadEntityType.toLowerCase()} records found
                    </p>
                  )}
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-3 p-4 border-t bg-secondary-50">
              <button
                onClick={() => setShowUploadModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={!uploadFile || uploading}
                className="btn-primary"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  'Upload'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="flex justify-between items-center p-4 border-b">
              <h2 className="text-lg font-semibold text-red-600">Reject Document</h2>
              <button
                onClick={() => { setShowRejectModal(false); setRejectReason(''); setRejectDocId(null); }}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4">
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Rejection Reason
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                rows={4}
                placeholder="Please provide a reason for rejection..."
                autoFocus
              />
            </div>

            <div className="flex justify-end space-x-3 p-4 border-t bg-secondary-50">
              <button
                onClick={() => { setShowRejectModal(false); setRejectReason(''); setRejectDocId(null); }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={confirmReject}
                disabled={!rejectReason.trim()}
                className="btn-danger"
              >
                Reject Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="flex justify-between items-center p-4 border-b">
              <h2 className="text-lg font-semibold text-red-600">Reject Document</h2>
              <button 
                onClick={() => { setShowRejectModal(false); setRejectReason(''); setRejectDocId(null); }}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4">
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Rejection Reason
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                rows={4}
                placeholder="Please provide a reason for rejection..."
                autoFocus
              />
            </div>

            <div className="flex justify-end space-x-3 p-4 border-t bg-secondary-50">
              <button
                onClick={() => { setShowRejectModal(false); setRejectReason(''); setRejectDocId(null); }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={confirmReject}
                disabled={!rejectReason.trim()}
                className="btn-danger"
              >
                Reject Document
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="flex justify-between items-center p-4 border-b">
              <h2 className="text-lg font-semibold text-red-600">Delete Document</h2>
              <button 
                onClick={() => { setShowDeleteModal(false); setDeleteDocId(null); }}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4">
              <p className="text-secondary-600">
                Are you sure you want to delete this document? This action cannot be undone.
              </p>
            </div>

            <div className="flex justify-end space-x-3 p-4 border-t bg-secondary-50">
              <button
                onClick={() => { setShowDeleteModal(false); setDeleteDocId(null); }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="btn-danger"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
