import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Banknote,
  Building2,
  Globe,
  DollarSign,
  Calendar,
  Percent,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  Send,
} from 'lucide-react'
import api from '@/api/axios'

// Types matching backend schema
interface LoanFormData {
  // Loan Type
  loan_type: 'term_loan' | 'revolving_loan' | 'trade_finance' | 'working_capital' | 'project_finance' | 'bridge_loan'

  // Borrower
  borrower_name: string
  borrower_address: string
  borrower_country: string
  borrower_tax_id: string
  borrower_registration_no: string

  // Lender Bank
  lender_bank_name: string
  lender_bank_bic: string
  lender_bank_address: string

  // Loan Amount
  currency: string
  principal_amount: string
  interest_rate: string
  interest_type: 'fixed' | 'floating'
  interest_rate_margin: string

  // Dates
  disbursement_date: string
  maturity_date: string
  first_repayment_date: string

  // Repayment Terms
  repayment_frequency: 'monthly' | 'quarterly' | 'semi_annual' | 'annual' | 'bullet'
  repayment_type: 'equal_installments' | 'bullet' | 'custom'
  number_of_installments: string

  // Security/Collateral
  collateral_description: string
  collateral_value: string

  // Purpose
  loan_purpose: string
  underlying_transaction_ref: string

  // Reference
  internal_reference: string
  external_reference: string

  // Additional
  special_conditions: string
}

interface FormErrors {
  [key: string]: string
}

const LOAN_TYPES = [
  { value: 'term_loan', label: 'Term Loan' },
  { value: 'revolving_loan', label: 'Revolving Loan' },
  { value: 'trade_finance', label: 'Trade Finance' },
  { value: 'working_capital', label: 'Working Capital' },
  { value: 'project_finance', label: 'Project Finance' },
  { value: 'bridge_loan', label: 'Bridge Loan' },
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

const REPAYMENT_FREQUENCIES = [
  { value: 'monthly', label: 'Monthly' },
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'semi_annual', label: 'Semi-Annual' },
  { value: 'annual', label: 'Annual' },
  { value: 'bullet', label: 'Bullet (One-time)' },
]

const REPAYMENT_TYPES = [
  { value: 'equal_installments', label: 'Equal Installments' },
  { value: 'bullet', label: 'Bullet Payment' },
  { value: 'custom', label: 'Custom Schedule' },
]

const INTEREST_TYPES = [
  { value: 'fixed', label: 'Fixed Rate' },
  { value: 'floating', label: 'Floating Rate' },
]

const initialFormData: LoanFormData = {
  loan_type: 'term_loan',
  borrower_name: '',
  borrower_address: '',
  borrower_country: '',
  borrower_tax_id: '',
  borrower_registration_no: '',
  lender_bank_name: '',
  lender_bank_bic: '',
  lender_bank_address: '',
  currency: 'USD',
  principal_amount: '',
  interest_rate: '',
  interest_type: 'fixed',
  interest_rate_margin: '',
  disbursement_date: '',
  maturity_date: '',
  first_repayment_date: '',
  repayment_frequency: 'monthly',
  repayment_type: 'equal_installments',
  number_of_installments: '',
  collateral_description: '',
  collateral_value: '',
  loan_purpose: '',
  underlying_transaction_ref: '',
  internal_reference: '',
  external_reference: '',
  special_conditions: '',
}

const STEPS = [
  { id: 1, title: 'Loan Type', description: 'Select loan category' },
  { id: 2, title: 'Borrower Details', description: 'Borrower information' },
  { id: 3, title: 'Lender Details', description: 'Lender bank information' },
  { id: 4, title: 'Amount & Interest', description: 'Terms & rates' },
  { id: 5, title: 'Repayment', description: 'Repayment schedule' },
  { id: 6, title: 'Review', description: 'Confirm details' },
]

