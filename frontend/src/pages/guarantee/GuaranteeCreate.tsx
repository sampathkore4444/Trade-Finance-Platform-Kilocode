import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Save,
  Send,
  Shield,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
} from 'lucide-react'
import api from '@/api/axios'

// Types matching backend schema
interface GuaranteeFormData {
  // Guarantee Type
  guarantee_type: 'bid_bond' | 'performance_bond' | 'advance_payment_guarantee' | 'payment_guarantee' | 'warranty_guarantee' | 'customs_guarantee' | 'judicial_guarantee' | 'financial_guarantee'

  // Applicant (Requesting Party)
  applicant_name: string
  applicant_address: string
  applicant_country: string

  // Beneficiary (Receiving Party)
  beneficiary_name: string
  beneficiary_address: string
  beneficiary_country: string

  // Issuing Bank
  issuing_bank_name: string
  issuing_bank_bic: string
  issuing_bank_address: string

  // Amount
  currency: string
  amount: string

  // Dates
  issue_date: string
  expiry_date: string
  expiry_place: string

  // Guarantee Details
  guarantee_amount_percent: string
  description: string
  underlying_contract_ref: string
  claim_conditions: string

  // Reference
  internal_reference: string
  external_reference: string
}

interface FormErrors {
  [key: string]: string
}

