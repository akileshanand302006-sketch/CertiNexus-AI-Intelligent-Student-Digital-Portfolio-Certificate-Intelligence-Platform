import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './lib/auth.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import CertificateUpload from './pages/CertificateUpload.jsx'
import Certificates from './pages/Certificates.jsx'
import CertificateDetails from './pages/CertificateDetails.jsx'
import Skills from './pages/Skills.jsx'
import Analytics from './pages/Analytics.jsx'
import Portfolio from './pages/Portfolio.jsx'
import PublicPortfolio from './pages/PublicPortfolio.jsx'
import MLResearch from './pages/MLResearch.jsx'
import ResumeBuilder from './pages/ResumeBuilder.jsx'
import AppLayout from './components/layout/AppLayout.jsx'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30000 } },
})

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="loading-screen"><div className="skeleton" style={{width:'100px',height:'100px',borderRadius:'50%'}}/></div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/portfolio/:username" element={<PublicPortfolio />} />

            {/* Protected routes */}
            <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/upload" element={<CertificateUpload />} />
              <Route path="/certificates" element={<Certificates />} />
              <Route path="/certificates/:id" element={<CertificateDetails />} />
              <Route path="/skills" element={<Skills />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/resume" element={<ResumeBuilder />} />
              <Route path="/research" element={<MLResearch />} />
            </Route>
          </Routes>
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: 'rgba(30,32,48,0.95)',
                color: '#f1f5f9',
                border: '1px solid rgba(255,255,255,0.1)',
                backdropFilter: 'blur(16px)',
                borderRadius: '12px',
              },
            }}
          />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
