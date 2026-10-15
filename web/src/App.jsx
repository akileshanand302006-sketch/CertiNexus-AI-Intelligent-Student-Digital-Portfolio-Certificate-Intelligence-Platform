import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './lib/auth.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'
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
import AIAssistant from './pages/AIAssistant.jsx'
import AppLayout from './components/layout/AppLayout.jsx'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
})

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: 'var(--bg-space)' }}>
        <div style={{ width: 48, height: 48, borderRadius: '50%', border: '2px solid var(--brand-ice)', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }} />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
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
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/certificates" element={<Navigate to="/portfolio" replace />} />
                <Route path="/certificates/:id" element={<CertificateDetails />} />
                <Route path="/skills" element={<Skills />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/resume" element={<ResumeBuilder />} />
                <Route path="/assistant" element={<AIAssistant />} />
                <Route path="/research" element={<Navigate to="/dashboard" replace />} />
              </Route>
            </Routes>
            <Toaster
              position="bottom-right"
              toastOptions={{
                style: {
                  background: 'var(--glass-elevated)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--glass-border-light)',
                  backdropFilter: 'blur(20px)',
                  WebkitBackdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  boxShadow: 'var(--glass-shadow-lg)',
                },
              }}
            />
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  )
}