const GUARANTEE_TYPES = [
  { value: 'bid_bond', label: 'Bid Bond' },
  { value: 'performance_bond', label: 'Performance Bond' },
  { value: 'advance_payment_guarantee', label: 'Advance Payment Guarantee' },
  { value: 'payment_guarantee', label: 'Payment Guarantee' },
  { value: 'warranty_guarantee', label: 'Warranty Guarantee' },
  { value: 'customs_guarantee', label: 'Customs Guarantee' },
  { value: 'judicial_guarantee', label: 'Judicial Guarantee' },
  { value: 'financial_guarantee', label: 'Financial Guarantee' },
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

const initialFormData: GuaranteeFormData = {
  guarantee_type: 'performance_bond',
  applicant_name: '',
  applicant_address: '',
  applicant_country: '',
  beneficiary_name: '',
  beneficiary_address: '',
  beneficiary_country: '',
  issuing_bank_name: '',
  issuing_bank_bic: '',
  issuing_bank_address: '',
  currency: 'USD',
  amount: '',
  issue_date: '',
  expiry_date: '',
  expiry_place: '',
  guarantee_amount_percent: '100',
  description: '',
  underlying_contract_ref: '',
  claim_conditions: '',
  internal_reference: '',
  external_reference: '',
}

const STEPS = [
  { id: 1, title: 'Guarantee Type', description: 'Select guarantee category' },
  { id: 2, title: 'Applicant & Beneficiary', description: 'Party details' },
  { id: 3, title: 'Bank Details', description: 'Issuing bank information' },
  { id: 4, title: 'Amount & Dates', description: 'Terms & validity' },
  { id: 5, title: 'Terms', description: 'Conditions & references' },
  { id: 6, title: 'Review', description: 'Confirm details' },
]

export default function GuaranteeCreate() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<GuaranteeFormData>(initialFormData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [submitSuccess, setSubmitSuccess] = useState(false)

  const updateField = (field: keyof GuaranteeFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  const validateStep = (step: number): boolean => {
    const newErrors: FormErrors = {}

    switch (step) {
      case 1:
        if (!formData.guarantee_type) {
          newErrors.guarantee_type = 'Guarantee Type is required'
        }
        break
      case 2:
        if (!formData.applicant_name.trim()) {
          newErrors.applicant_name = 'Applicant name is required'
        }
        if (!formData.applicant_country) {
          newErrors.applicant_country = 'Applicant country is required'
        }
        if (!formData.beneficiary_name.trim()) {
          newErrors.beneficiary_name = 'Beneficiary name is required'
        }
        if (!formData.beneficiary_country) {
          newErrors.beneficiary_country = 'Beneficiary country is required'
        }
        break
      case 3:
        if (!formData.issuing_bank_name.trim()) {
          newErrors.issuing_bank_name = 'Issuing bank name is required'
        }
        if (!formData.issuing_bank_bic.trim()) {
          newErrors.issuing_bank_bic = 'Bank BIC/SWIFT code is required'
        }
        break
      case 4:
        if (!formData.amount || parseFloat(formData.amount) <= 0) {
          newErrors.amount = 'Valid amount is required'
        }
        if (!formData.expiry_date) {
          newErrors.expiry_date = 'Expiry date is required'
        }
        if (!formData.expiry_place.trim()) {
          newErrors.expiry_place = 'Expiry place is required'
        }
        break
      case 5:
        if (!formData.description.trim()) {
          newErrors.description = 'Description is required'
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
        amount: parseFloat(formData.amount),
        guarantee_amount_percent: parseFloat(formData.guarantee_amount_percent),
        issue_date: formData.issue_date ? new Date(formData.issue_date).toISOString() : null,
        expiry_date: formData.expiry_date ? new Date(formData.expiry_date).toISOString() : null,
      }

      const response = await api.post('/guarantee/', payload)
      
      if (response.data && response.data.id) {
        setSubmitSuccess(true)
        setTimeout(() => {
          navigate('/guarantee')
        }, 2000)
      }
    } catch (error: any) {
      console.error('Guarantee Creation Error:', error)
      // Handle FastAPI validation errors which can be an array of error objects
      let errorMessage = 'Failed to create Bank Guarantee. Please try again.'
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
            <Shield className="w-5 h-5 mr-2 text-primary-600" />
            Bank Guarantee Type
          </h3>
        </div>
        <div className="card-body">
          <p className="text-sm text-secondary-500 mb-4">
            Select the type of Bank Guarantee that best matches your requirements.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {GUARANTEE_TYPES.map((type) => (
              <label
                key={type.value}
                className={`flex items-center p-4 border rounded-lg cursor-pointer transition-all ${
                  formData.guarantee_type === type.value
                    ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                    : 'border-secondary-200 hover:border-secondary-300 hover:bg-secondary-50'
                }`}
              >
                <input
                  type="radio"
                  name="guarantee_type"
                  value={type.value}
                  checked={formData.guarantee_type === type.value}
                  onChange={(e) => updateField('guarantee_type', e.target.value as GuaranteeFormData['guarantee_type'])}
                  className="sr-only"
                />
                <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 mr-3">
                  {formData.guarantee_type === type.value && (
                    <div className="w-2.5 h-2.5 rounded-full bg-primary-600" />
                  )}
                </div>
                <span className="font-medium text-secondary-900">{type.label}</span>
              </label>
            ))}
          </div>
          {errors.guarantee_type && (
            <p className="mt-2 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.guarantee_type}
            </p>
          )}
        </div>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      {/* Applicant Section */}
      <div className="card">
        <div className="card-header bg-blue-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Building2 className="w-5 h-5 mr-2 text-blue-600" />
            Applicant (Requesting Party)
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
                value={formData.applicant_name}
                onChange={(e) => updateField('applicant_name', e.target.value)}
                className={`input ${errors.applicant_name ? 'border-red-500' : ''}`}
                placeholder="Enter applicant company name"
              />
              {errors.applicant_name && (
                <p className="mt-1 text-sm text-red-600">{errors.applicant_name}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Address</label>
              <textarea
                value={formData.applicant_address}
                onChange={(e) => updateField('applicant_address', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Enter complete address"
              />
            </div>
            <div>
              <label className="label">
                Country <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.applicant_country}
                onChange={(e) => updateField('applicant_country', e.target.value)}
                className={`input ${errors.applicant_country ? 'border-red-500' : ''}`}
              >
                <option value="">Select country</option>
                {COUNTRIES.map((country) => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              {errors.applicant_country && (
                <p className="mt-1 text-sm text-red-600">{errors.applicant_country}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Beneficiary Section */}
      <div className="card">
        <div className="card-header bg-green-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-green-600" />
            Beneficiary (Receiving Party)
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
                value={formData.beneficiary_name}
                onChange={(e) => updateField('beneficiary_name', e.target.value)}
                className={`input ${errors.beneficiary_name ? 'border-red-500' : ''}`}
                placeholder="Enter beneficiary company name"
              />
              {errors.beneficiary_name && (
                <p className="mt-1 text-sm text-red-600">{errors.beneficiary_name}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Address</label>
              <textarea
                value={formData.beneficiary_address}
                onChange={(e) => updateField('beneficiary_address', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Enter complete address"
              />
            </div>
            <div>
              <label className="label">
                Country <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.beneficiary_country}
                onChange={(e) => updateField('beneficiary_country', e.target.value)}
                className={`input ${errors.beneficiary_country ? 'border-red-500' : ''}`}
              >
                <option value="">Select country</option>
                {COUNTRIES.map((country) => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              {errors.beneficiary_country && (
                <p className="mt-1 text-sm text-red-600">{errors.beneficiary_country}</p>
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
            <Building2 className="w-5 h-5 mr-2 text-primary-600" />
            Issuing Bank Details
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="label">
                Bank Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.issuing_bank_name}
                onChange={(e) => updateField('issuing_bank_name', e.target.value)}
                className={`input ${errors.issuing_bank_name ? 'border-red-500' : ''}`}
                placeholder="Enter issuing bank name"
              />
              {errors.issuing_bank_name && (
                <p className="mt-1 text-sm text-red-600">{errors.issuing_bank_name}</p>
              )}
            </div>
            <div>
              <label className="label">
                BIC/SWIFT Code <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.issuing_bank_bic}
                onChange={(e) => updateField('issuing_bank_bic', e.target.value)}
                className={`input ${errors.issuing_bank_bic ? 'border-red-500' : ''}`}
                placeholder="e.g., DEUTDEFF"
              />
              {errors.issuing_bank_bic && (
                <p className="mt-1 text-sm text-red-600">{errors.issuing_bank_bic}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Bank Address</label>
              <textarea
                value={formData.issuing_bank_address}
                onChange={(e) => updateField('issuing_bank_address', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Enter bank address"
              />
            </div>
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
            <DollarSign className="w-5 h-5 mr-2 text-primary-600" />
            Amount
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                placeholder="Enter guarantee amount"
                min="0"
                step="0.01"
              />
              {errors.amount && (
                <p className="mt-1 text-sm text-red-600">{errors.amount}</p>
              )}
            </div>
            <div>
              <label className="label">Guarantee Amount (%)</label>
              <input
                type="number"
                value={formData.guarantee_amount_percent}
                onChange={(e) => updateField('guarantee_amount_percent', e.target.value)}
                className="input"
                placeholder="100"
                min="0"
                max="100"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-primary-600" />
            Validity Period
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              <label className="label">
                Expiry Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.expiry_date}
                onChange={(e) => updateField('expiry_date', e.target.value)}
                className={`input ${errors.expiry_date ? 'border-red-500' : ''}`}
              />
              {errors.expiry_date && (
                <p className="mt-1 text-sm text-red-600">{errors.expiry_date}</p>
              )}
            </div>
            <div>
              <label className="label">
                Expiry Place <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.expiry_place}
                onChange={(e) => updateField('expiry_place', e.target.value)}
                className={`input ${errors.expiry_place ? 'border-red-500' : ''}`}
                placeholder="e.g., Issuing Bank Counter"
              />
              {errors.expiry_place && (
                <p className="mt-1 text-sm text-red-600">{errors.expiry_place}</p>
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
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-primary-600" />
            Guarantee Terms
          </h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            <div>
              <label className="label">
                Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => updateField('description', e.target.value)}
                className={`input min-h-[120px] ${errors.description ? 'border-red-500' : ''}`}
                placeholder="Describe the purpose and nature of the guarantee"
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600">{errors.description}</p>
              )}
            </div>
            <div>
              <label className="label">Underlying Contract Reference</label>
              <input
                type="text"
                value={formData.underlying_contract_ref}
                onChange={(e) => updateField('underlying_contract_ref', e.target.value)}
                className="input"
                placeholder="Reference to the main contract"
              />
            </div>
            <div>
              <label className="label">Claim Conditions</label>
              <textarea
                value={formData.claim_conditions}
                onChange={(e) => updateField('claim_conditions', e.target.value)}
                className="input min-h-[100px]"
                placeholder="Terms and conditions for claiming the guarantee"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Reference Numbers</h3>
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
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep6 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Review Bank Guarantee</h3>
        </div>
        <div className="card-body space-y-6">
          {/* Type */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-1">Guarantee Type</h4>
            <p className="font-medium">{GUARANTEE_TYPES.find(t => t.value === formData.guarantee_type)?.label}</p>
          </div>

          {/* Parties */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Parties</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-secondary-400">Applicant</p>
                <p className="font-medium">{formData.applicant_name}</p>
                <p className="text-sm text-secondary-500">{formData.applicant_country}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Beneficiary</p>
                <p className="font-medium">{formData.beneficiary_name}</p>
                <p className="text-sm text-secondary-500">{formData.beneficiary_country}</p>
              </div>
            </div>
          </div>

          {/* Bank */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Issuing Bank</h4>
            <p className="font-medium">{formData.issuing_bank_name}</p>
            <p className="text-sm text-secondary-500">{formData.issuing_bank_bic}</p>
          </div>

          {/* Amount & Dates */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Amount & Validity</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-secondary-400">Amount</p>
                <p className="font-medium">{formData.currency} {parseFloat(formData.amount || '0').toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Expiry</p>
                <p className="font-medium">{formData.expiry_date} ({formData.expiry_place})</p>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h4 className="text-sm font-medium text-secondary-500 mb-1">Description</h4>
            <p className="text-sm">{formData.description || 'N/A'}</p>
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
              Bank Guarantee created successfully! Redirecting...
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
          <h1 className="text-2xl font-bold text-secondary-900">Create Bank Guarantee</h1>
          <p className="text-sm text-secondary-500 mt-1">
            Fill in the details to create a new Bank Guarantee
          </p>
        </div>
        <button
          onClick={() => navigate('/guarantee')}
          className="btn-outline flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Guarantee List
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
