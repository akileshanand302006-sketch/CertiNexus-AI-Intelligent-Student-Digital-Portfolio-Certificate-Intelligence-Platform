/**
 * CertiNexus AI — Certificates List
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Award, Search, Filter, Plus } from 'lucide-react'
import api from '../lib/api.js'

export default function Certificates() {
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const navigate = useNavigate()

  const { data: certificates = [], isLoading } = useQuery({
    queryKey: ['certificates'],
    queryFn: () => api.getCertificates(),
  })

  const filtered = certificates.filter(cert => {
    const matchesSearch = !searchQuery ||
      (cert.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (cert.organization || '').toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = !categoryFilter || cert.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  const categories = [...new Set(certificates.map(c => c.category).filter(Boolean))]

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Certificates</h1>
          <p>{certificates.length} certificates in your portfolio</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/upload')}>
          <Plus size={16} /> Upload
        </button>
      </div>

      {/* Search & Filter */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '200px' }}>
          <Search size={16} style={{
            position: 'absolute', left: '14px', top: '50%',
            transform: 'translateY(-50%)', color: 'var(--text-muted)',
          }} />
          <input className="glass-input" placeholder="Search certificates..."
            value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '40px' }} />
        </div>
        <select className="glass-input" style={{ width: '200px' }}
          value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
          <option value="">All Categories</option>
          {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
        </select>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid-cards">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="glass-card">
              <div className="skeleton" style={{ height: '20px', width: '60%', marginBottom: '12px' }} />
              <div className="skeleton" style={{ height: '16px', width: '80%', marginBottom: '8px' }} />
              <div className="skeleton" style={{ height: '14px', width: '40%' }} />
            </div>
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid-cards">
          {filtered.map((cert, i) => (
            <motion.div key={cert.id} className="glass-card"
              initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => navigate(`/certificates/${cert.id}`)}
              style={{ cursor: 'pointer' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <span className="category-badge">{cert.category || 'Uncategorized'}</span>
                {cert.ai_confidence != null && (
                  <span className={`confidence-badge confidence-${cert.ai_confidence_level || 'medium'}`}>
                    {(cert.ai_confidence * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              <h3 style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '6px' }}>
                {cert.title || cert.original_filename || 'Untitled Certificate'}
              </h3>
              <p style={{ color: 'var(--text-tertiary)', fontSize: '0.85rem', marginBottom: '4px' }}>
                {cert.organization || 'Unknown Organization'}
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                {cert.issue_date || new Date(cert.created_at).toLocaleDateString()}
              </p>
              {cert.extracted_skills?.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '10px' }}>
                  {cert.extracted_skills.slice(0, 3).map((s, j) => (
                    <span key={j} style={{
                      padding: '2px 8px', borderRadius: 'var(--radius-full)',
                      background: 'rgba(168,85,247,0.1)', fontSize: '0.65rem',
                      color: 'var(--color-secondary-light)', fontWeight: 500,
                    }}>{s}</span>
                  ))}
                  {cert.extracted_skills.length > 3 && (
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                      +{cert.extracted_skills.length - 3}
                    </span>
                  )}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="glass-card" style={{ textAlign: 'center', padding: '64px 32px' }}>
          <Award size={48} style={{ color: 'var(--text-muted)', marginBottom: '16px' }} />
          <h3 style={{ fontWeight: 600, marginBottom: '8px', fontFamily: 'var(--font-display)' }}>
            {searchQuery || categoryFilter ? 'No matching certificates' : 'No certificates yet'}
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
            {searchQuery || categoryFilter ? 'Try adjusting your search or filters' : 'Upload your first certificate to get started'}
          </p>
          {!searchQuery && !categoryFilter && (
            <button className="btn btn-primary" onClick={() => navigate('/upload')}>
              <Plus size={16} /> Upload Certificate
            </button>
          )}
        </div>
      )}
    </div>
  )
}
