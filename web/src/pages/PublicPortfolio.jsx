/**
 * CertiNexus AI — Verified Public Portfolio Showcase
 * External View with Atmospheric Liquid Glass & Cryptographic Attestation
 */

import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Award, Sparkles, MapPin, Calendar, ShieldCheck, ExternalLink, ArrowLeft } from 'lucide-react'
import api from '../lib/api.js'

export default function PublicPortfolio() {
  const { username } = useParams()
  const navigate = useNavigate()
  const { data: portfolio, isLoading, error } = useQuery({
    queryKey: ['public-portfolio', username],
    queryFn: () => api.getPublicPortfolio(username),
  })

  if (isLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-space)' }}>
        <div style={{ width: 48, height: 48, borderRadius: '50%', border: '2px solid var(--brand-ice)', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }} />
      </div>
    )
  }

  if (error || !portfolio) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-space)', padding: '24px' }}>
        <div className="glass-panel" style={{ padding: '48px 36px', textAlign: 'center', maxWidth: 480 }}>
          <ShieldCheck size={48} style={{ color: 'var(--brand-ice)', margin: '0 auto 16px' }} />
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
            Portfolio Not Available
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '24px' }}>
            This portfolio is set to private by the student or does not exist.
          </p>
          <button onClick={() => navigate('/')} className="btn-liquid btn-liquid-primary">
            Return to CertiNexus AI
          </button>
        </div>
      </div>
    )
  }

  const { user, certificates = [], skills = [], portfolio_completeness = 0 } = portfolio

  return (
    <div style={{ minHeight: '100vh', position: 'relative', overflowX: 'hidden' }}>
      <div className="atmospheric-ambient" />
      <div className="spatial-grid-overlay" />

      {/* Top Banner Island */}
      <header className="floating-nav-island" style={{ justifyContent: 'space-between' }}>
        <div className="nav-brand-island" onClick={() => navigate('/')}>
          <div className="nav-brand-logo">C</div>
          <div className="nav-brand-text">
            <span>CertiNexus</span>
            <span className="nav-brand-badge">VERIFIED</span>
          </div>
          <span className="status-beacon green" title="Verified Credential Record" />
        </div>

        <button onClick={() => navigate('/login')} className="btn-liquid btn-liquid-ghost" style={{ padding: '6px 16px', fontSize: '0.84rem' }}>
          Sign In to Platform
        </button>
      </header>

      {/* Main Container */}
      <div style={{ maxWidth: 960, margin: '0 auto', paddingTop: '110px', paddingBottom: '60px', paddingLeft: '24px', paddingRight: '24px', position: 'relative', zIndex: 10 }}>
        {/* Profile Island */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel"
          style={{ padding: '40px', textAlign: 'center', marginBottom: '28px', borderRadius: '32px' }}
        >
          <div
            style={{
              width: 88,
              height: 88,
              borderRadius: '50%',
              margin: '0 auto 20px',
              background: 'linear-gradient(135deg, var(--brand-primary), var(--brand-cyan))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2.2rem',
              fontWeight: 800,
              color: '#ffffff',
              boxShadow: '0 0 30px rgba(56, 189, 248, 0.35)',
            }}
          >
            {(user.full_name || user.username || 'U')[0].toUpperCase()}
          </div>

          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
            {user.full_name || user.username}
          </h1>

          {user.institution && (
            <p style={{ color: 'var(--brand-ice)', fontSize: '0.95rem', fontWeight: 500, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
              <MapPin size={15} />
              <span>{user.institution}</span>
            </p>
          )}

          {user.bio && (
            <p style={{ color: 'var(--text-secondary)', marginTop: '12px', maxWidth: '520px', margin: '12px auto 0', fontSize: '0.92rem' }}>
              {user.bio}
            </p>
          )}

          {/* Attestation Stats */}
          <div style={{ display: 'flex', gap: '28px', justifyContent: 'center', marginTop: '28px' }}>
            <div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {certificates.length}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Verified Certs
              </div>
            </div>

            <div style={{ width: 1, height: 40, background: 'var(--glass-border)' }} />

            <div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, color: 'var(--brand-primary-light)' }}>
                {skills.length}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Extracted Skills
              </div>
            </div>

            <div style={{ width: 1, height: 40, background: 'var(--glass-border)' }} />

            <div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, color: 'var(--brand-emerald)' }}>
                {portfolio_completeness}%
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Completeness
              </div>
            </div>
          </div>
        </motion.div>

        {/* Skills Section */}
        {skills.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-panel"
            style={{ padding: '32px', marginBottom: '28px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Sparkles size={18} style={{ color: 'var(--brand-ice)' }} />
              <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Demonstrated Competencies
              </h2>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {skills.map((s, i) => (
                <span key={i} className="glass-pill active" style={{ fontSize: '0.85rem' }}>
                  {s.skill_name}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Certificates Section */}
        {certificates.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="glass-panel"
            style={{ padding: '32px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
              <Award size={18} style={{ color: 'var(--brand-ice)' }} />
              <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Accredited Credentials ({certificates.length})
              </h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '16px' }}>
              {certificates.map((cert, i) => (
                <div key={i} className="glass-card-spatial" style={{ padding: '18px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span className="glass-pill active" style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
                      {cert.category || 'Accredited'}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                    {cert.title || 'Certificate of Completion'}
                  </h3>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)' }}>
                    {cert.organization || 'Verified Institution'}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