export default function LoanCreate() {
  const { id } = useParams<{ id: string }>()
  const isEditMode = Boolean(id)
  
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<LoanFormData>(initialFormData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Fetch loan data for edit mode
  useEffect(() => {
    if (!id) return
    
    const fetchLoan = async () => {
      setIsLoading(true)
      try {
        const response = await api.get(`/loan/loans/${id}`)
        const loan = response.data
        setFormData({
          loan_type: loan.loan_type || 'term_loan',
          borrower_name: loan.borrower_name || '',
          borrower_address: loan.borrower_address || '',
          borrower_country: loan.borrower_country || '',
          borrower_tax_id: loan.borrower_tax_id || '',
          borrower_registration_no: loan.borrower_registration_no || '',
          lender_bank_name: loan.lender_bank_name || '',
          lender_bank_bic: loan.lender_bank_bic || '',
          lender_bank_address: loan.lender_bank_address || '',
          currency: loan.currency || 'USD',
          principal_amount: String(loan.amount || loan.principal_amount || ''),
          interest_rate: String(loan.interest_rate || ''),
          interest_type: loan.interest_type || 'fixed',
          interest_rate_margin: String(loan.interest_rate_margin || ''),
          disbursement_date: loan.disbursement_date || '',
          maturity_date: loan.maturity_date || '',
          first_repayment_date: loan.first_repayment_date || '',
          repayment_frequency: loan.repayment_frequency || 'monthly',
          repayment_type: loan.repayment_type || 'equal_installments',
          number_of_installments: String(loan.number_of_installments || ''),
          collateral_description: loan.collateral_description || '',
          collateral_value: String(loan.collateral_value || ''),
          loan_purpose: loan.loan_purpose || '',
          underlying_transaction_ref: loan.underlying_transaction_ref || '',
          internal_reference: loan.internal_reference || '',
          external_reference: loan.external_reference || '',
          special_conditions: loan.special_conditions || '',
        })
      } catch (err) {
        console.error('Error fetching loan:', err)
        setSubmitError('Failed to load loan data')
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchLoan()
  }, [id])

  const updateField = (field: keyof LoanFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  const validateStep = (step: number): boolean => {
    const newErrors: FormErrors = {}

    switch (step) {
      case 1:
        if (!formData.loan_type) {
          newErrors.loan_type = 'Loan Type is required'
        }
        if (!formData.loan_purpose.trim()) {
          newErrors.loan_purpose = 'Loan purpose is required'
        }
        break
      case 2:
        if (!formData.borrower_name.trim()) {
          newErrors.borrower_name = 'Borrower name is required'
        }
        if (!formData.borrower_country) {
          newErrors.borrower_country = 'Borrower country is required'
        }
        break
      case 3:
        if (!formData.lender_bank_name.trim()) {
          newErrors.lender_bank_name = 'Lender bank name is required'
        }
        if (!formData.lender_bank_bic.trim()) {
          newErrors.lender_bank_bic = 'Bank BIC/SWIFT code is required'
        }
        break
      case 4:
        if (!formData.principal_amount || parseFloat(formData.principal_amount) <= 0) {
          newErrors.principal_amount = 'Valid principal amount is required'
        }
        if (!formData.interest_rate || parseFloat(formData.interest_rate) < 0) {
          newErrors.interest_rate = 'Interest rate is required'
        }
        if (!formData.maturity_date) {
          newErrors.maturity_date = 'Maturity date is required'
        }
        break
      case 5:
        if (!formData.disbursement_date) {
          newErrors.disbursement_date = 'Disbursement date is required'
        }
        if (!formData.repayment_frequency) {
          newErrors.repayment_frequency = 'Repayment frequency is required'
        }
        if (!formData.number_of_installments && formData.repayment_frequency !== 'bullet') {
          newErrors.number_of_installments = 'Number of installments is required'
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
        principal_amount: parseFloat(formData.principal_amount),
        interest_rate: parseFloat(formData.interest_rate),
        interest_rate_margin: formData.interest_rate_margin ? parseFloat(formData.interest_rate_margin) : null,
        collateral_value: formData.collateral_value ? parseFloat(formData.collateral_value) : null,
        number_of_installments: formData.number_of_installments ? parseInt(formData.number_of_installments) : null,
        disbursement_date: formData.disbursement_date ? new Date(formData.disbursement_date).toISOString() : null,
        maturity_date: formData.maturity_date ? new Date(formData.maturity_date).toISOString() : null,
        first_repayment_date: formData.first_repayment_date ? new Date(formData.first_repayment_date).toISOString() : null,
      }

      const response = await api.post('/loan/loans/', payload)
      
      if (response.data && response.data.id) {
        setSubmitSuccess(true)
        setTimeout(() => {
          navigate('/loan')
        }, 2000)
      }
    } catch (error: any) {
      console.error('Loan Creation Error:', error)
      const errorData = error.response?.data
      let errorMessage = 'Failed to create Trade Loan. Please try again.'
      
      if (errorData?.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (Array.isArray(errorData.detail)) {
          // Handle FastAPI validation error array
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
            <Banknote className="w-5 h-5 mr-2 text-primary-600" />
            Loan Type
          </h3>
        </div>
        <div className="card-body">
          <p className="text-sm text-secondary-500 mb-4">
            Select the type of Trade Loan that best matches your financing requirements.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {LOAN_TYPES.map((type) => (
              <label
                key={type.value}
                className={`flex items-center p-4 border rounded-lg cursor-pointer transition-all ${
                  formData.loan_type === type.value
                    ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                    : 'border-secondary-200 hover:border-secondary-300 hover:bg-secondary-50'
                }`}
              >
                <input
                  type="radio"
                  name="loan_type"
                  value={type.value}
                  checked={formData.loan_type === type.value}
                  onChange={(e) => updateField('loan_type', e.target.value as LoanFormData['loan_type'])}
                  className="sr-only"
                />
                <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 mr-3">
                  {formData.loan_type === type.value && (
                    <div className="w-2.5 h-2.5 rounded-full bg-primary-600" />
                  )}
                </div>
                <span className="font-medium text-secondary-900">{type.label}</span>
              </label>
            ))}
          </div>
          {errors.loan_type && (
            <p className="mt-2 text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.loan_type}
            </p>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Loan Purpose</h3>
        </div>
        <div className="card-body">
          <div>
            <label className="label">
              Purpose of Loan <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.loan_purpose}
              onChange={(e) => updateField('loan_purpose', e.target.value)}
              className={`input min-h-[100px] ${errors.loan_purpose ? 'border-red-500' : ''}`}
              placeholder="Describe the purpose of this loan"
            />
            {errors.loan_purpose && (
              <p className="mt-1 text-sm text-red-600">{errors.loan_purpose}</p>
            )}
          </div>
          <div className="mt-4">
            <label className="label">Underlying Transaction Reference</label>
            <input
              type="text"
              value={formData.underlying_transaction_ref}
              onChange={(e) => updateField('underlying_transaction_ref', e.target.value)}
              className="input"
              placeholder="Reference to related transaction (LC, guarantee, etc.)"
            />
          </div>
        </div>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header bg-blue-50">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Building2 className="w-5 h-5 mr-2 text-blue-600" />
            Borrower Details
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
                value={formData.borrower_name}
                onChange={(e) => updateField('borrower_name', e.target.value)}
                className={`input ${errors.borrower_name ? 'border-red-500' : ''}`}
                placeholder="Enter borrower company name"
              />
              {errors.borrower_name && (
                <p className="mt-1 text-sm text-red-600">{errors.borrower_name}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Address</label>
              <textarea
                value={formData.borrower_address}
                onChange={(e) => updateField('borrower_address', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Enter registered address"
              />
            </div>
            <div>
              <label className="label">Registration Number</label>
              <input
                type="text"
                value={formData.borrower_registration_no}
                onChange={(e) => updateField('borrower_registration_no', e.target.value)}
                className="input"
                placeholder="Company registration number"
              />
            </div>
            <div>
              <label className="label">Tax ID</label>
              <input
                type="text"
                value={formData.borrower_tax_id}
                onChange={(e) => updateField('borrower_tax_id', e.target.value)}
                className="input"
                placeholder="Tax identification number"
              />
            </div>
            <div>
              <label className="label">
                Country <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.borrower_country}
                onChange={(e) => updateField('borrower_country', e.target.value)}
                className={`input ${errors.borrower_country ? 'border-red-500' : ''}`}
              >
                <option value="">Select country</option>
                {COUNTRIES.map((country) => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              {errors.borrower_country && (
                <p className="mt-1 text-sm text-red-600">{errors.borrower_country}</p>
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
            Lender Bank Details
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
                value={formData.lender_bank_name}
                onChange={(e) => updateField('lender_bank_name', e.target.value)}
                className={`input ${errors.lender_bank_name ? 'border-red-500' : ''}`}
                placeholder="Enter lender bank name"
              />
              {errors.lender_bank_name && (
                <p className="mt-1 text-sm text-red-600">{errors.lender_bank_name}</p>
              )}
            </div>
            <div>
              <label className="label">
                BIC/SWIFT Code <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.lender_bank_bic}
                onChange={(e) => updateField('lender_bank_bic', e.target.value)}
                className={`input ${errors.lender_bank_bic ? 'border-red-500' : ''}`}
                placeholder="e.g., DEUTDEFF"
              />
              {errors.lender_bank_bic && (
                <p className="mt-1 text-sm text-red-600">{errors.lender_bank_bic}</p>
              )}
            </div>
            <div className="md:col-span-2">
              <label className="label">Bank Address</label>
              <textarea
                value={formData.lender_bank_address}
                onChange={(e) => updateField('lender_bank_address', e.target.value)}
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
            Loan Amount
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
                Principal Amount <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.principal_amount}
                onChange={(e) => updateField('principal_amount', e.target.value)}
                className={`input ${errors.principal_amount ? 'border-red-500' : ''}`}
                placeholder="Enter loan amount"
                min="0"
                step="0.01"
              />
              {errors.principal_amount && (
                <p className="mt-1 text-sm text-red-600">{errors.principal_amount}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Percent className="w-5 h-5 mr-2 text-primary-600" />
            Interest Rate
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Interest Type</label>
              <select
                value={formData.interest_type}
                onChange={(e) => updateField('interest_type', e.target.value as LoanFormData['interest_type'])}
                className="input"
              >
                {INTEREST_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">
                Interest Rate (%) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={formData.interest_rate}
                onChange={(e) => updateField('interest_rate', e.target.value)}
                className={`input ${errors.interest_rate ? 'border-red-500' : ''}`}
                placeholder="e.g., 5.5"
                min="0"
                step="0.01"
              />
              {errors.interest_rate && (
                <p className="mt-1 text-sm text-red-600">{errors.interest_rate}</p>
              )}
            </div>
            <div>
              <label className="label">Margin (%)</label>
              <input
                type="number"
                value={formData.interest_rate_margin}
                onChange={(e) => updateField('interest_rate_margin', e.target.value)}
                className="input"
                placeholder="e.g., 1.5"
                min="0"
                step="0.01"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-primary-600" />
            Loan Term
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">
                Disbursement Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.disbursement_date}
                onChange={(e) => updateField('disbursement_date', e.target.value)}
                className={`input ${errors.disbursement_date ? 'border-red-500' : ''}`}
              />
              {errors.disbursement_date && (
                <p className="mt-1 text-sm text-red-600">{errors.disbursement_date}</p>
              )}
            </div>
            <div>
              <label className="label">
                Maturity Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.maturity_date}
                onChange={(e) => updateField('maturity_date', e.target.value)}
                className={`input ${errors.maturity_date ? 'border-red-500' : ''}`}
              />
              {errors.maturity_date && (
                <p className="mt-1 text-sm text-red-600">{errors.maturity_date}</p>
              )}
            </div>
            <div>
              <label className="label">First Repayment Date</label>
              <input
                type="date"
                value={formData.first_repayment_date}
                onChange={(e) => updateField('first_repayment_date', e.target.value)}
                className="input"
              />
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
          <h3 className="text-lg font-semibold text-secondary-900">Repayment Terms</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">
                Repayment Frequency <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.repayment_frequency}
                onChange={(e) => updateField('repayment_frequency', e.target.value as LoanFormData['repayment_frequency'])}
                className={`input ${errors.repayment_frequency ? 'border-red-500' : ''}`}
              >
                {REPAYMENT_FREQUENCIES.map((freq) => (
                  <option key={freq.value} value={freq.value}>{freq.label}</option>
                ))}
              </select>
              {errors.repayment_frequency && (
                <p className="mt-1 text-sm text-red-600">{errors.repayment_frequency}</p>
              )}
            </div>
            <div>
              <label className="label">Repayment Type</label>
              <select
                value={formData.repayment_type}
                onChange={(e) => updateField('repayment_type', e.target.value as LoanFormData['repayment_type'])}
                className="input"
              >
                {REPAYMENT_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">
                {formData.repayment_frequency === 'bullet' ? 'Loan Tenor (Months)' : 'Number of Installments'}
              </label>
              <input
                type="number"
                value={formData.number_of_installments}
                onChange={(e) => updateField('number_of_installments', e.target.value)}
                className={`input ${errors.number_of_installments ? 'border-red-500' : ''}`}
                placeholder={formData.repayment_frequency === 'bullet' ? 'e.g., 12' : 'e.g., 24'}
                min="1"
              />
              {errors.number_of_installments && (
                <p className="mt-1 text-sm text-red-600">{errors.number_of_installments}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Collateral/Security</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Collateral Description</label>
              <textarea
                value={formData.collateral_description}
                onChange={(e) => updateField('collateral_description', e.target.value)}
                className="input min-h-[100px]"
                placeholder="Describe the collateral/security"
              />
            </div>
            <div>
              <label className="label">Collateral Value</label>
              <input
                type="number"
                value={formData.collateral_value}
                onChange={(e) => updateField('collateral_value', e.target.value)}
                className="input"
                placeholder="Value of collateral"
                min="0"
                step="0.01"
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
              <label className="label">Special Conditions</label>
              <textarea
                value={formData.special_conditions}
                onChange={(e) => updateField('special_conditions', e.target.value)}
                className="input min-h-[80px]"
                placeholder="Any special conditions or covenants"
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
          <h3 className="text-lg font-semibold text-secondary-900">Review Trade Loan</h3>
        </div>
        <div className="card-body space-y-6">
          {/* Type & Purpose */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-1">Loan Type</h4>
            <p className="font-medium">{LOAN_TYPES.find(t => t.value === formData.loan_type)?.label}</p>
            <p className="text-sm text-secondary-500 mt-1">{formData.loan_purpose}</p>
          </div>

          {/* Borrower */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Borrower</h4>
            <p className="font-medium">{formData.borrower_name}</p>
            <p className="text-sm text-secondary-500">{formData.borrower_country}</p>
          </div>

          {/* Lender */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Lender Bank</h4>
            <p className="font-medium">{formData.lender_bank_name}</p>
            <p className="text-sm text-secondary-500">{formData.lender_bank_bic}</p>
          </div>

          {/* Amount & Interest */}
          <div className="border-b border-secondary-200 pb-4">
            <h4 className="text-sm font-medium text-secondary-500 mb-2">Amount & Interest</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-secondary-400">Principal</p>
                <p className="font-medium">{formData.currency} {parseFloat(formData.principal_amount || '0').toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Interest Rate</p>
                <p className="font-medium">{formData.interest_rate}% {formData.interest_type === 'fixed' ? '(Fixed)' : '(Floating)'}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Disbursement</p>
                <p className="font-medium">{formData.disbursement_date}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-400">Maturity</p>
                <p className="font-medium">{formData.maturity_date}</p>
              </div>
            </div>
          </div>

          {/* Repayment */}
          <div>
            <h4 className="text-sm font-medium text-secondary-500 mb-1">Repayment Terms</h4>
            <p className="font-medium">
              {REPAYMENT_FREQUENCIES.find(f => f.value === formData.repayment_frequency)?.label} - 
              {REPAYMENT_TYPES.find(t => t.value === formData.repayment_type)?.label}
              {formData.number_of_installments && ` (${formData.number_of_installments} installments)`}
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
              Trade Loan created successfully! Redirecting...
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
          <h1 className="text-2xl font-bold text-secondary-900">{isEditMode ? 'Edit Trade Loan' : 'Create Trade Loan'}</h1>
          <p className="text-sm text-secondary-500 mt-1">
            Fill in the details to create a new Trade Finance Loan
          </p>
        </div>
        <button
          onClick={() => navigate('/loan')}
          className="btn-outline flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Loan List
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
