import { useState, useEffect } from 'react'
import { 
  Upload, 
  FileText, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Loader2,
  Brain,
  Eye,
  Search,
  MessageSquare,
  FileCheck,
  AlertCircle,
  RefreshCw
} from 'lucide-react'
import api from '@/api/axios'

interface AnalysisResult {
  status: 'success' | 'error'
  document_type?: string
  extracted_text?: string
  extracted_fields?: Record<string, any>
  analysis?: string
  discrepancies?: any[]
  compliance_report?: string
  summary?: string
}

export default function AIDocumentProcessor() {
  const [file, setFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [activeTab, setActiveTab] = useState<'ocr' | 'classify' | 'analyze' | 'compliance' | 'discrepancy'>('ocr')
  const [documentText, setDocumentText] = useState('')
  const [referenceText, setReferenceText] = useState('')
  const [showDiscrepancyForm, setShowDiscrepancyForm] = useState(false)
  const [engineStatus, setEngineStatus] = useState<Record<string, string>>({})

  useEffect(() => {
    checkEngineStatus()
  }, [])

  const checkEngineStatus = async () => {
    try {
      const response = await api.get('/smart-engines/health')
      setEngineStatus(response.data.services)
    } catch (error) {
      console.error('Failed to check engine status:', error)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResult(null)
    }
  }

  const handleOCR = async () => {
    if (!file) return
    
    setIsAnalyzing(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/smart-engines/ocr/analyze-document', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setResult({
        status: 'success',
        extracted_text: response.data.full_text,
        extracted_fields: response.data.extracted_fields,
        document_type: response.data.document_type
      })
    } catch (error: any) {
      setResult({
        status: 'error',
        ...error.response?.data
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleClassify = async () => {
    if (!documentText) return
    
    setIsAnalyzing(true)
    try {
      const response = await api.post('/smart-engines/classify/document', {
        text: documentText
      })
      
      setResult({
        status: 'success',
        document_type: response.data.document_type,
        analysis: response.data.justification
      })
    } catch (error: any) {
      setResult({
        status: 'error',
        ...error.response?.data
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleAnalyzeClauses = async () => {
    if (!documentText) return
    
    setIsAnalyzing(true)
    try {
      const response = await api.post('/smart-engines/analyze/clauses', {
        text: documentText
      })
      
      setResult({
        status: 'success',
        analysis: response.data.analysis
      })
    } catch (error: any) {
      setResult({
        status: 'error',
        ...error.response?.data
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleComplianceCheck = async () => {
    if (!documentText) return
    
    setIsAnalyzing(true)
    try {
      const response = await api.post('/smart-engines/compliance/check', {
        text: documentText,
        policies: 'Standard trade finance compliance policies'
      })
      
      setResult({
        status: 'success',
        compliance_report: response.data.compliance_report
      })
    } catch (error: any) {
      setResult({
        status: 'error',
        ...error.response?.data
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleDiscrepancyCheck = async () => {
    if (!documentText || !referenceText) return
    
    setIsAnalyzing(true)
    try {
      const response = await api.post('/smart-engines/discrepancy/detect', {
        document: { text: documentText },
        reference: { text: referenceText }
      })
      
      setResult({
        status: 'success',
        discrepancies: response.data.discrepancies
      })
    } catch (error: any) {
      setResult({
        status: 'error',
        ...error.response?.data
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleGenerateSummary = async () => {
    if (!documentText) return
    
    setIsAnalyzing(true)
    try {
      const response = await api.post('/smart-engines/generate/summary', {
        text: documentText
      })
      
      setResult({
        status: 'success',
        summary: response.data.summary
      })
    } catch (error: any) {
      setResult({
        status: 'error',
        ...error.response?.data
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">AI Document Processor</h1>
          <p className="text-sm text-secondary-500 mt-1">
            Smart engines for trade finance document processing
          </p>
        </div>
        <button onClick={checkEngineStatus} className="btn-outline flex items-center">
          <RefreshCw className="w-4 h-4 mr-2" /> Refresh Status
        </button>
      </div>

      {/* Engine Status */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium">Engine Status</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center p-3 bg-secondary-50 rounded-lg">
              <Eye className="w-5 h-5 text-blue-500 mr-3" />
              <div>
                <p className="text-sm font-medium">OCR</p>
                <p className="text-xs text-green-600">{engineStatus.ocr || 'Loading...'}</p>
              </div>
            </div>
            <div className="flex items-center p-3 bg-secondary-50 rounded-lg">
              <Brain className="w-5 h-5 text-purple-500 mr-3" />
              <div>
                <p className="text-sm font-medium">Ollama</p>
                <p className="text-xs text-green-600">{engineStatus.ollama || 'Loading...'}</p>
              </div>
            </div>
            <div className="flex items-center p-3 bg-secondary-50 rounded-lg">
              <Shield className="w-5 h-5 text-green-500 mr-3" />
              <div>
                <p className="text-sm font-medium">Compliance</p>
                <p className="text-xs text-green-600">{engineStatus.compliance || 'Loading...'}</p>
              </div>
            </div>
            <div className="flex items-center p-3 bg-secondary-50 rounded-lg">
              <Search className="w-5 h-5 text-orange-500 mr-3" />
              <div>
                <p className="text-sm font-medium">Discrepancy</p>
                <p className="text-xs text-green-600">{engineStatus.discrepancy || 'Loading...'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-secondary-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'ocr', label: 'OCR & Extraction', icon: Eye },
            { id: 'classify', label: 'Classification', icon: FileText },
            { id: 'analyze', label: 'Clause Analysis', icon: MessageSquare },
            { id: 'compliance', label: 'Compliance', icon: Shield },
            { id: 'discrepancy', label: 'Discrepancy Detection', icon: AlertTriangle },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as any)
                setResult(null)
                setShowDiscrepancyForm(false)
              }}
              className={`
                flex items-center py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }
              `}
            >
              <tab.icon className="w-5 h-5 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="card">
        <div className="card-body">
          {/* OCR Tab */}
          {activeTab === 'ocr' && (
            <div className="space-y-4">
              <div className="flex items-center justify-center w-full">
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-secondary-300 border-dashed rounded-lg cursor-pointer bg-secondary-50 hover:bg-secondary-100">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="w-8 h-8 mb-3 text-secondary-400" />
                    <p className="text-sm text-secondary-500">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-secondary-400">PDF, PNG, JPG (max 10MB)</p>
                  </div>
                  <input type="file" className="hidden" onChange={handleFileSelect} accept=".pdf,.png,.jpg,.jpeg" />
                </label>
              </div>
              
              {file && (
                <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-secondary-500 mr-2" />
                    <span className="text-sm font-medium">{file.name}</span>
                  </div>
                  <button onClick={handleOCR} disabled={isAnalyzing} className="btn-primary">
                    {isAnalyzing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</> : 'Extract Text'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Classification & Analysis Tabs */}
          {['classify', 'analyze', 'compliance'].includes(activeTab) && (
            <div className="space-y-4">
              <div>
                <label className="label">Document Text</label>
                <textarea
                  value={documentText}
                  onChange={(e) => setDocumentText(e.target.value)}
                  rows={8}
                  className="input"
                  placeholder="Paste document text here for analysis..."
                />
              </div>
              
              <div className="flex space-x-3">
                {activeTab === 'classify' && (
                  <button onClick={handleClassify} disabled={isAnalyzing || !documentText} className="btn-primary">
                    {isAnalyzing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</> : 'Classify Document'}
                  </button>
                )}
                {activeTab === 'analyze' && (
                  <button onClick={handleAnalyzeClauses} disabled={isAnalyzing || !documentText} className="btn-primary">
                    {isAnalyzing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</> : 'Analyze Clauses'}
                  </button>
                )}
                {activeTab === 'compliance' && (
                  <button onClick={handleComplianceCheck} disabled={isAnalyzing || !documentText} className="btn-primary">
                    {isAnalyzing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</> : 'Check Compliance'}
                  </button>
                )}
                <button onClick={handleGenerateSummary} disabled={isAnalyzing || !documentText} className="btn-secondary">
                  Generate Summary
                </button>
              </div>
            </div>
          )}

          {/* Discrepancy Tab */}
          {activeTab === 'discrepancy' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Document to Check</label>
                  <textarea
                    value={documentText}
                    onChange={(e) => setDocumentText(e.target.value)}
                    rows={6}
                    className="input"
                    placeholder="Enter document text..."
                  />
                </div>
                <div>
                  <label className="label">Reference Document</label>
                  <textarea
                    value={referenceText}
                    onChange={(e) => setReferenceText(e.target.value)}
                    rows={6}
                    className="input"
                    placeholder="Enter reference text..."
                  />
                </div>
              </div>
              
              <button onClick={handleDiscrepancyCheck} disabled={isAnalyzing || !documentText || !referenceText} className="btn-primary">
                {isAnalyzing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</> : 'Detect Discrepancies'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="card border-primary-200">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-medium">Analysis Results</h3>
            {result.status === 'success' ? (
              <span className="badge bg-green-100 text-green-800"><CheckCircle className="w-4 h-4 mr-1" /> Success</span>
            ) : (
              <span className="badge bg-red-100 text-red-800"><XCircle className="w-4 h-4 mr-1" /> Error</span>
            )}
          </div>
          <div className="card-body space-y-4">
            {result.document_type && (
              <div>
                <h4 className="text-sm font-medium text-secondary-500 mb-1">Document Type</h4>
                <p className="text-lg font-semibold">{result.document_type}</p>
              </div>
            )}
            
            {result.extracted_fields && (
              <div>
                <h4 className="text-sm font-medium text-secondary-500 mb-2">Extracted Fields</h4>
                <div className="bg-secondary-50 rounded-lg p-4 grid grid-cols-2 md:grid-cols-3 gap-3">
                  {Object.entries(result.extracted_fields).map(([key, value]) => (
                    value && (
                      <div key={key}>
                        <span className="text-xs text-secondary-500 uppercase">{key.replace('_', ' ')}</span>
                        <p className="text-sm font-medium">{String(value)}</p>
                      </div>
                    )
                  ))}
                </div>
              </div>
            )}

            {result.extracted_text && (
              <div>
                <h4 className="text-sm font-medium text-secondary-500 mb-1">Extracted Text</h4>
                <p className="text-sm bg-secondary-50 p-3 rounded-lg max-h-40 overflow-y-auto">
                  {result.extracted_text}
                </p>
              </div>
            )}

            {result.analysis && (
              <div>
                <h4 className="text-sm font-medium text-secondary-500 mb-1">Analysis</h4>
                <p className="text-sm bg-secondary-50 p-3 rounded-lg whitespace-pre-wrap">{result.analysis}</p>
              </div>
            )}

            {result.compliance_report && (
              <div>
                <h4 className="text-sm font-medium text-secondary-500 mb-1">Compliance Report</h4>
                <p className="text-sm bg-secondary-50 p-3 rounded-lg whitespace-pre-wrap">{result.compliance_report}</p>
              </div>
            )}

            {result.summary && (
              <div>
                <h4 className="text-sm font-medium text-secondary-500 mb-1">Summary</h4>
                <p className="text-sm bg-secondary-50 p-3 rounded-lg">{result.summary}</p>
              </div>
            )}

            {result.discrepancies && (
              <div>
                <h4 className="text-sm font-medium text-secondary-500 mb-2">Discrepancies Found ({result.discrepancies.length})</h4>
                <div className="space-y-2">
                  {result.discrepancies.map((disc: any, idx: number) => (
                    <div key={idx} className={`p-3 rounded-lg ${disc.severity === 'critical' ? 'bg-red-50 border border-red-200' : 'bg-yellow-50 border border-yellow-200'}`}>
                      <div className="flex items-center">
                        <AlertTriangle className={`w-4 h-4 mr-2 ${disc.severity === 'critical' ? 'text-red-500' : 'text-yellow-500'}`} />
                        <span className="text-sm font-medium">{disc.type}</span>
                      </div>
                      <p className="text-sm mt-1">{disc.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.status === 'error' && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center text-red-600">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  <span>Analysis failed. Please try again.</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
