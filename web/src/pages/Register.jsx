/**
 * CertiNexus AI — Register Page
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../lib/auth.jsx'
import { Eye, EyeOff, UserPlus, AlertCircle } from 'lucide-react'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '', full_name: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { register } = useAuth()

  const updateField = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await register(form)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      position: 'relative', overflow: 'hidden', padding: '24px',
    }}>
      <div className="aurora-bg">
        <div className="aurora-blob aurora-blob-1" />
        <div className="aurora-blob aurora-blob-2" />
        <div className="aurora-blob aurora-blob-3" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="glass-card"
        style={{
          width: '100%', maxWidth: '480px', padding: '40px',
          position: 'relative', zIndex: 1,
        }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: 48, height: 48, borderRadius: '14px', margin: '0 auto 16px',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 800, color: 'white', fontSize: '1.3rem',
          }}>C</div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 700 }}>
            Create your account
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Start building your intelligent portfolio
          </p>
        </div>

        {error && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '12px', borderRadius: 'var(--radius-md)',
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
            color: 'var(--color-error-light)', fontSize: '0.85rem', marginBottom: '20px',
          }}><AlertCircle size={16} />{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>Full Name</label>
              <input className="glass-input" placeholder="John Doe"
                value={form.full_name} onChange={updateField('full_name')} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>Username</label>
              <input className="glass-input" required placeholder="johndoe"
                value={form.username} onChange={updateField('username')} />
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>Email</label>
            <input className="glass-input" type="email" required
              placeholder="you@example.com"
              value={form.email} onChange={updateField('email')} />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>Password</label>
            <div style={{ position: 'relative' }}>
              <input className="glass-input" required minLength={6}
                type={showPassword ? 'text' : 'password'}
                placeholder="Min 6 characters"
                value={form.password} onChange={updateField('password')}
                style={{ paddingRight: '44px' }} />
              <button type="button" onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute', right: '12px', top: '50%',
                  transform: 'translateY(-50%)', background: 'none',
                  border: 'none', color: 'var(--text-muted)', cursor: 'pointer',
                }}>
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}
            style={{ width: '100%', padding: '14px', fontSize: '0.95rem' }}>
            {loading ? 'Creating account...' : <><UserPlus size={18} /> Create Account</>}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '20px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--color-primary-light)', fontWeight: 600 }}>Sign in</Link>
        </p>
      </motion.div>
    </div>
  )
}
