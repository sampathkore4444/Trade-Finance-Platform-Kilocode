import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Receipt,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  Send,
} from 'lucide-react'
import api from '@/api/axios'

// Types matching backend schema
interface InvoiceFormData {
  // Invoice Type
  invoice_type: 'trade_invoice' | 'commercial_invoice' | 'consignment_invoice'

  // Seller (Exporter)
  seller_name: string
  seller_address: string
  seller_country: string
  seller_tax_id: string

  // Buyer (Importer)
  buyer_name: string
  buyer_address: string
  buyer_country: string
  buyer_tax_id: string

  // Invoice Details
  invoice_number: string
  invoice_date: string
  currency: string
  amount: string
  tax_amount: string
  discount_percent: string

  // Payment Terms
  payment_terms: string
  due_date: string

  // Goods/Services Description
  description_goods: string
  description_services: string
  quantity: string
  unit_price: string

  // Shipping
  shipment_date: string
  shipment_from: string
  shipment_to: string

  // Reference
  internal_reference: string
  external_reference: string

  // Additional
  notes: string
}

interface FormErrors {
  [key: string]: string
}

const INVOICE_TYPES = [
  { value: 'trade_invoice', label: 'Trade Invoice' },
  { value: 'commercial_invoice', label: 'Commercial Invoice' },
  { value: 'consignment_invoice', label: 'Consignment Invoice' },
]

const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CNY', 'INR', 'SGD', 'AUD', 'CAD']

const COUNTRIES = [
  'Afghanistan', 'Albania', 'Algeria', 'Argentina', 'Australia', 'Austria', 'Bahrain',
  'Bangladesh', 'Belgium', 'Brazil', 'Canada', 'China', 'Colombia', 'Czech Republic',
  'Denmark', 'Egypt', 'Finland', 'France', 'Germany', 'Greece', 'Hong Kong', 'Hungary',
  'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Japan', 'Jordan',
  'Kenya', 'Kuwait', 'Lebanon', 'Malaysia', 'Mexico', 'Morocco', 'Netherlands', 'New Zealand',
  'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Peru', 'Philippines', 'Poland', 'Portugal',
  'Qatar', 'Romania', 'Russia', 'Saudi Arabia', 'Singapore', 'South Africa', 'South Korea',
  'Spain', 'Sri Lanka', 'Sweden', 'Switzerland', 'Taiwan', 'Thailand', 'Turkey', 'UAE',
  'United Kingdom', 'United States', 'Vietnam', 'Zimbabwe'
]

const PAYMENT_TERMS = [
  { value: 'immediate', label: 'Immediate Payment' },
  { value: 'net_15', label: 'Net 15 Days' },
  { value: 'net_30', label: 'Net 30 Days' },
  { value: 'net_45', label: 'Net 45 Days' },
  { value: 'net_60', label: 'Net 60 Days' },
  { value: 'net_90', label: 'Net 90 Days' },
]

const initialFormData: InvoiceFormData = {
  invoice_type: 'trade_invoice',
  seller_name: '',
  seller_address: '',
  seller_country: '',
  seller_tax_id: '',
  buyer_name: '',
  buyer_address: '',
  buyer_country: '',
  buyer_tax_id: '',
  invoice_number: '',
  invoice_date: '',
  currency: 'USD',
  amount: '',
  tax_amount: '0',
  discount_percent: '0',
  payment_terms: 'net_30',
  due_date: '',
  description_goods: '',
  description_services: '',
  quantity: '',
  unit_price: '',
  shipment_date: '',
  shipment_from: '',
  shipment_to: '',
  internal_reference: '',
  external_reference: '',
  notes: '',
}

const STEPS = [
  { id: 1, title: 'Invoice Type', description: 'Select invoice category' },
  { id: 2, title: 'Seller & Buyer', description: 'Party details' },
  { id: 3, title: 'Invoice Details', description: 'Amount & dates' },
  { id: 4, title: 'Payment Terms', description: 'Payment conditions' },
  { id: 5, title: 'Shipment', description: 'Shipping information' },
  { id: 6, title: 'Review', description: 'Confirm details' },
]

