import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  FileText,
  Building2,
  DollarSign,
  CheckCircle,
  AlertCircle,
  Clock,
  Send,
} from 'lucide-react'
import api from '@/api/axios'

// Types matching backend schema
interface CollectionFormData {
  // Collection Type
  collection_type: 'da_dp' | 'da_da'

  // Applicant (Drawer/Seller)
  applicant_name: string
  applicant_address: string
  applicant_country: string

  // Beneficiary (Drawee/Buyer)
  beneficiary_name: string
  beneficiary_address: string
  beneficiary_country: string

  // Remitting Bank
  remitting_bank_name: string
  remitting_bank_bic: string

  // Collecting Bank
  collecting_bank_name: string
  collecting_bank_bic: string

  // Presenting Bank
  presenting_bank_name: string
  presenting_bank_bic: string

  // Amount
  currency: string
  amount: string

  // Dates
  issue_date: string
  due_date: string

  // Documents
  documents_description: string
  invoice_number: string

  // Reference
  internal_reference: string
}

interface FormErrors {
  [key: string]: string
}

const COLLECTION_TYPES = [
  { value: 'da_da', label: 'Documents Against Acceptance (D/A)', description: 'Documents are released to the buyer upon acceptance of the draft' },
  { value: 'da_dp', label: 'Documents Against Payment (D/P)', description: 'Documents are released to the buyer upon payment' },
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

const initialFormData: CollectionFormData = {
  collection_type: 'da_da',
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
  currency: 'USD',
  amount: '',
  issue_date: '',
  due_date: '',
  documents_description: '',
  invoice_number: '',
  internal_reference: '',
}

export default function CollectionCreate() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<CollectionFormData>(initialFormData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [submitSuccess, setSubmitSuccess] = useState(false)

  const updateField = (field: keyof CollectionFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  const validate = (): boolean => {
    const newErrors: FormErrors = {}

    // Collection type
    if (!formData.collection_type) {
      newErrors.collection_type = 'Collection Type is required'
    }

    // Applicant (Drawer)
    if (!formData.applicant_name.trim()) {
      newErrors.applicant_name = 'Applicant name is required'
    }

    // Beneficiary (Drawee)
    if (!formData.beneficiary_name.trim()) {
      newErrors.beneficiary_name = 'Beneficiary name is required'
    }

    // Amount
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = 'Valid amount is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setIsSubmitting(true)
    setSubmitError('')

    try {
      const payload = {
        collection_type: formData.collection_type,
        applicant_name: formData.applicant_name,
        applicant_address: formData.applicant_address || null,
        applicant_country: formData.applicant_country || null,
        beneficiary_name: formData.beneficiary_name,
        beneficiary_address: formData.beneficiary_address || null,
        beneficiary_country: formData.beneficiary_country || null,
        remitting_bank_name: formData.remitting_bank_name || null,
        remitting_bank_bic: formData.remitting_bank_bic || null,
        collecting_bank_name: formData.collecting_bank_name || null,
        collecting_bank_bic: formData.collecting_bank_bic || null,
        presenting_bank_name: formData.presenting_bank_name || null,
        presenting_bank_bic: formData.presenting_bank_bic || null,
        currency: formData.currency,
        amount: parseFloat(formData.amount),
        issue_date: formData.issue_date ? new Date(formData.issue_date).toISOString() : null,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
        documents_description: formData.documents_description || null,
        invoice_number: formData.invoice_number || null,
        internal_reference: formData.internal_reference || null,
      }

      const response = await api.post('/collection/collections/', payload)
      
      if (response.data && response.data.id) {
        setSubmitSuccess(true)
        setTimeout(() => {
          navigate('/collection')
        }, 2000)
      }
    } catch (error: any) {
      console.error('Collection Creation Error:', error)
      // Handle FastAPI validation errors which can be an array of error objects
      let errorMessage = 'Failed to create Documentary Collection. Please try again.'
      const detail = error.response?.data?.detail
      if (detail) {
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          // Format validation errors: "field: message"
          errorMessage = detail.map((e: any) => `${e.loc?.[e.loc?.length - 1] || 'field'}: ${e.msg}`).join(', ')
        }
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      setSubmitError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Create Documentary Collection</h1>
          <p className="text-sm text-secondary-500 mt-1">
            Fill in the details to create a new Documentary Collection
          </p>
        </div>
        <button
          onClick={() => navigate('/collection')}
          className="btn-outline flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Collection List
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Collection Type */}
        <div className="card mb-6">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
              <FileText className="w-5 h-5 mr-2 text-primary-600" />
              Documentary Collection Type
            </h3>
          </div>
          <div className="card-body">
            <p className="text-sm text-secondary-500 mb-4">
              Select the type of Documentary Collection that best matches your transaction requirements.
            </p>
            <div className="space-y-4">
              {COLLECTION_TYPES.map((type) => (
                <label
                  key={type.value}
                  className={`flex items-start p-4 border rounded-lg cursor-pointer transition-all ${
                    formData.collection_type === type.value
                      ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                      : 'border-secondary-200 hover:border-secondary-300 hover:bg-secondary-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="collection_type"
                    value={type.value}
                    checked={formData.collection_type === type.value}
                    onChange={(e) => updateField('collection_type', e.target.value as CollectionFormData['collection_type'])}
                    className="sr-only"
                  />
                  <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 mr-3 mt-0.5">
                    {formData.collection_type === type.value && (
                      <div className="w-2.5 h-2.5 rounded-full bg-primary-600" />
                    )}
                  </div>
                  <div>
                    <span className="font-medium text-secondary-900">{type.label}</span>
                    <p className="text-sm text-secondary-500 mt-1">{type.description}</p>
                  </div>
                </label>
              ))}
            </div>
            {errors.collection_type && (
              <p className="mt-2 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.collection_type}
              </p>
            )}
          </div>
        </div>

        {/* Applicant & Beneficiary */}
        <div className="card mb-6">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
              <Building2 className="w-5 h-5 mr-2 text-primary-600" />
              Parties Information
            </h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Applicant Section */}
              <div className="space-y-4">
                <h4 className="font-medium text-secondary-700 border-b pb-2">Applicant (Drawer/Seller)</h4>
                <div>
                  <label className="label">
                    Company Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.applicant_name}
                    onChange={(e) => updateField('applicant_name', e.target.value)}
                    className={`input ${errors.applicant_name ? 'border-red-500' : ''}`}
                    placeholder="Enter applicant company name"
                  />
                  {errors.applicant_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.applicant_name}</p>
                  )}
                </div>
                <div>
                  <label className="label">Address</label>
                  <textarea
                    value={formData.applicant_address}
                    onChange={(e) => updateField('applicant_address', e.target.value)}
                    className="input min-h-[80px]"
                    placeholder="Enter company address"
                  />
                </div>
                <div>
                  <label className="label">Country</label>
                  <select
                    value={formData.applicant_country}
                    onChange={(e) => updateField('applicant_country', e.target.value)}
                    className="input"
                  >
                    <option value="">Select country</option>
                    {COUNTRIES.map((country) => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Beneficiary Section */}
              <div className="space-y-4">
                <h4 className="font-medium text-secondary-700 border-b pb-2">Beneficiary (Drawee/Buyer)</h4>
                <div>
                  <label className="label">
                    Company Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.beneficiary_name}
                    onChange={(e) => updateField('beneficiary_name', e.target.value)}
                    className={`input ${errors.beneficiary_name ? 'border-red-500' : ''}`}
                    placeholder="Enter beneficiary company name"
                  />
                  {errors.beneficiary_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.beneficiary_name}</p>
                  )}
                </div>
                <div>
                  <label className="label">Address</label>
                  <textarea
                    value={formData.beneficiary_address}
                    onChange={(e) => updateField('beneficiary_address', e.target.value)}
                    className="input min-h-[80px]"
                    placeholder="Enter company address"
                  />
                </div>
                <div>
                  <label className="label">Country</label>
                  <select
                    value={formData.beneficiary_country}
                    onChange={(e) => updateField('beneficiary_country', e.target.value)}
                    className="input"
                  >
                    <option value="">Select country</option>
                    {COUNTRIES.map((country) => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bank Details */}
        <div className="card mb-6">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900">
              Bank Information (Optional)
            </h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Remitting Bank */}
              <div className="space-y-4">
                <h4 className="font-medium text-secondary-700 border-b pb-2">Remitting Bank</h4>
                <div>
                  <label className="label">Bank Name</label>
                  <input
                    type="text"
                    value={formData.remitting_bank_name}
                    onChange={(e) => updateField('remitting_bank_name', e.target.value)}
                    className="input"
                    placeholder="Enter remitting bank name"
                  />
                </div>
                <div>
                  <label className="label">BIC/SWIFT Code</label>
                  <input
                    type="text"
                    value={formData.remitting_bank_bic}
                    onChange={(e) => updateField('remitting_bank_bic', e.target.value)}
                    className="input"
                    placeholder="e.g., DEUTDEFF"
                  />
                </div>
              </div>

              {/* Collecting Bank */}
              <div className="space-y-4">
                <h4 className="font-medium text-secondary-700 border-b pb-2">Collecting Bank</h4>
                <div>
                  <label className="label">Bank Name</label>
                  <input
                    type="text"
                    value={formData.collecting_bank_name}
                    onChange={(e) => updateField('collecting_bank_name', e.target.value)}
                    className="input"
                    placeholder="Enter collecting bank name"
                  />
                </div>
                <div>
                  <label className="label">BIC/SWIFT Code</label>
                  <input
                    type="text"
                    value={formData.collecting_bank_bic}
                    onChange={(e) => updateField('collecting_bank_bic', e.target.value)}
                    className="input"
                    placeholder="e.g., DEUTDEFF"
                  />
                </div>
              </div>

              {/* Presenting Bank */}
              <div className="space-y-4">
                <h4 className="font-medium text-secondary-700 border-b pb-2">Presenting Bank</h4>
                <div>
                  <label className="label">Bank Name</label>
                  <input
                    type="text"
                    value={formData.presenting_bank_name}
                    onChange={(e) => updateField('presenting_bank_name', e.target.value)}
                    className="input"
                    placeholder="Enter presenting bank name"
                  />
                </div>
                <div>
                  <label className="label">BIC/SWIFT Code</label>
                  <input
                    type="text"
                    value={formData.presenting_bank_bic}
                    onChange={(e) => updateField('presenting_bank_bic', e.target.value)}
                    className="input"
                    placeholder="e.g., DEUTDEFF"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Amount & Terms */}
        <div className="card mb-6">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
              <DollarSign className="w-5 h-5 mr-2 text-primary-600" />
              Amount & Terms
            </h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
                  placeholder="Enter collection amount"
                  min="0"
                  step="0.01"
                />
                {errors.amount && (
                  <p className="mt-1 text-sm text-red-600">{errors.amount}</p>
                )}
              </div>
              <div>
                <label className="label">Issue Date</label>
                <input
                  type="date"
                  value={formData.issue_date}
                  onChange={(e) => updateField('issue_date', e.target.value)}
                  className="input"
                />
              </div>
              <div>
                <label className="label">Due Date</label>
                <input
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => updateField('due_date', e.target.value)}
                  className="input"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Documents & Reference */}
        <div className="card mb-6">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900">
              Documents & Reference (Optional)
            </h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Invoice Number</label>
                <input
                  type="text"
                  value={formData.invoice_number}
                  onChange={(e) => updateField('invoice_number', e.target.value)}
                  className="input"
                  placeholder="Enter invoice number"
                />
              </div>
              <div>
                <label className="label">Internal Reference</label>
                <input
                  type="text"
                  value={formData.internal_reference}
                  onChange={(e) => updateField('internal_reference', e.target.value)}
                  className="input"
                  placeholder="Enter internal reference"
                />
              </div>
              <div className="md:col-span-2">
                <label className="label">Documents Description</label>
                <textarea
                  value={formData.documents_description}
                  onChange={(e) => updateField('documents_description', e.target.value)}
                  className="input min-h-[80px]"
                  placeholder="Enter documents description"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {submitError && (
          <div className="card border-red-200 bg-red-50 mb-6">
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
          <div className="card border-green-200 bg-green-50 mb-6">
            <div className="card-body">
              <p className="text-green-600 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Documentary Collection created successfully! Redirecting...
              </p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
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
                Create Documentary Collection
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
