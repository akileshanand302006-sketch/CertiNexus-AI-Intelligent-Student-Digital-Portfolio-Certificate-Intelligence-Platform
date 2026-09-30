/**
 * CertiNexus AI — Login Page (Liquid Glass)
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../lib/auth.jsx'
import { Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', position: 'relative', overflow: 'hidden',
    }}>
      {/* Aurora Background */}
      <div className="aurora-bg">
        <div className="aurora-blob aurora-blob-1" />
        <div className="aurora-blob aurora-blob-2" />
        <div className="aurora-blob aurora-blob-3" />
      </div>

      {/* Left Panel — Branding */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        justifyContent: 'center', padding: '48px',
        position: 'relative', zIndex: 1,
      }}>
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px',
          }}>
            <div style={{
              width: 44, height: 44, borderRadius: '12px',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: 800, color: 'white', fontFamily: 'var(--font-display)', fontSize: '1.2rem',
            }}>C</div>
            <span style={{
              fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.3rem',
            }}>CertiNexus AI</span>
          </div>

          <h1 style={{
            fontFamily: 'var(--font-display)', fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: 800, lineHeight: 1.15, marginBottom: '16px',
            background: 'linear-gradient(135deg, #f1f5f9, #6366f1)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            Your achievements.<br />Intelligently organized.
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: 1.7, maxWidth: '400px' }}>
            Upload certificates, let AI classify and extract skills,
            and build your digital portfolio automatically.
          </p>
        </motion.div>
      </div>

      {/* Right Panel — Login Form */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: '48px', position: 'relative', zIndex: 1,
      }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="glass-card"
          style={{
            width: '100%', maxWidth: '420px', padding: '40px',
            background: 'rgba(255,255,255,0.04)',
          }}>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 700,
            marginBottom: '8px',
          }}>Welcome back</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '32px' }}>
            Sign in to your CertiNexus AI account
          </p>

          {error && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              padding: '12px 16px', borderRadius: 'var(--radius-md)',
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
              color: 'var(--color-error-light)', fontSize: '0.85rem',
              marginBottom: '20px',
            }}>
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block', fontSize: '0.85rem', fontWeight: 500,
                color: 'var(--text-secondary)', marginBottom: '8px',
              }}>Email</label>
              <input className="glass-input" type="email" required
                placeholder="you@example.com"
                value={email} onChange={e => setEmail(e.target.value)} />
            </div>

            <div style={{ marginBottom: '28px' }}>
              <label style={{
                display: 'block', fontSize: '0.85rem', fontWeight: 500,
                color: 'var(--text-secondary)', marginBottom: '8px',
              }}>Password</label>
              <div style={{ position: 'relative' }}>
                <input className="glass-input" required
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password} onChange={e => setPassword(e.target.value)}
                  style={{ paddingRight: '44px' }} />
                <button type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute', right: '12px', top: '50%',
                    transform: 'translateY(-50%)', background: 'none',
                    border: 'none', color: 'var(--text-muted)', cursor: 'pointer',
                  }}>
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button type="submit" className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', padding: '14px', fontSize: '0.95rem' }}>
              {loading ? 'Signing in...' : <>Sign In <LogIn size={18} /></>}
            </button>
          </form>

          <p style={{
            textAlign: 'center', marginTop: '24px',
            color: 'var(--text-secondary)', fontSize: '0.85rem',
          }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: 'var(--color-primary-light)', fontWeight: 600 }}>
              Create one
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  )
}
