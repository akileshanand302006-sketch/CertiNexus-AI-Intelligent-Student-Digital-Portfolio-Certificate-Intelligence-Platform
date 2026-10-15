/**
 * CertiNexus AI — Liquid Glass Certificate Gallery
 * Filter Pills, Spatial 3D Tilt Cards, and Real Data Integration
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Award, Search, Plus, Sparkles, Calendar, Building, ChevronRight } from 'lucide-react'
import api from '../lib/api.js'

export default function Certificates() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const navigate = useNavigate()

  const { data: certificates = [], isLoading } = useQuery({
    queryKey: ['certificates'],
    queryFn: () => api.getCertificates(),
  })

  const filtered = certificates.filter((cert) => {
    const matchesSearch =
      !searchQuery ||
      (cert.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (cert.organization || '').toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = !selectedCategory || cert.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = [...new Set(certificates.map((c) => c.category).filter(Boolean))]

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="status-beacon" />
            <span style={{ fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--brand-ice)' }}>
              Accredited Credentials
            </span>
          </div>
          <h1 className="spatial-hero-title">
            Certificate Gallery
          </h1>
          <p className="spatial-hero-subtitle">
            {certificates.length} verified digital credentials secured and analyzed.
          </p>
        </div>

        <button
          onClick={() => navigate('/upload')}
          className="btn-liquid btn-liquid-primary"
        >
          <Plus size={16} />
          <span>Upload Certificate</span>
        </button>
      </div>

      {/* Filter and Search Island */}
      <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '28px', borderRadius: '24px' }}>
        <div style={{ display: 'flex', gap: '14px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
            <Search
              size={16}
              style={{
                position: 'absolute',
                left: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
              }}
            />
            <input
              className="glass-input-spatial"
              placeholder="Search by title, issuer, or skill..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '44px', borderRadius: 'var(--radius-full)' }}
            />
          </div>

          {/* Category Filter Pills */}
          <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
            <button
              onClick={() => setSelectedCategory('')}
              className={`glass-pill ${!selectedCategory ? 'active' : ''}`}
            >
              All ({certificates.length})
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`glass-pill ${selectedCategory === cat ? 'active' : ''}`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Gallery Cards Grid */}
      {isLoading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="glass-panel" style={{ padding: '24px', height: '180px' }}>
              <div style={{ width: '40%', height: '20px', borderRadius: 10, background: 'var(--glass-pill)', marginBottom: '14px' }} />
              <div style={{ width: '80%', height: '24px', borderRadius: 8, background: 'var(--glass-pill)', marginBottom: '10px' }} />
              <div style={{ width: '60%', height: '16px', borderRadius: 8, background: 'var(--glass-pill)' }} />
            </div>
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {filtered.map((cert, idx) => (
            <motion.div
              key={cert.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.04 }}
              onClick={() => navigate(`/certificates/${cert.id}`)}
              className="glass-card-spatial glass-specular-glow"
              style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <span className="glass-pill active" style={{ fontSize: '0.74rem', padding: '4px 10px' }}>
                    {cert.category || 'Accredited'}
                  </span>
                  {cert.ai_confidence != null && (
                    <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--brand-emerald)' }}>
                      {(cert.ai_confidence * 100).toFixed(0)}% Match
                    </span>
                  )}
                </div>

                <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px', lineHeight: 1.3 }}>
                  {cert.title || cert.original_filename || 'Achievement Certificate'}
                </h2>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-tertiary)', fontSize: '0.82rem', marginBottom: '4px' }}>
                  <Building size={14} />
                  <span>{cert.organization || 'Verified Institution'}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                  <Calendar size={13} />
                  <span>{cert.issue_date || (cert.created_at ? new Date(cert.created_at).toLocaleDateString() : 'Verified')}</span>
                </div>
              </div>

              {/* Skills Tags */}
              <div style={{ marginTop: '18px', paddingTop: '14px', borderTop: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {cert.extracted_skills && cert.extracted_skills.slice(0, 3).map((s, j) => (
                    <span key={j} className="glass-pill" style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                      {typeof s === 'string' ? s : s.name}
                    </span>
                  ))}
                </div>
                <ChevronRight size={16} style={{ color: 'var(--brand-ice)' }} />
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '60px 24px', borderRadius: '28px' }}>
          <Award size={40} style={{ color: 'var(--brand-ice)', marginBottom: '14px' }} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
            No matching certificates found
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '20px' }}>
            Try adjusting your search criteria or upload a new certificate.
          </p>
          <button onClick={() => navigate('/upload')} className="btn-liquid btn-liquid-primary">
            <Plus size={16} />
            <span>Upload Certificate</span>
          </button>
        </div>
      )}
    </div>
  )
}
