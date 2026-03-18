import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import Layout from '@/components/layout/Layout'
import Login from '@/pages/auth/Login'
import Dashboard from '@/pages/dashboard/Dashboard'
import LCList from '@/pages/lc/LCList'
import LCCreate from '@/pages/lc/LCCreate'
import LCDetail from '@/pages/lc/LCDetail'
import GuaranteeList from '@/pages/guarantee/GuaranteeList'
import GuaranteeCreate from '@/pages/guarantee/GuaranteeCreate'
import CollectionList from '@/pages/collection/CollectionList'
import CollectionCreate from '@/pages/collection/CollectionCreate'
import CollectionDetail from '@/pages/collection/CollectionDetail'
import InvoiceList from '@/pages/invoice/InvoiceList'
import InvoiceCreate from '@/pages/invoice/InvoiceCreate'
import InvoiceDetail from '@/pages/invoice/InvoiceDetail'
import LoanList from '@/pages/loan/LoanList'
import LoanCreate from '@/pages/loan/LoanCreate'
import RiskDashboard from '@/pages/risk/RiskDashboard'
import ComplianceDashboard from '@/pages/compliance/ComplianceDashboard'
import Reports from '@/pages/reports/Reports'
import Settings from '@/pages/settings/Settings'
import Users from '@/pages/admin/Users'
import { Loader2 } from 'lucide-react'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        
        {/* Letter of Credit Routes */}
        <Route path="lc">
          <Route index element={<LCList />} />
          <Route path="create" element={<LCCreate />} />
          <Route path=":id" element={<LCDetail />} />
        </Route>
        
        {/* Bank Guarantee Routes */}
        <Route path="guarantee">
          <Route index element={<GuaranteeList />} />
          <Route path="new" element={<GuaranteeCreate />} />
        </Route>
        
        {/* Documentary Collection Routes */}
        <Route path="collection">
          <Route index element={<CollectionList />} />
          <Route path="new" element={<CollectionCreate />} />
          <Route path=":id" element={<CollectionDetail />} />
        </Route>
        
        {/* Invoice Financing Routes */}
        <Route path="invoice">
          <Route index element={<InvoiceList />} />
          <Route path="new" element={<InvoiceCreate />} />
          <Route path=":id" element={<InvoiceDetail />} />
        </Route>
        
        {/* Trade Loan Routes */}
        <Route path="loan">
          <Route index element={<LoanList />} />
          <Route path="new" element={<LoanCreate />} />
          <Route path=":id" element={<LoanCreate />} />
        </Route>
        
        {/* Risk Management Routes */}
        <Route path="risk">
          <Route index element={<RiskDashboard />} />
        </Route>
        
        {/* Compliance Routes */}
        <Route path="compliance">
          <Route index element={<ComplianceDashboard />} />
        </Route>
        
        {/* Reports Routes */}
        <Route path="reports">
          <Route index element={<Reports />} />
        </Route>
        
        {/* Settings Routes */}
        <Route path="settings">
          <Route index element={<Settings />} />
        </Route>
        
        {/* Admin Routes */}
        <Route path="admin">
          <Route path="users" element={<Users />} />
        </Route>
      </Route>
      
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
