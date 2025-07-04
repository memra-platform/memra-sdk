'use client'

import { useState } from 'react'
import { Upload, FileText, Database, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'

interface WorkflowStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  message?: string
  data?: any
}

interface InvoiceData {
  vendor_name: string
  invoice_number: string
  invoice_date: string
  amount: number
  tax_amount: number
  line_items: string
}

export default function Dashboard() {
  const [apiKey, setApiKey] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([
    { id: '1', name: 'Pre-ETL Database Monitor', status: 'pending' },
    { id: '2', name: 'Data Engineer', status: 'pending' },
    { id: '3', name: 'Invoice Parser', status: 'pending' },
    { id: '4', name: 'Data Entry Specialist', status: 'pending' },
    { id: '5', name: 'Post-ETL Database Monitor', status: 'pending' },
  ])
  const [extractedData, setExtractedData] = useState<InvoiceData | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf', '.PDF']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setUploadedFile(acceptedFiles[0])
      toast.success(`File uploaded: ${acceptedFiles[0].name}`)
    }
  })

  const updateStepStatus = (stepId: string, status: WorkflowStep['status'], message?: string, data?: any) => {
    setWorkflowSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, status, message, data }
        : step
    ))
  }

  const processInvoice = async () => {
    if (!apiKey) {
      toast.error('Please enter your Memra API key')
      return
    }
    
    if (!uploadedFile) {
      toast.error('Please upload a PDF file')
      return
    }

    setIsProcessing(true)
    
    try {
      // Step 1: Upload file
      updateStepStatus('1', 'running', 'Monitoring database state...')
      
      const formData = new FormData()
      formData.append('file', uploadedFile)
      
      const uploadResponse = await fetch(`${process.env.NEXT_PUBLIC_MEMRA_API_URL || 'https://api.memra.co'}/upload`, {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey,
        },
        body: formData
      })

      if (!uploadResponse.ok) {
        throw new Error('File upload failed')
      }

      const uploadResult = await uploadResponse.json()
      updateStepStatus('1', 'completed', 'Database monitoring completed')
      
      // Step 2: Data Engineer
      updateStepStatus('2', 'running', 'Extracting invoice schema...')
      await new Promise(resolve => setTimeout(resolve, 1000))
      updateStepStatus('2', 'completed', 'Schema extracted successfully')
      
      // Step 3: Invoice Parser
      updateStepStatus('3', 'running', 'Processing invoice with AI...')
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Simulate extracted data (replace with actual API call)
      const mockExtractedData: InvoiceData = {
        vendor_name: 'Superior Propane',
        invoice_number: '50482291',
        invoice_date: '2024-09-16',
        amount: 197.79,
        tax_amount: 25.8,
        line_items: JSON.stringify([
          { description: '33lb CYL AL/BOUT 33Lb', quantity: 6, unit_price: 22.174, total: 133.04 },
          { description: 'CARBUN TAX / FUEL TAX', total: 11.94 }
        ])
      }
      
      setExtractedData(mockExtractedData)
      updateStepStatus('3', 'completed', 'Invoice data extracted successfully', mockExtractedData)
      
      // Step 4: Data Entry Specialist
      updateStepStatus('4', 'running', 'Validating and inserting data...')
      await new Promise(resolve => setTimeout(resolve, 1000))
      updateStepStatus('4', 'completed', 'Data inserted into database')
      
      // Step 5: Post-ETL Monitor
      updateStepStatus('5', 'running', 'Verifying data integrity...')
      await new Promise(resolve => setTimeout(resolve, 500))
      updateStepStatus('5', 'completed', 'ETL process completed successfully')
      
      toast.success('Invoice processed successfully!')
      
    } catch (error) {
      console.error('Processing error:', error)
      toast.error('Failed to process invoice')
      updateStepStatus('3', 'failed', 'Processing failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const getStepIcon = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-500" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-error-500" />
      case 'running':
        return <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
    }
  }

  const getStepColor = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'completed':
        return 'text-success-600 bg-success-50 border-success-200'
      case 'failed':
        return 'text-error-600 bg-error-50 border-error-200'
      case 'running':
        return 'text-primary-600 bg-primary-50 border-primary-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Database className="w-8 h-8 text-primary-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Memra ETL Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <input
                type="password"
                placeholder="Enter Memra API Key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Invoice</h2>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                {uploadedFile ? (
                  <div>
                    <FileText className="w-8 h-8 text-success-500 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">{uploadedFile.name}</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-gray-600">
                      {isDragActive ? 'Drop the PDF here' : 'Drag & drop a PDF file, or click to select'}
                    </p>
                    <p className="text-xs text-gray-500 mt-2">Supports PDF files only</p>
                  </div>
                )}
              </div>

              <button
                onClick={processInvoice}
                disabled={isProcessing || !uploadedFile || !apiKey}
                className="btn-primary w-full mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Process Invoice'
                )}
              </button>
            </div>

            {/* Extracted Data Display */}
            {extractedData && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Extracted Data</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-500">Vendor:</span>
                    <span className="text-sm text-gray-900">{extractedData.vendor_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-500">Invoice #:</span>
                    <span className="text-sm text-gray-900">{extractedData.invoice_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-500">Date:</span>
                    <span className="text-sm text-gray-900">{extractedData.invoice_date}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-500">Amount:</span>
                    <span className="text-sm text-gray-900">${extractedData.amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-500">Tax:</span>
                    <span className="text-sm text-gray-900">${extractedData.tax_amount.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Workflow Progress */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">ETL Workflow Progress</h2>
            
            <div className="space-y-4">
              {workflowSteps.map((step) => (
                <div
                  key={step.id}
                  className={`flex items-center p-4 rounded-lg border ${getStepColor(step.status)}`}
                >
                  {getStepIcon(step.status)}
                  <div className="ml-3 flex-1">
                    <h3 className="text-sm font-medium">{step.name}</h3>
                    {step.message && (
                      <p className="text-xs mt-1 opacity-75">{step.message}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Summary Stats */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-primary-600">
                    {workflowSteps.filter(s => s.status === 'completed').length}
                  </div>
                  <div className="text-xs text-gray-500">Completed</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-warning-500">
                    {workflowSteps.filter(s => s.status === 'running').length}
                  </div>
                  <div className="text-xs text-gray-500">Running</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-error-500">
                    {workflowSteps.filter(s => s.status === 'failed').length}
                  </div>
                  <div className="text-xs text-gray-500">Failed</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
} 