/**
 * CertiNexus AI — Public Portfolio Page
 */
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Award, Sparkles, MapPin, Calendar } from 'lucide-react'
import api from '../lib/api.js'

export default function PublicPortfolio() {
  const { username } = useParams()
  const { data: portfolio, isLoading, error } = useQuery({
    queryKey: ['public-portfolio', username],
    queryFn: () => api.getPublicPortfolio(username),
  })

  if (isLoading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
      <div className="skeleton" style={{ width: 100, height: 100, borderRadius: '50%' }} />
    </div>
  )

  if (error) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', marginBottom: '8px' }}>Portfolio Not Found</h2>
        <p style={{ color: 'var(--text-secondary)' }}>This portfolio is private or doesn't exist.</p>
      </div>
    </div>
  )

  const { user, certificates = [], skills = [], portfolio_completeness = 0 } = portfolio

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', position: 'relative' }}>
      <div className="aurora-bg">
        <div className="aurora-blob aurora-blob-1" />
        <div className="aurora-blob aurora-blob-2" />
      </div>

      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '48px 24px', position: 'relative', zIndex: 1 }}>
        {/* Hero */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{
            width: 96, height: 96, borderRadius: '50%', margin: '0 auto 20px',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '2.5rem', fontWeight: 700, color: 'white',
          }}>{(user.full_name || user.username || 'U')[0].toUpperCase()}</div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }}>
            {user.full_name || user.username}
          </h1>
          {user.institution && (
            <p style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
              <MapPin size={14} /> {user.institution}
            </p>
          )}
          {user.bio && <p style={{ color: 'var(--text-tertiary)', marginTop: '12px', maxWidth: '500px', margin: '12px auto 0' }}>{user.bio}</p>}

          <div style={{ display: 'flex', gap: '24px', justifyContent: 'center', marginTop: '24px' }}>
            {[
              { label: 'Certificates', value: certificates.length },
              { label: 'Skills', value: skills.length },
              { label: 'Completeness', value: `${portfolio_completeness}%` },
            ].map((s, i) => (
              <div key={i}>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary-light)' }}>{s.value}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Skills */}
        {skills.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="glass-card" style={{ padding: '32px', marginBottom: '24px' }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={20} style={{ color: 'var(--color-secondary)' }} /> Skills
            </h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {skills.map((s, i) => (
                <span key={i} style={{
                  padding: '6px 14px', borderRadius: 'var(--radius-full)',
                  background: 'rgba(168,85,247,0.12)', border: '1px solid rgba(168,85,247,0.2)',
                  fontSize: '0.85rem', fontWeight: 500, color: 'var(--color-secondary-light)',
                }}>{s.skill_name}</span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Certificates */}
        {certificates.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Award size={20} style={{ color: 'var(--color-primary)' }} /> Certificates & Achievements
            </h2>
            <div className="grid-cards">
              {certificates.map((cert, i) => (
                <motion.div key={cert.id} className="glass-card"
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 + i * 0.05 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span className="category-badge">{cert.category}</span>
                    {cert.issue_date && <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={12} />{cert.issue_date}</span>}
                  </div>
                  <h3 style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '4px' }}>{cert.title || 'Certificate'}</h3>
                  <p style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>{cert.organization}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Footer */}
        <div style={{ textAlign: 'center', marginTop: '64px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
          Powered by CertiNexus AI
        </div>
      </div>
    </div>
  )
}
