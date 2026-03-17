import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Save,
  Send,
  Building2,
  Globe,
  FileText,
  Calendar,
  DollarSign,
  Ship,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  Upload,
  X,
} from 'lucide-react'
import api from '@/api/axios'

// Types matching backend schema
interface LCFormData {
  // LC Type
  lc_type: 'import' | 'export' | 'standby' | 'transferable' | 'back_to_back' | 'confirmed'

  // Applicant (Importer)
  applicant_name: string
  applicant_address: string
  applicant_country: string

  // Beneficiary (Exporter)
  beneficiary_name: string
  beneficiary_address: string
  beneficiary_country: string

  // Issuing Bank
  issuing_bank_name: string
  issuing_bank_bic: string
  issuing_bank_address: string

  // Advising Bank
  advising_bank_name: string
  advising_bank_bic: string

  // Amount
  currency: string
  amount: string
  tolerance_percent: string

  // Dates
  expiry_date: string
  expiry_place: string
  last_shipment_date: string

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

  // Reference
  internal_reference: string
  external_reference: string

  // Additional options
  is_revokable: boolean
  is_confirmed: boolean
  ucp_version: string
  terms_conditions: string
}

interface FormErrors {
  [key: string]: string
}

const LC_TYPES = [
  { value: 'import', label: 'Import LC' },
  { value: 'export', label: 'Export LC' },
  { value: 'standby', label: 'Standby LC' },
  { value: 'transferable', label: 'Transferable LC' },
  { value: 'back_to_back', label: 'Back-to-Back LC' },
  { value: 'confirmed', label: 'Confirmed LC' },
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

const SHIPPING_TERMS = [
  { value: 'EXW', label: 'EXW - Ex Works' },
  { value: 'FOB', label: 'FOB - Free On Board' },
  { value: 'CIF', label: 'CIF - Cost, Insurance & Freight' },
  { value: 'CFR', label: 'CFR - Cost and Freight' },
  { value: 'DDP', label: 'DDP - Delivered Duty Paid' },
  { value: 'DAP', label: 'DAP - Delivered at Place' },
  { value: 'FCA', label: 'FCA - Free Carrier' },
  { value: 'CPT', label: 'CPT - Carriage Paid To' },
]

const initialFormData: LCFormData = {
  lc_type: 'import',
  applicant_name: '',
  applicant_address: '',
  applicant_country: '',
  beneficiary_name: '',
  beneficiary_address: '',
  beneficiary_country: '',
  issuing_bank_name: '',
  issuing_bank_bic: '',
  issuing_bank_address: '',
  advising_bank_name: '',
  advising_bank_bic: '',
  currency: 'USD',
  amount: '',
  tolerance_percent: '10.00',
  expiry_date: '',
  expiry_place: '',
  last_shipment_date: '',
  shipment_from: '',
  shipment_to: '',
  partial_shipment: false,
  transhipment: false,
  shipping_terms: '',
  description_goods: '',
  description_services: '',
  additional_conditions: '',
  documents_required: '',
  internal_reference: '',
  external_reference: '',
  is_revokable: false,
  is_confirmed: false,
  ucp_version: 'UCP 600',
  terms_conditions: '',
}

const STEPS = [
  { id: 1, title: 'LC Type', description: 'Select LC category' },
  { id: 2, title: 'Applicant & Beneficiary', description: 'Party details' },
  { id: 3, title: 'Bank Details', description: 'Issuing & advising banks' },
  { id: 4, title: 'Amount & Dates', description: 'Terms & validity' },
  { id: 5, title: 'Shipment', description: 'Shipping information' },
  { id: 6, title: 'Documents', description: 'Required documents' },
  { id: 7, title: 'Review', description: 'Confirm details' },
]

export default function LCCreate() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<LCFormData>(initialFormData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [submitSuccess, setSubmitSuccess] = useState(false)

  const updateField = (field: keyof LCFormData, value: string | boolean | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  const validateStep = (step: number): boolean => {
    const newErrors: FormErrors = {}

    switch (step) {
      case 1:
        if (!formData.lc_type) {
          newErrors.lc_type = 'LC Type is required'
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
        if (!formData.shipment_from.trim()) {
          newErrors.shipment_from = 'Shipment from is required'
        }
        if (!formData.shipment_to.trim()) {
          newErrors.shipment_to = 'Shipment to is required'
        }
        if (!formData.last_shipment_date) {
          newErrors.last_shipment_date = 'Last shipment date is required'
        }
        break
      case 6:
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

  const handleSubmit = async (saveAsDraft: boolean = false) => {
    if (!validateStep(7)) return

    setIsSubmitting(true)
    setSubmitError('')

    try {
      const payload = {
        ...formData,
        amount: parseFloat(formData.amount),
        tolerance_percent: parseFloat(formData.tolerance_percent),
        expiry_date: formData.expiry_date ? new Date(formData.expiry_date).toISOString() : null,
        last_shipment_date: formData.last_shipment_date ? new Date(formData.last_shipment_date).toISOString() : null,
      }

      const response = await api.post('/lc/', payload)
      
      if (response.data && response.data.id) {
        setSubmitSuccess(true)
        setTimeout(() => {
          navigate('/lc')
        }, 2000)
      }
    } catch (error: any) {
      console.error('LC Creation Error:', error)
      setSubmitError(
        error.response?.data?.detail || 
        error.response?.data?.message || 
        'Failed to create Letter of Credit. Please try again.'
      )
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
            <FileText className="w-5 h-5 mr-2 text-primary-600" />
            Letter of Credit Type
          </h3>
        </div>
        <div className="card-body">
          <p className="text-sm text-secondary-500 mb-4">
            Select the type of Letter of Credit that best matches your trade transaction requirements.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {LC_TYPES.map((type) => (
              <label
                key={type.value}
                className={`flex items-center p-4 border rounded-lg cursor-pointer transition-all ${
                  formData.lc_type === type.value
                    ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                    : 'border-secondary-200 hover:border-secondary-300 hover:bg-secondary-50'
                }`}
              >
                <input
                  type="radio"
                  name="lc_type"
                  value={type.value}
                  checked={formData.lc_type === type.value}
                  onChange={(e) => updateField('lc_type', e.target.value)}
                  className="sr-only"
                />
                <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 mr-3">
                  {formData.lc_type === type.value && (
                    <div className="w-2.5 h-2.5 rounded-full bg-primary-600" />
                  )}
                </div>
                <span className="font-medium text-secondary-900">{type.label}</span>
              </label>
            ))}
          </div>
          {errors.lc_type && (
            <p className="mt-2 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.lc_type}
            </p>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">UCP Rules & LC Options</h3>
        </div>
        <div className="card-body space-y-4">
          <div>
            <label className="label">UCP Version</label>
            <select
              value={formData.ucp_version}
              onChange={(e) => updateField('ucp_version', e.target.value)}
              className="input"
            >
              <option value="UCP 600">UCP 600 (Latest)</option>
              <option value="UCP 500">UCP 500</option>
            </select>
          </div>
          <div className="flex items-center space-x-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_revokable}
                onChange={(e) => updateField('is_revokable', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
              />
              <span className="ml-2 text-sm text-secondary-700">Revokable LC</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_confirmed}
                onChange={(e) => updateField('is_confirmed', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
              />
              <span className="ml-2 text-sm text-secondary-700">Confirmed LC</span>
            </label>
          </div>
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
            Applicant (Importer)
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
            Beneficiary (Exporter)
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

      {/* References */}
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
                placeholder="e.g., LC-2024-001"
              />
            </div>
            <div>
              <label className="label">External Reference</label>
              <input
                type="text"
                value={formData.external_reference}
                onChange={(e) => updateField('external_reference', e.target.value)}
                className="input"
                placeholder="Client reference number"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div className="space-y-6">
      {/* Issuing Bank */}
      <div className="card">
        <div className="card-header bg-primary-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Building2 className="w-5 h-5 mr-2 text-primary-600" />
            Issuing Bank
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
                BIC / SWIFT Code <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.issuing_bank_bic}
                onChange={(e) => updateField('issuing_bank_bic', e.target.value.toUpperCase())}
                className={`input ${errors.issuing_bank_bic ? 'border-red-500' : ''}`}
                placeholder="e.g., CHASUS33"
                maxLength={11}
              />
              {errors.issuing_bank_bic && (
                <p className="mt-1 text-sm text-red-600">{errors.issuing_bank_bic}</p>
              )}
            </div>
            <div>
              <label className="label">Branch Address</label>
              <input
                type="text"
                value={formData.issuing_bank_address}
                onChange={(e) => updateField('issuing_bank_address', e.target.value)}
                className="input"
                placeholder="Bank branch address"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Advising Bank */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Advising Bank (Optional)</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Bank Name</label>
              <input
                type="text"
                value={formData.advising_bank_name}
                onChange={(e) => updateField('advising_bank_name', e.target.value)}
                className="input"
                placeholder="Enter advising bank name"
              />
            </div>
            <div>
              <label className="label">BIC / SWIFT Code</label>
              <input
                type="text"
                value={formData.advising_bank_bic}
                onChange={(e) => updateField('advising_bank_bic', e.target.value.toUpperCase())}
                className="input"
                placeholder="e.g., DEUTDEFF"
                maxLength={11}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep4 = () => (
    <div className="space-y-6">
      {/* Amount */}
      <div className="card">
        <div className="card-header bg-yellow-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <DollarSign className="w-5 h-5 mr-2 text-yellow-600" />
            Amount & Currency
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">
                Currency <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.currency}
                onChange={(e) => updateField('currency', e.target.value)}
                className="input"
              >
                {CURRENCIES.map((currency) => (
                  <option key={currency} value={currency}>{currency}</option>
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
                placeholder="0.00"
                min="0"
                step="0.01"
              />
              {errors.amount && (
                <p className="mt-1 text-sm text-red-600">{errors.amount}</p>
              )}
            </div>
            <div>
              <label className="label">Tolerance (+/- %)</label>
              <input
                type="number"
                value={formData.tolerance_percent}
                onChange={(e) => updateField('tolerance_percent', e.target.value)}
                className="input"
                placeholder="10.00"
                min="0"
                max="100"
                step="0.01"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Validity */}
      <div className="card">
        <div className="card-header bg-purple-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-purple-600" />
            Validity Period
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                placeholder="e.g., New York, USA"
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
      {/* Shipment Details */}
      <div className="card">
        <div className="card-header bg-teal-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Ship className="w-5 h-5 mr-2 text-teal-600" />
            Shipment Details
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">
                Shipment From <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.shipment_from}
                onChange={(e) => updateField('shipment_from', e.target.value)}
                className={`input ${errors.shipment_from ? 'border-red-500' : ''}`}
                placeholder="Port or place of loading"
              />
              {errors.shipment_from && (
                <p className="mt-1 text-sm text-red-600">{errors.shipment_from}</p>
              )}
            </div>
            <div>
              <label className="label">
                Shipment To <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.shipment_to}
                onChange={(e) => updateField('shipment_to', e.target.value)}
                className={`input ${errors.shipment_to ? 'border-red-500' : ''}`}
                placeholder="Port or place of discharge"
              />
              {errors.shipment_to && (
                <p className="mt-1 text-sm text-red-600">{errors.shipment_to}</p>
              )}
            </div>
            <div>
              <label className="label">
                Last Shipment Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.last_shipment_date}
                onChange={(e) => updateField('last_shipment_date', e.target.value)}
                className={`input ${errors.last_shipment_date ? 'border-red-500' : ''}`}
              />
              {errors.last_shipment_date && (
                <p className="mt-1 text-sm text-red-600">{errors.last_shipment_date}</p>
              )}
            </div>
            <div>
              <label className="label">Incoterms</label>
              <select
                value={formData.shipping_terms}
                onChange={(e) => updateField('shipping_terms', e.target.value)}
                className="input"
              >
                <option value="">Select shipping terms</option>
                {SHIPPING_TERMS.map((term) => (
                  <option key={term.value} value={term.value}>{term.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4 flex items-center space-x-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.partial_shipment}
                onChange={(e) => updateField('partial_shipment', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
              />
              <span className="ml-2 text-sm text-secondary-700">Partial Shipment Allowed</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.transhipment}
                onChange={(e) => updateField('transhipment', e.target.checked)}
                className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
              />
              <span className="ml-2 text-sm text-secondary-700">Transhipment Allowed</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep6 = () => (
    <div className="space-y-6">
      {/* Description */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-primary-600" />
            Description of Goods / Services
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="label">Description of Goods</label>
              <textarea
                value={formData.description_goods}
                onChange={(e) => updateField('description_goods', e.target.value)}
                className={`input min-h-[120px] ${errors.description_goods ? 'border-red-500' : ''}`}
                placeholder="Detailed description of goods to be shipped..."
              />
              {errors.description_goods && (
                <p className="mt-1 text-sm text-red-600">{errors.description_goods}</p>
              )}
            </div>
            <div>
              <label className="label">Description of Services (if applicable)</label>
              <textarea
                value={formData.description_services}
                onChange={(e) => updateField('description_services', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Description of services if this is a service LC..."
              />
            </div>
          </div>
        </div>
      </div>

      {/* Documents Required */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Documents Required</h3>
        </div>
        <div className="card-body">
          <textarea
            value={formData.documents_required}
            onChange={(e) => updateField('documents_required', e.target.value)}
            className="input min-h-[120px]"
            placeholder="List of documents required under this LC (e.g., Bill of Lading, Commercial Invoice, Certificate of Origin, etc.)"
          />
        </div>
      </div>

      {/* Additional Conditions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Additional Conditions</h3>
        </div>
        <div className="card-body">
          <textarea
            value={formData.additional_conditions}
            onChange={(e) => updateField('additional_conditions', e.target.value)}
            className="input min-h-[100px]"
            placeholder="Any special conditions or instructions..."
          />
        </div>
      </div>

      {/* Terms & Conditions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Terms & Conditions</h3>
        </div>
        <div className="card-body">
          <textarea
            value={formData.terms_conditions}
            onChange={(e) => updateField('terms_conditions', e.target.value)}
            className="input min-h-[100px]"
            placeholder="Additional terms and conditions for this LC..."
          />
        </div>
      </div>
    </div>
  )

  const renderStep7 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header bg-green-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
            Review Letter of Credit Details
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* LC Type */}
            <div className="p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">LC Type</p>
              <p className="text-sm font-semibold text-secondary-900 mt-1">
                {LC_TYPES.find(t => t.value === formData.lc_type)?.label}
              </p>
              <p className="text-xs text-secondary-500 mt-1">
                UCP Version: {formData.ucp_version} | 
                {formData.is_revokable ? ' Revokable' : ' Irrevokable'}
                {formData.is_confirmed ? ' | Confirmed' : ''}
              </p>
            </div>

            {/* Amount */}
            <div className="p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">Amount</p>
              <p className="text-lg font-semibold text-secondary-900 mt-1">
                {formData.currency} {parseFloat(formData.amount || '0').toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-secondary-500 mt-1">
                Tolerance: ±{formData.tolerance_percent}%
              </p>
            </div>

            {/* Applicant */}
            <div className="p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">Applicant</p>
              <p className="text-sm font-semibold text-secondary-900 mt-1">{formData.applicant_name}</p>
              <p className="text-xs text-secondary-500 mt-1">{formData.applicant_country}</p>
            </div>

            {/* Beneficiary */}
            <div className="p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">Beneficiary</p>
              <p className="text-sm font-semibold text-secondary-900 mt-1">{formData.beneficiary_name}</p>
              <p className="text-xs text-secondary-500 mt-1">{formData.beneficiary_country}</p>
            </div>

            {/* Issuing Bank */}
            <div className="p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">Issuing Bank</p>
              <p className="text-sm font-semibold text-secondary-900 mt-1">{formData.issuing_bank_name}</p>
              <p className="text-xs text-secondary-500 mt-1">SWIFT: {formData.issuing_bank_bic}</p>
            </div>

            {/* Validity */}
            <div className="p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">Validity</p>
              <p className="text-sm font-semibold text-secondary-900 mt-1">
                Expires: {formData.expiry_date ? new Date(formData.expiry_date).toLocaleDateString() : 'N/A'}
              </p>
              <p className="text-xs text-secondary-500 mt-1">Place: {formData.expiry_place}</p>
            </div>

            {/* Shipment */}
            <div className="p-4 bg-secondary-50 rounded-lg md:col-span-2">
              <p className="text-xs font-medium text-secondary-500 uppercase">Shipment</p>
              <p className="text-sm font-semibold text-secondary-900 mt-1">
                From: {formData.shipment_from} → To: {formData.shipment_to}
              </p>
              <p className="text-xs text-secondary-500 mt-1">
                Last Shipment: {formData.last_shipment_date ? new Date(formData.last_shipment_date).toLocaleDateString() : 'N/A'}
                {formData.shipping_terms ? ` | Incoterms: ${formData.shipping_terms}` : ''}
                {formData.partial_shipment ? ' | Partial: Yes' : ''}
                {formData.transhipment ? ' | Transhipment: Yes' : ''}
              </p>
            </div>
          </div>

          {formData.description_goods && (
            <div className="mt-4 p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">Description of Goods</p>
              <p className="text-sm text-secondary-700 mt-1">{formData.description_goods}</p>
            </div>
          )}

          {formData.documents_required && (
            <div className="mt-4 p-4 bg-secondary-50 rounded-lg">
              <p className="text-xs font-medium text-secondary-500 uppercase">Documents Required</p>
              <p className="text-sm text-secondary-700 mt-1">{formData.documents_required}</p>
            </div>
          )}
        </div>
      </div>

      {/* Error Message */}
      {submitError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-2" />
            {submitError}
          </p>
        </div>
      )}
    </div>
  )

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderStep1()
      case 2:
        return renderStep2()
      case 3:
        return renderStep3()
      case 4:
        return renderStep4()
      case 5:
        return renderStep5()
      case 6:
        return renderStep6()
      case 7:
        return renderStep7()
      default:
        return null
    }
  }

  if (submitSuccess) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-secondary-900">Letter of Credit Created Successfully</h2>
          <p className="text-secondary-500 mt-2">Redirecting to LC list...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/lc')}
            className="mr-4 p-2 text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">Create Letter of Credit</h1>
            <p className="text-sm text-secondary-500 mt-1">
              Complete all required information to issue a new LC
            </p>
          </div>
        </div>
      </div>

      {/* Step Indicator */}
      {renderStepIndicator()}

      {/* Form Content */}
      <div className="min-h-[400px]">
        {renderCurrentStep()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4 border-t border-secondary-200">
        <div>
          {currentStep > 1 && (
            <button
              onClick={handleBack}
              className="btn-secondary flex items-center"
              disabled={isSubmitting}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Previous
            </button>
          )}
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => handleSubmit(true)}
            className="btn-outline flex items-center"
            disabled={isSubmitting}
          >
            <Save className="w-4 h-4 mr-2" />
            Save as Draft
          </button>
          {currentStep < 7 ? (
            <button
              onClick={handleNext}
              className="btn-primary flex items-center"
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              onClick={() => handleSubmit(false)}
              className="btn-primary flex items-center bg-green-600 hover:bg-green-700"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Submit for Approval
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
