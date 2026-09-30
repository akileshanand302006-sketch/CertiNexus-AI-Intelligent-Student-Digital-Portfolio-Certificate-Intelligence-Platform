/**
 * CertiNexus AI — Portfolio Page
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { User, Globe, Lock, QrCode, Copy, ExternalLink } from 'lucide-react'
import { useState } from 'react'
import api from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'
import toast from 'react-hot-toast'

export default function Portfolio() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const { data: portfolio } = useQuery({ queryKey: ['portfolio'], queryFn: () => api.getPortfolio() })
  const [showQR, setShowQR] = useState(false)

  const togglePublic = useMutation({
    mutationFn: (isPublic) => api.updatePortfolio({ portfolio_public: isPublic }),
    onSuccess: () => {
      queryClient.invalidateQueries(['portfolio'])
      toast.success('Portfolio visibility updated')
    },
  })

  const portfolioUrl = `${window.location.origin}/portfolio/${user?.username}`

  const copyLink = () => {
    navigator.clipboard.writeText(portfolioUrl)
    toast.success('Link copied!')
  }

  return (
    <div>
      <div className="page-header">
        <h1>My Portfolio</h1>
        <p>Manage your public portfolio and settings</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Portfolio Preview */}
        <motion.div className="glass-card" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} style={{ padding: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
            <div style={{
              width: 64, height: 64, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.5rem', fontWeight: 700, color: 'white',
            }}>
              {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
            </div>
            <div>
              <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700 }}>{user?.full_name || user?.username}</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{user?.institution || 'Student'}</p>
              {user?.bio && <p style={{ color: 'var(--text-tertiary)', fontSize: '0.85rem', marginTop: '4px' }}>{user.bio}</p>}
            </div>
          </div>

          {/* Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
            {[
              { label: 'Certificates', value: portfolio?.certificates?.length || 0 },
              { label: 'Skills', value: portfolio?.skills?.length || 0 },
              { label: 'Completeness', value: `${portfolio?.portfolio_completeness || 0}%` },
            ].map((s, i) => (
              <div key={i} className="stat-card" style={{ padding: '16px' }}>
                <div className="stat-value" style={{ fontSize: '1.5rem' }}>{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Skills */}
          {portfolio?.skills?.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '12px', fontSize: '0.95rem' }}>Skills</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {portfolio.skills.map((s, i) => (
                  <span key={i} style={{
                    padding: '4px 12px', borderRadius: 'var(--radius-full)',
                    background: 'rgba(168,85,247,0.12)', border: '1px solid rgba(168,85,247,0.2)',
                    fontSize: '0.8rem', fontWeight: 500, color: 'var(--color-secondary-light)',
                  }}>{s.skill_name}</span>
                ))}
              </div>
            </div>
          )}

          {/* Certificates */}
          {portfolio?.certificates?.length > 0 && (
            <div>
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '12px', fontSize: '0.95rem' }}>Certificates</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {portfolio.certificates.slice(0, 5).map((cert, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '12px', borderRadius: 'var(--radius-md)',
                    background: 'var(--glass-bg)', border: '1px solid var(--glass-border)',
                  }}>
                    <div>
                      <div style={{ fontWeight: 500, fontSize: '0.9rem' }}>{cert.title || 'Untitled'}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{cert.organization}</div>
                    </div>
                    <span className="category-badge">{cert.category}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Settings */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <div className="glass-card" style={{ padding: '24px', marginBottom: '16px' }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', fontSize: '0.95rem' }}>Visibility</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button className={`btn ${user?.portfolio_public ? 'btn-primary' : 'btn-ghost'}`} style={{ width: '100%', justifyContent: 'flex-start' }}
                onClick={() => togglePublic.mutate(true)}>
                <Globe size={16} /> Public
              </button>
              <button className={`btn ${!user?.portfolio_public ? 'btn-primary' : 'btn-ghost'}`} style={{ width: '100%', justifyContent: 'flex-start' }}
                onClick={() => togglePublic.mutate(false)}>
                <Lock size={16} /> Private
              </button>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '24px', marginBottom: '16px' }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '12px', fontSize: '0.95rem' }}>Share</h3>
            <div style={{
              padding: '10px', borderRadius: 'var(--radius-md)', background: 'rgba(0,0,0,0.2)',
              border: '1px solid var(--glass-border)', fontSize: '0.75rem',
              fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)',
              wordBreak: 'break-all', marginBottom: '12px',
            }}>{portfolioUrl}</div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-ghost btn-sm" onClick={copyLink}><Copy size={14} /> Copy</button>
              <button className="btn btn-ghost btn-sm" onClick={() => window.open(portfolioUrl, '_blank')}><ExternalLink size={14} /> Open</button>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '24px' }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '12px', fontSize: '0.95rem' }}>Theme</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {['liquid-glass', 'minimal', 'developer', 'academic', 'professional'].map(theme => (
                <button key={theme} className={`btn ${user?.portfolio_theme === theme ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                  style={{ width: '100%', justifyContent: 'flex-start', textTransform: 'capitalize' }}
                  onClick={() => api.updatePortfolio({ portfolio_theme: theme })}>
                  {theme.replace('-', ' ')}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
