import { useState, useEffect } from 'react'
import {
  Plus, Search, Filter, Download, RefreshCw, ChevronLeft, ChevronRight, MoreVertical, Eye, Edit,
  FileText, Building2, DollarSign, Calendar, AlertCircle, Receipt
} from 'lucide-react'
import api from '@/api/axios'

interface InvoiceItem {
  id: number
  invoice_number: string
  invoice_type: string
  status: string
  seller_name: string
  buyer_name: string
  currency: string
  amount: number
  due_date: string | null
  created_at: string
}

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  draft: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Draft' },
  submitted: { color: 'text-blue-600', bg: 'bg-blue-100', label: 'Submitted' },
  approved: { color: 'text-green-600', bg: 'bg-green-100', label: 'Approved' },
  rejected: { color: 'text-red-600', bg: 'bg-red-100', label: 'Rejected' },
  financed: { color: 'text-purple-600', bg: 'bg-purple-100', label: 'Financed' },
  repaid: { color: 'text-teal-600', bg: 'bg-teal-100', label: 'Repaid' },
  overdue: { color: 'text-orange-600', bg: 'bg-orange-100', label: 'Overdue' },
  closed: { color: 'text-secondary-600', bg: 'bg-secondary-100', label: 'Closed' },
}

const INVOICE_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'trade_invoice', label: 'Trade Invoice' },
  { value: 'commercial_invoice', label: 'Commercial Invoice' },
  { value: 'consignment_invoice', label: 'Consignment Invoice' },
]

export default function InvoiceList() {
  const [invoices, setInvoices] = useState<InvoiceItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => { fetchInvoices() }, [page, status])

  const fetchInvoices = async () => {
    setIsLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('page_size', '10')
      if (search) params.append('search', search)
      if (status) params.append('status', status)
      const response = await api.get(`/invoice/invoices/?${params.toString()}`)
      setInvoices(response.data.items)
      setTotal(response.data.total)
      setTotalPages(response.data.total_pages)
    } catch (err: any) {
      console.error('Error fetching invoices:', err)
      setError(err.response?.data?.detail || 'Failed to load Invoices')
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (d: string | null) => d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A'
  const formatAmount = (a: number, c: string) => new Intl.NumberFormat('en-US', { style: 'currency', currency: c, minimumFractionDigits: 0 }).format(a)
  const getStatusConfig = (s: string) => STATUS_CONFIG[s] || { color: 'text-secondary-600', bg: 'bg-secondary-100', label: s }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Invoice Financing</h1>
          <p className="text-sm text-secondary-500 mt-1">Manage Invoice Financing transactions</p>
        </div>
        <button className="btn-primary"><Plus className="h-5 w-5 mr-2" />Create Invoice</button>
      </div>

      <div className="card">
        <div className="card-body">
          <form onSubmit={(e) => { e.preventDefault(); setPage(1); fetchInvoices() }} className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-secondary-400" />
              <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search invoices..." className="input pl-10" />
            </div>
            <button type="button" onClick={() => setShowFilters(!showFilters)} className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'}`}><Filter className="w-4 h-4 mr-2" />Filters</button>
            <button type="submit" className="btn-primary"><Search className="w-4 h-4 mr-2" />Search</button>
            <button type="button" onClick={fetchInvoices} className="btn-outline"><RefreshCw className="w-4 h-4" /></button>
          </form>
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-secondary-200 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Status</label>
                <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }} className="input">
                  <option value="">All Statuses</option>
                  {Object.entries(STATUS_CONFIG).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
                </select>
              </div>
              <div className="flex items-end">
                <button onClick={() => { setStatus(''); setSearch(''); setPage(1) }} className="btn-outline w-full">Clear</button>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-secondary-500">Showing {invoices.length} of {total} Invoices</p>
        <button className="btn-outline text-sm"><Download className="w-4 h-4 mr-2" />Export</button>
      </div>

      {isLoading && <div className="card"><div className="card-body text-center py-12"><div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" /></div></div>}
      {error && !isLoading && <div className="card border-red-200"><div className="card-body text-center py-12"><AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" /><p>{error}</p></div></div>}

      {!isLoading && !error && (
        <div className="card overflow-hidden">
          <table className="table">
            <thead><tr><th>Invoice No.</th><th>Type</th><th>Seller</th><th>Buyer</th><th>Amount</th><th>Due Date</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-12"><Receipt className="w-12 h-12 text-secondary-300 mx-auto mb-4" /><p className="text-secondary-500">No Invoices found</p></td></tr>
              ) : invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-secondary-50">
                  <td className="font-medium text-primary-600">{inv.invoice_number}</td>
                  <td><span className="badge badge-secondary">{inv.invoice_type}</span></td>
                  <td className="max-w-[150px] truncate"><span className="truncate">{inv.seller_name || 'N/A'}</span></td>
                  <td className="max-w-[150px] truncate"><span className="truncate">{inv.buyer_name || 'N/A'}</span></td>
                  <td className="font-medium">{formatAmount(Number(inv.amount), inv.currency)}</td>
                  <td>{formatDate(inv.due_date)}</td>
                  <td><span className={`badge ${getStatusConfig(inv.status).bg} ${getStatusConfig(inv.status).color}`}>{getStatusConfig(inv.status).label}</span></td>
                  <td><div className="flex space-x-2"><button className="p-1 text-secondary-400 hover:text-primary-600"><Eye className="w-4 h-4" /></button><button className="p-1 text-secondary-400 hover:text-primary-600"><Edit className="w-4 h-4" /></button></div></td>
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
    </div>
  )
}