export default function InvoiceCreate() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<InvoiceFormData>(initialFormData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [submitSuccess, setSubmitSuccess] = useState(false)

  const updateField = (field: keyof InvoiceFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  const validateStep = (step: number): boolean => {
    const newErrors: FormErrors = {}

    switch (step) {
      case 1:
        if (!formData.invoice_type) {
          newErrors.invoice_type = 'Invoice Type is required'
        }
        break
      case 2:
        if (!formData.seller_name.trim()) {
          newErrors.seller_name = 'Seller name is required'
        }
        if (!formData.seller_country) {
          newErrors.seller_country = 'Seller country is required'
        }
        if (!formData.buyer_name.trim()) {
          newErrors.buyer_name = 'Buyer name is required'
        }
        if (!formData.buyer_country) {
          newErrors.buyer_country = 'Buyer country is required'
        }
        break
      case 3:
        if (!formData.invoice_number.trim()) {
          newErrors.invoice_number = 'Invoice number is required'
        }
        if (!formData.invoice_date) {
          newErrors.invoice_date = 'Invoice date is required'
        }
        if (!formData.amount || parseFloat(formData.amount) <= 0) {
          newErrors.amount = 'Valid amount is required'
        }
        break
      case 4:
        if (!formData.payment_terms) {
          newErrors.payment_terms = 'Payment terms are required'
        }
        if (!formData.due_date) {
          newErrors.due_date = 'Due date is required'
        }
        break
      case 5:
        if (!formData.description_goods.trim() && !formData.description_services.trim()) {
          newErrors.description_goods = 'Description of goods or services is required'
        }
        break
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, STEPS.length))
    }
  }

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1))
  }

  const handleSubmit = async () => {
    if (!validateStep(6)) return

    setIsSubmitting(true)
    setSubmitError('')

    try {
      const payload = {
        ...formData,
        invoice_amount: parseFloat(formData.amount),
        amount: parseFloat(formData.amount),
        tax_amount: parseFloat(formData.tax_amount) || 0,
        discount_percent: parseFloat(formData.discount_percent) || 0,
        quantity: formData.quantity ? parseFloat(formData.quantity) : null,
        unit_price: formData.unit_price ? parseFloat(formData.unit_price) : null,
        invoice_date: formData.invoice_date ? new Date(formData.invoice_date).toISOString() : null,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
        shipment_date: formData.shipment_date ? new Date(formData.shipment_date).toISOString() : null,
      }

      const response = await api.post('/invoice/invoices/', payload)
      
      if (response.data && response.data.id) {
        setSubmitSuccess(true)
        setTimeout(() => {
          navigate('/invoice')
        }, 2000)
      }
    } catch (error: any) {
      console.error('Invoice Creation Error:', error)
      // Handle FastAPI validation error response
      const errorData = error.response?.data
      let errorMessage = 'Failed to create Invoice. Please try again.'
      
      if (errorData?.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (Array.isArray(errorData.detail)) {
          // Format validation errors
          errorMessage = errorData.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        }
      } else if (errorData?.message) {
        errorMessage = errorData.message
      }
      
      setSubmitError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  const calculateTotal = () => {
    const amount = parseFloat(formData.amount) || 0
    const tax = parseFloat(formData.tax_amount) || 0
    const discount = amount * (parseFloat(formData.discount_percent) || 0) / 100
    return amount + tax - discount
  }

  const renderStepIndicator = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {STEPS.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            <div
              className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                currentStep > step.id
                  ? 'bg-green-500 border-green-500 text-white'
                  : currentStep === step.id
                  ? 'bg-primary-600 border-primary-600 text-white'
                  : 'bg-white border-secondary-300 text-secondary-400'
              }`}
            >
              {currentStep > step.id ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <span className="text-sm font-medium">{step.id}</span>
              )}
            </div>
            {index < STEPS.length - 1 && (
              <div
                className={`flex-1 h-0.5 mx-2 ${
                  currentStep > step.id ? 'bg-green-500' : 'bg-secondary-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>
      <div className="flex justify-between mt-2">
        {STEPS.map((step) => (
          <div
            key={step.id}
            className={`text-xs text-center flex-1 ${
              currentStep >= step.id ? 'text-secondary-700' : 'text-secondary-400'
            }`}
          >
            {step.title}
          </div>
        ))}
      </div>
    </div>
  )

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Receipt className="w-5 h-5 mr-2 text-primary-600" />
            Invoice Type
          </h3>
        </div>
        <div className="card-body">
          <p className="text-sm text-secondary-500 mb-4">
            Select the type of Invoice for your trade transaction.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {INVOICE_TYPES.map((type) => (
              <label
                key={type.value}
                className={`flex items-center p-4 border rounded-lg cursor-pointer transition-all ${
                  formData.invoice_type === type.value
                    ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                    : 'border-secondary-200 hover:border-secondary-300 hover:bg-secondary-50'
                }`}
              >
                <input
                  type="radio"
                  name="invoice_type"
                  value={type.value}
                  checked={formData.invoice_type === type.value}
                  onChange={(e) => updateField('invoice_type', e.target.value as InvoiceFormData['invoice_type'])}
                  className="sr-only"
                />
                <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 mr-3">
                  {formData.invoice_type === type.value && (
                    <div className="w-2.5 h-2.5 rounded-full bg-primary-600" />
                  )}
                </div>
                <span className="font-medium text-secondary-900">{type.label}</span>
              </label>
            ))}
          </div>
          {errors.invoice_type && (
            <p className="mt-2 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.invoice_type}
            </p>
          )}
        </div>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      {/* Seller Section */}
      <div className="card">
        <div className="card-header bg-blue-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Building2 className="w-5 h-5 mr-2 text-blue-600" />
            Seller (Exporter)
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="label">
                Company Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.seller_name}
                onChange={(e) => updateField('seller_name', e.target.value)}
                className={`input ${errors.seller_name ? 'border-red-500' : ''}`}
                placeholder="Enter seller company name"
              />
              {errors.seller_name && (
                <p className="mt-1 text-sm text-red-600">{errors.seller_name}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Address</label>
              <textarea
                value={formData.seller_address}
                onChange={(e) => updateField('seller_address', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Enter complete address"
              />
            </div>
            <div>
              <label className="label">Tax ID</label>
              <input
                type="text"
                value={formData.seller_tax_id}
                onChange={(e) => updateField('seller_tax_id', e.target.value)}
                className="input"
                placeholder="Tax identification number"
              />
            </div>
            <div>
              <label className="label">
                Country <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.seller_country}
                onChange={(e) => updateField('seller_country', e.target.value)}
                className={`input ${errors.seller_country ? 'border-red-500' : ''}`}
              >
                <option value="">Select country</option>
                {COUNTRIES.map((country) => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              {errors.seller_country && (
                <p className="mt-1 text-sm text-red-600">{errors.seller_country}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Buyer Section */}
      <div className="card">
        <div className="card-header bg-green-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-green-600" />
            Buyer (Importer)
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="label">
                Company Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.buyer_name}
                onChange={(e) => updateField('buyer_name', e.target.value)}
                className={`input ${errors.buyer_name ? 'border-red-500' : ''}`}
                placeholder="Enter buyer company name"
              />
              {errors.buyer_name && (
                <p className="mt-1 text-sm text-red-600">{errors.buyer_name}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Address</label>
              <textarea
                value={formData.buyer_address}
                onChange={(e) => updateField('buyer_address', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Enter complete address"
              />
            </div>
            <div>
              <label className="label">Tax ID</label>
              <input
                type="text"
                value={formData.buyer_tax_id}
                onChange={(e) => updateField('buyer_tax_id', e.target.value)}
                className="input"
                placeholder="Tax identification number"
              />
            </div>
            <div>
              <label className="label">
                Country <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.buyer_country}
                onChange={(e) => updateField('buyer_country', e.target.value)}
                className={`input ${errors.buyer_country ? 'border-red-500' : ''}`}
              >
                <option value="">Select country</option>
                {COUNTRIES.map((country) => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              {errors.buyer_country && (
                <p className="mt-1 text-sm text-red-600">{errors.buyer_country}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-primary-600" />
            Invoice Information
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">
                Invoice Number <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.invoice_number}
                onChange={(e) => updateField('invoice_number', e.target.value)}
                className={`input ${errors.invoice_number ? 'border-red-500' : ''}`}
                placeholder="e.g., INV-2024-001"
              />
              {errors.invoice_number && (
                <p className="mt-1 text-sm text-red-600">{errors.invoice_number}</p>
              )}
            </div>
            <div>
              <label className="label">
                Invoice Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.invoice_date}
                onChange={(e) => updateField('invoice_date', e.target.value)}
                className={`input ${errors.invoice_date ? 'border-red-500' : ''}`}
              />
              {errors.invoice_date && (
                <p className="mt-1 text-sm text-red-600">{errors.invoice_date}</p>
              )}
            </div>
            <div>
              <label className="label">Currency</label>
              <select
                value={formData.currency}
                onChange={(e) => updateField('currency', e.target.value)}
                className="input"
              >
                {CURRENCIES.map((curr) => (
                  <option key={curr} value={curr}>{curr}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">
                Amount <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => updateField('amount', e.target.value)}
                className={`input ${errors.amount ? 'border-red-500' : ''}`}
                placeholder="Enter invoice amount"
                min="0"
                step="0.01"
              />
              {errors.amount && (
                <p className="mt-1 text-sm text-red-600">{errors.amount}</p>
              )}
            </div>
            <div>
              <label className="label">Tax Amount</label>
              <input
                type="number"
                value={formData.tax_amount}
                onChange={(e) => updateField('tax_amount', e.target.value)}
                className="input"
                placeholder="0.00"
                min="0"
                step="0.01"
              />
            </div>
            <div>
              <label className="label">Discount (%)</label>
              <input
                type="number"
                value={formData.discount_percent}
                onChange={(e) => updateField('discount_percent', e.target.value)}
                className="input"
                placeholder="0"
                min="0"
                max="100"
                step="0.1"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card bg-primary-50 border-primary-200">
        <div className="card-body">
          <div className="flex items-center justify-between">
            <span className="text-lg font-semibold text-primary-900">Total Amount</span>
            <span className="text-2xl font-bold text-primary-600">
              {formData.currency} {calculateTotal().toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-primary-600" />
            Payment Terms
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">
                Payment Terms <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.payment_terms}
                onChange={(e) => updateField('payment_terms', e.target.value)}
                className={`input ${errors.payment_terms ? 'border-red-500' : ''}`}
              >
                {PAYMENT_TERMS.map((term) => (
                  <option key={term.value} value={term.value}>{term.label}</option>
                ))}
              </select>
              {errors.payment_terms && (
                <p className="mt-1 text-sm text-red-600">{errors.payment_terms}</p>
              )}
            </div>
            <div>
              <label className="label">
                Due Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => updateField('due_date', e.target.value)}
                className={`input ${errors.due_date ? 'border-red-500' : ''}`}
              />
              {errors.due_date && (
                <p className="mt-1 text-sm text-red-600">{errors.due_date}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep5 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Goods/Services Description</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="label">
                Description of Goods
              </label>
              <textarea
                value={formData.description_goods}
                onChange={(e) => updateField('description_goods', e.target.value)}
                className={`input min-h-[100px] ${errors.description_goods ? 'border-red-500' : ''}`}
                placeholder="Describe the goods being invoiced"
              />
              {errors.description_goods && (
                <p className="mt-1 text-sm text-red-600">{errors.description_goods}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Description of Services</label>
              <textarea
                value={formData.description_services}
                onChange={(e) => updateField('description_services', e.target.value)}
                className="input min-h-[100px]"
                placeholder="Describe any services being invoiced"
              />
            </div>
            <div>
              <label className="label">Quantity</label>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => updateField('quantity', e.target.value)}
                className="input"
                placeholder="e.g., 100"
                min="0"
                step="0.01"
              />
            </div>
            <div>
              <label className="label">Unit Price</label>
              <input
                type="number"
                value={formData.unit_price}
                onChange={(e) => updateField('unit_price', e.target.value)}
                className="input"
                placeholder="Price per unit"
                min="0"
                step="0.01"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Shipment Information</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Shipment Date</label>
              <input
                type="date"
                value={formData.shipment_date}
                onChange={(e) => updateField('shipment_date', e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="label">Shipment From</label>
              <input
                type="text"
                value={formData.shipment_from}
                onChange={(e) => updateField('shipment_from', e.target.value)}
                className="input"
                placeholder="Port or place of loading"
              />
            </div>
            <div>
              <label className="label">Shipment To</label>
              <input
                type="text"
                value={formData.shipment_to}
                onChange={(e) => updateField('shipment_to', e.target.value)}
                className="input"
                placeholder="Port or place of destination"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Additional Information</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Internal Reference</label>
              <input
                type="text"
                value={formData.internal_reference}
                onChange={(e) => updateField('internal_reference', e.target.value)}
                className="input"
                placeholder="Internal reference number"
              />
            </div>
            <div>
              <label className="label">External Reference</label>
              <input
                type="text"
                value={formData.external_reference}
                onChange={(e) => updateField('external_reference', e.target.value)}
                className="input"
                placeholder="External reference number"
              />
            </div>
            <div className="md:col-span-2">
              <label className="label">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => updateField('notes', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Additional notes or comments"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep6 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Review Invoice</h3>
        </div>
        <div className="card-body space-y-6">
          {/* Type */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-1">Invoice Type</h4>
            <p className="font-medium">{INVOICE_TYPES.find(t => t.value === formData.invoice_type)?.label}</p>
          </div>

          {/* Parties */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Parties</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-secondary-400">Seller</p>
                <p className="font-medium">{formData.seller_name}</p>
                <p className="text-sm text-secondary-500">{formData.seller_country}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Buyer</p>
                <p className="font-medium">{formData.buyer_name}</p>
                <p className="text-sm text-secondary-500">{formData.buyer_country}</p>
              </div>
            </div>
          </div>

          {/* Invoice Details */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Invoice Details</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-secondary-400">Invoice Number</p>
                <p className="font-medium">{formData.invoice_number}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Invoice Date</p>
                <p className="font-medium">{formData.invoice_date}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Amount</p>
                <p className="font-medium">{formData.currency} {parseFloat(formData.amount || '0').toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Due Date</p>
                <p className="font-medium">{formData.due_date}</p>
              </div>
            </div>
          </div>

          {/* Total */}
          <div>
            <h4 className="text-sm font-medium text-secondary-500 mb-1">Total Amount</h4>
            <p className="text-2xl font-bold text-primary-600">
              {formData.currency} {calculateTotal().toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {submitError && (
        <div className="card border-red-200 bg-red-50">
          <div className="card-body">
            <p className="text-red-600 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              {submitError}
            </p>
          </div>
        </div>
      )}

      {/* Success Message */}
      {submitSuccess && (
        <div className="card border-green-200 bg-green-50">
          <div className="card-body">
            <p className="text-green-600 flex items-center">
              <CheckCircle className="w-5 h-5 mr-2" />
              Invoice created successfully! Redirecting...
            </p>
          </div>
        </div>
      )}
    </div>
  )

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1: return renderStep1()
      case 2: return renderStep2()
      case 3: return renderStep3()
      case 4: return renderStep4()
      case 5: return renderStep5()
      case 6: return renderStep6()
      default: return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Create Invoice</h1>
          <p className="text-sm text-secondary-500 mt-1">
            Fill in the details to create a new Invoice for financing
          </p>
        </div>
        <button
          onClick={() => navigate('/invoice')}
          className="btn-outline flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Invoice List
        </button>
      </div>

      {/* Step Indicator */}
      {renderStepIndicator()}

      {/* Form Steps */}
      <div className="card">
        <div className="card-body">
          {renderCurrentStep()}
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleBack}
          disabled={currentStep === 1 || isSubmitting}
          className="btn-outline flex items-center disabled:opacity-50"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>

        <div className="flex items-center space-x-3">
          {currentStep < STEPS.length ? (
            <button
              onClick={handleNext}
              className="btn-primary flex items-center"
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <>
              <button
                onClick={() => handleSubmit()}
                disabled={isSubmitting}
                className="btn-primary flex items-center"
              >
                {isSubmitting ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Submit
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
