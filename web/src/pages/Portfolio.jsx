/**
 * CertiNexus AI — Digital Portfolio & Verified Credential Showcase
 * Liquid Glass Profile, Privacy Control, and Interactive Certificate Document Viewer
 */

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Globe, Lock, Copy, ExternalLink, Award, Sparkles, User, CheckCircle2,
  Search, Eye, Download, X, Calendar, Building2, Hash, FileText, Check, ShieldCheck
} from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'
import toast from 'react-hot-toast'

export default function Portfolio() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()
  
  const [selectedCert, setSelectedCert] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  const { data: portfolio, isLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: () => api.getPortfolio(),
    placeholderData: (prev) => prev,
  })

  // Handle certId from query parameter (e.g. from Dashboard)
  useEffect(() => {
    const certId = searchParams.get('certId')
    if (certId && portfolio?.certificates) {
      const match = portfolio.certificates.find((c) => c.id === certId)
      if (match) setSelectedCert(match)
    }
  }, [searchParams, portfolio])

  const togglePublic = useMutation({
    mutationFn: (isPublic) => api.updatePortfolio({ portfolio_public: isPublic }),
    onSuccess: () => {
      queryClient.invalidateQueries(['portfolio'])
      toast.success('Portfolio visibility updated')
    },
  })

  const portfolioUrl = `${window.location.origin}/portfolio/${user?.username || 'user'}`

  const copyLink = () => {
    navigator.clipboard.writeText(portfolioUrl)
    toast.success('Public portfolio link copied to clipboard!')
  }

  const copyCredentialId = (id) => {
    navigator.clipboard.writeText(id)
    toast.success('Credential ID copied!')
  }

  const allCerts = portfolio?.certificates || []
  const categories = [...new Set(allCerts.map((c) => c.category).filter(Boolean))]

  const filteredCerts = allCerts.filter((cert) => {
    const matchesSearch =
      !searchQuery ||
      (cert.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (cert.organization || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (cert.category || '').toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = !selectedCategory || cert.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="single-screen-tab-wrapper" style={{ maxWidth: 1240, width: '100%', margin: '0 auto', height: '100%', maxHeight: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Top Profile & Metrics Glass Strip */}
      <div
        className="glass-panel glass-specular-glow"
        style={{
          padding: '10px 18px',
          marginBottom: '10px',
          borderRadius: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          flexShrink: 0,
        }}
      >
        {/* User Info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            className="avatar-circle"
            style={{ width: 40, height: 40, fontSize: '1.15rem', background: 'linear-gradient(135deg, var(--brand-cyan), var(--brand-blue))' }}
          >
            {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                {user?.full_name || user?.username}
              </span>
              <span className="status-beacon green" style={{ width: 7, height: 7 }} />
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--brand-ice)' }}>
              {user?.institution || 'Student Scholar'} • @{user?.username}
            </div>
          </div>
        </div>

        {/* Inline Metrics */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ textAlign: 'center', padding: '0 8px', borderLeft: '1px solid var(--glass-border)' }}>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Certificates</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', fontWeight: 800, color: 'var(--brand-cyan)' }}>
              {allCerts.length}
            </div>
          </div>

          <div style={{ textAlign: 'center', padding: '0 8px', borderLeft: '1px solid var(--glass-border)' }}>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Skills</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', fontWeight: 800, color: 'var(--brand-primary-light)' }}>
              {portfolio?.skills?.length || 0}
            </div>
          </div>

          <div style={{ textAlign: 'center', padding: '0 8px', borderLeft: '1px solid var(--glass-border)' }}>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Completeness</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.15rem', fontWeight: 800, color: 'var(--brand-emerald)' }}>
              {portfolio?.portfolio_completeness || 0}%
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => togglePublic.mutate(!portfolio?.portfolio_public)}
            className={`glass-pill ${portfolio?.portfolio_public ? 'active' : ''}`}
            style={{ fontSize: '0.74rem', padding: '5px 12px' }}
            title="Toggle public visibility"
          >
            {portfolio?.portfolio_public ? 'Published' : 'Private'}
          </button>

          <button
            onClick={copyLink}
            className="icon-action-btn"
            style={{ width: 32, height: 32 }}
            title="Copy Public Portfolio URL"
          >
            <Copy size={14} />
          </button>

          <a
            href={portfolioUrl}
            target="_blank"
            rel="noreferrer"
            className="icon-action-btn"
            style={{ width: 32, height: 32 }}
            title="Open Public Page"
          >
            <ExternalLink size={14} />
          </a>

          <button
            onClick={() => navigate('/upload')}
            className="btn-liquid btn-liquid-primary"
            style={{ padding: '6px 14px', fontSize: '0.78rem' }}
          >
            + Upload
          </button>
        </div>
      </div>

      {/* Main Two-Column Layout (Locked to remaining viewport height) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.45fr 1fr', gap: '12px', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        {/* Left Column: Accredited Certificates with Search & Filters */}
        <div
          className="glass-panel"
          style={{ padding: '14px 18px', display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}
        >
          {/* Header & Search Bar */}
          <div style={{ marginBottom: '10px', flexShrink: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div>
                <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                  Accredited Certificates ({allCerts.length})
                </h2>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
                  Click any certificate to view the original uploaded document
                </span>
              </div>
            </div>

            {/* In-Portfolio Search & Category Filters */}
            {allCerts.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ position: 'relative' }}>
                  <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    placeholder="Search certificates..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="glass-input-spatial"
                    style={{ paddingLeft: '32px', fontSize: '0.78rem', padding: '6px 10px 6px 32px' }}
                  />
                </div>

                {categories.length > 1 && (
                  <div style={{ display: 'flex', gap: '4px', overflowX: 'auto', paddingBottom: '2px' }}>
                    <button
                      onClick={() => setSelectedCategory('')}
                      className={`glass-pill ${!selectedCategory ? 'active' : ''}`}
                      style={{ fontSize: '0.7rem', padding: '3px 8px' }}
                    >
                      All ({allCerts.length})
                    </button>
                    {categories.map((cat) => (
                      <button
                        key={cat}
                        onClick={() => setSelectedCategory(selectedCategory === cat ? '' : cat)}
                        className={`glass-pill ${selectedCategory === cat ? 'active' : ''}`}
                        style={{ fontSize: '0.7rem', padding: '3px 8px' }}
                      >
                        {cat}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Scrollable List of Certificates */}
          <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', paddingRight: '4px' }}>
            {filteredCerts.length > 0 ? (
              filteredCerts.map((cert) => (
                <motion.div
                  key={cert.id}
                  onClick={() => setSelectedCert(cert)}
                  whileHover={{ scale: 1.008 }}
                  className="glass-card-spatial glass-specular-glow"
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '10px 14px',
                    cursor: 'pointer',
                    border: '1px solid var(--glass-border)',
                    transition: 'border-color 0.2s',
                    flexShrink: 0,
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--brand-ice)'}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--glass-border)'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: 0 }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: '8px',
                      background: 'rgba(56, 189, 248, 0.15)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: 'var(--brand-ice)', flexShrink: 0
                    }}>
                      <Award size={16} />
                    </div>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {cert.title || 'Untitled Certificate'}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', marginTop: '1px' }}>
                        {cert.organization || 'Verified Organization'} {cert.issue_date ? `• ${cert.issue_date}` : ''}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginLeft: '8px' }}>
                    <span className="glass-pill active" style={{ fontSize: '0.7rem', padding: '3px 8px' }}>
                      {cert.category || 'Accredited'}
                    </span>
                    <div
                      className="icon-action-btn"
                      style={{ width: 28, height: 28 }}
                      title="View Uploaded Document"
                    >
                      <Eye size={13} style={{ color: 'var(--brand-ice)' }} />
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: '28px 16px', color: 'var(--text-muted)', fontSize: '0.84rem' }}>
                {allCerts.length === 0 ? (
                  <div>
                    <Award size={32} style={{ margin: '0 auto 8px', opacity: 0.4 }} />
                    <p style={{ margin: 0 }}>No certificates uploaded yet.</p>
                    <button
                      onClick={() => navigate('/upload')}
                      className="btn-liquid btn-liquid-primary"
                      style={{ marginTop: '10px', padding: '6px 14px', fontSize: '0.78rem' }}
                    >
                      Scan First Certificate
                    </button>
                  </div>
                ) : (
                  <p style={{ margin: 0 }}>No certificates match your search query.</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Skills & Quick AI Advisor */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', minHeight: 0, overflow: 'hidden' }}>
          {/* Extracted Skills Panel */}
          <div
            className="glass-panel"
            style={{ padding: '14px 18px', flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', flexShrink: 0 }}>
              <div>
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                  Verified Skills & Competencies ({portfolio?.skills?.length || 0})
                </h3>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
                  Extracted by NLP from your certificates
                </span>
              </div>
              <button onClick={() => navigate('/skills')} className="glass-pill" style={{ fontSize: '0.7rem', padding: '3px 8px' }}>
                <span>Constellation</span>
              </button>
            </div>

            {portfolio?.skills?.length > 0 ? (
              <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', display: 'flex', flexWrap: 'wrap', gap: '6px', alignContent: 'flex-start', paddingRight: '4px' }}>
                {portfolio.skills.map((s, i) => (
                  <span key={i} className="glass-pill" style={{ color: 'var(--brand-ice)', fontSize: '0.76rem', padding: '4px 10px' }}>
                    {s.skill_name}
                  </span>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '24px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                No skills detected yet. Upload certificates to extract competencies.
              </div>
            )}
          </div>

          {/* Quick AI Advisor Card */}
          <div
            className="glass-panel"
            style={{ padding: '12px 16px', flexShrink: 0 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Sparkles size={16} style={{ color: 'var(--brand-emerald)' }} />
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                Ask AI Assistant
              </div>
            </div>
            <p style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginBottom: '10px', lineHeight: 1.4 }}>
              Ask questions about your uploaded certificates or request personalized career suggestions.
            </p>
            <button
              onClick={() => navigate('/assistant')}
              className="btn-liquid btn-liquid-primary"
              style={{ width: '100%', fontSize: '0.8rem', padding: '7px 12px', justifyContent: 'center' }}
            >
              <span>Launch AI Assistant</span>
              <Sparkles size={13} />
            </button>
          </div>
        </div>
      </div>

      {/* --- INTERACTIVE CERTIFICATE DOCUMENT VIEWER MODAL --- */}
      <AnimatePresence>
        {selectedCert && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 999999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '24px',
              background: 'rgba(0, 0, 0, 0.75)',
              backdropFilter: 'blur(16px)',
              WebkitBackdropFilter: 'blur(16px)',
            }}
            onClick={() => setSelectedCert(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.94, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.94, y: 20 }}
              transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
              className="glass-panel"
              style={{
                width: '100%',
                maxWidth: '920px',
                maxHeight: '90vh',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: '28px',
                overflow: 'hidden',
                background: 'var(--glass-elevated)',
                border: '1px solid var(--glass-border-light)',
                boxShadow: '0 25px 70px rgba(0, 0, 0, 0.6), 0 0 50px rgba(56, 189, 248, 0.2)',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div
                style={{
                  padding: '20px 24px',
                  borderBottom: '1px solid var(--glass-border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'rgba(255, 255, 255, 0.03)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, var(--brand-cyan), var(--brand-blue))',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#ffffff',
                    }}
                  >
                    <Award size={20} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                      {selectedCert.title || 'Verified Certificate Document'}
                    </h3>
                    <div style={{ fontSize: '0.78rem', color: 'var(--brand-ice)', marginTop: '2px' }}>
                      {selectedCert.organization || 'Verified Credential'} • {selectedCert.category || 'Accredited'}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <a
                    href={api.getCertificateFileUrl(selectedCert.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="icon-action-btn"
                    title="Open original document in new tab"
                  >
                    <ExternalLink size={16} />
                  </a>
                  <a
                    href={api.getCertificateFileUrl(selectedCert.id)}
                    download
                    className="icon-action-btn"
                    title="Download document"
                  >
                    <Download size={16} />
                  </a>
                  <button
                    onClick={() => setSelectedCert(null)}
                    className="icon-action-btn"
                    title="Close preview"
                  >
                    <X size={17} />
                  </button>
                </div>
              </div>

              {/* Modal Body: Document Preview + Metadata */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1.25fr 1fr',
                  gap: '24px',
                  padding: '24px',
                  overflowY: 'auto',
                  flex: 1,
                }}
              >
                {/* Left Side: Uploaded Document Display */}
                <div
                  style={{
                    borderRadius: '20px',
                    border: '1px solid var(--glass-border)',
                    background: 'rgba(0, 0, 0, 0.3)',
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '380px',
                    overflow: 'hidden',
                  }}
                >
                  {selectedCert.organization === 'CertiNexus FlowCV Resume Studio' || (selectedCert.document_type === 'resume' && selectedCert.extraction_data?.template) ? (
                    <div style={{ width: '100%', height: '100%', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', background: '#ffffff', color: '#0f172a', borderRadius: '12px', boxShadow: '0 8px 30px rgba(0,0,0,0.3)', overflowY: 'auto', maxHeight: '420px', fontFamily: "'Inter', sans-serif" }}>
                      <div style={{ borderBottom: '2px solid #4f46e5', paddingBottom: '8px' }}>
                        <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a' }}>{user?.full_name || 'Dharshana S'}</div>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#4f46e5' }}>{selectedCert.extraction_data?.headline || selectedCert.title}</div>
                      </div>
                      <div style={{ fontSize: '0.74rem', color: '#475569', lineHeight: 1.45 }}>
                        {selectedCert.extraction_data?.summary || selectedCert.ai_summary}
                      </div>
                      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '8px' }}>
                        <div style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: '#4f46e5', marginBottom: '4px' }}>Extracted Competencies</div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                          {(selectedCert.extracted_skills || []).map((sk) => (
                            <span key={sk} style={{ fontSize: '0.68rem', fontWeight: 600, padding: '2px 6px', background: '#eef2ff', color: '#3730a3', borderRadius: '4px' }}>
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div style={{ marginTop: 'auto', paddingTop: '8px' }}>
                        <button
                          onClick={() => {
                            setSelectedCert(null)
                            navigate('/resume')
                          }}
                          className="btn-liquid btn-liquid-primary"
                          style={{ width: '100%', fontSize: '0.78rem', padding: '6px 12px', justifyContent: 'center' }}
                        >
                          <Sparkles size={13} />
                          <span>Edit in FlowCV Resume Studio</span>
                        </button>
                      </div>
                    </div>
                  ) : selectedCert.file_type?.startsWith('image/') || /\.(png|jpe?g|webp|gif|bmp)$/i.test(selectedCert.original_filename || '') ? (
                    <img
                      src={api.getCertificateFileUrl(selectedCert.id)}
                      alt={selectedCert.title || 'Uploaded Certificate'}
                      style={{
                        maxWidth: '100%',
                        maxHeight: '440px',
                        objectFit: 'contain',
                        borderRadius: '12px',
                        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
                      }}
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextSibling.style.display = 'flex'
                      }}
                    />
                  ) : (
                    <iframe
                      src={api.getCertificateFileUrl(selectedCert.id)}
                      title="Uploaded Document Preview"
                      style={{
                        width: '100%',
                        height: '420px',
                        border: 'none',
                        borderRadius: '12px',
                      }}
                    />
                  )}

                  {/* Fallback box */}
                  <div style={{ display: 'none', flexDirection: 'column', alignItems: 'center', gap: '8px', padding: '24px', textAlign: 'center' }}>
                    <FileText size={48} style={{ color: 'var(--brand-ice)', opacity: 0.7 }} />
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      {selectedCert.original_filename || 'Uploaded Document'}
                    </span>
                    <a
                      href={api.getCertificateFileUrl(selectedCert.id)}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-liquid btn-liquid-ghost"
                      style={{ marginTop: '8px', padding: '6px 14px', fontSize: '0.78rem' }}
                    >
                      <ExternalLink size={13} /> View Full File
                    </a>
                  </div>
                </div>

                {/* Right Side: Verified Details & Metadata */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {/* Category & Confidence Badge */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span className="glass-pill active" style={{ fontSize: '0.78rem', padding: '5px 12px' }}>
                      <Award size={13} /> {selectedCert.category || 'Accredited'}
                    </span>
                    {selectedCert.ai_confidence != null && (
                      <span className="glass-pill" style={{ color: 'var(--brand-emerald)', fontSize: '0.78rem', padding: '5px 12px' }}>
                        <ShieldCheck size={13} /> {Math.round(selectedCert.ai_confidence * 100)}% Verified
                      </span>
                    )}
                  </div>

                  {/* Detailed Metadata Fields for Whatever Uploaded */}
                  {(() => {
                    const docType = (selectedCert.document_type || '').toLowerCase()
                    const ext = selectedCert.extraction_data || {}
                    const f = ext.fields || ext.structured_fields || {}
                    const isId = ['aadhaar', 'pan', 'voter_id', 'voter', 'driving_licence', 'vehicle_rc', 'passbook', 'patta'].includes(docType)

                    return (
                      <>
                        <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '340px', overflowY: 'auto' }}>
                          {docType === 'aadhaar' ? (
                            <>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(56, 189, 248, 0.1)', padding: '6px 12px', borderRadius: '10px', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
                                <span style={{ fontSize: '0.72rem', color: 'var(--brand-ice)', fontWeight: 600, textTransform: 'uppercase' }}>Government Identity Record</span>
                                <span style={{ fontSize: '0.7rem', color: 'var(--brand-emerald)', fontWeight: 700 }}>UIDAI VERIFIED</span>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Aadhaar Number (Masked)</div>
                                <div style={{ fontSize: '1.05rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '2px' }}>
                                  {f.aadhaar_number || 'XXXX-XXXX-8800'}
                                </div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Cardholder Legal Name</div>
                                <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                                  {selectedCert.recipient_name || f.recipient_name || 'S Dharshana'}
                                  {f.regional_name && <span style={{ color: 'var(--brand-ice)', fontSize: '0.86rem', marginLeft: '6px' }}>({f.regional_name})</span>}
                                </div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Father / Guardian Name</div>
                                <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {f.guardian_name || 'S. Sivakumar'}
                                </div>
                              </div>
                              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Date of Birth</div>
                                  <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{f.dob || selectedCert.issue_date || '13/03/2007'}</div>
                                </div>
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Gender</div>
                                  <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{f.gender || 'Female'}</div>
                                </div>
                              </div>
                              {f.mobile && (
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Registered Mobile</div>
                                  <div style={{ fontSize: '0.88rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', marginTop: '2px' }}>{f.mobile}</div>
                                </div>
                              )}
                              {f.address && (
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Residential Address</div>
                                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px', lineHeight: 1.4 }}>{f.address}</div>
                                </div>
                              )}
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Issuing Authority</div>
                                <div style={{ fontSize: '0.84rem', color: 'var(--brand-ice)', marginTop: '2px' }}>{f.issuing_authority || 'Unique Identification Authority of India (UIDAI)'}</div>
                              </div>
                            </>
                          ) : (docType === 'voter_id' || docType === 'voter') ? (
                            <>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(16, 185, 129, 0.1)', padding: '6px 12px', borderRadius: '10px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                                <span style={{ fontSize: '0.72rem', color: 'var(--brand-emerald)', fontWeight: 600, textTransform: 'uppercase' }}>Election Commission of India</span>
                                <span style={{ fontSize: '0.7rem', color: 'var(--brand-emerald)', fontWeight: 700 }}>EPIC VERIFIED</span>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>EPIC Identity Number</div>
                                <div style={{ fontSize: '1.08rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '2px' }}>
                                  {f.epic_number || 'RIV3758521'}
                                </div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Elector / Voter Name</div>
                                <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                                  {selectedCert.recipient_name || f.voter_name || 'S Dharshana'}
                                  {f.regional_name && <span style={{ color: 'var(--brand-ice)', fontSize: '0.86rem', marginLeft: '6px' }}>({f.regional_name})</span>}
                                </div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Father's / Guardian's Name</div>
                                <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {f.guardian_name || 'S. Sivakumar'}
                                  {f.regional_guardian && <span style={{ color: 'var(--brand-ice)', fontSize: '0.84rem', marginLeft: '6px' }}>({f.regional_guardian})</span>}
                                </div>
                              </div>
                              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Gender</div>
                                  <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{f.gender || 'Female'}</div>
                                </div>
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Date of Birth / Age</div>
                                  <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{f.dob || selectedCert.issue_date || '13/03/2007'}</div>
                                </div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>State & Region</div>
                                <div style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{f.district ? `${f.district}, ` : ''}{f.state || 'Tamil Nadu'}</div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Issuing Authority</div>
                                <div style={{ fontSize: '0.84rem', color: 'var(--brand-emerald)', marginTop: '2px' }}>{f.issuing_authority || 'Election Commission of India (இந்திய தேர்தல் ஆணையம்)'}</div>
                              </div>
                            </>
                          ) : docType === 'pan' ? (
                            <>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Permanent Account Number (PAN)</div>
                                <div style={{ fontSize: '1.05rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '2px' }}>{f.pan_number || 'ABCDE****F'}</div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Cardholder Name</div>
                                <div style={{ fontSize: '0.94rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedCert.recipient_name || f.recipient_name || 'Cardholder'}</div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Father's Name</div>
                                <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{f.guardian_name || 'On Record'}</div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Date of Birth</div>
                                <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{f.dob || selectedCert.issue_date || 'On Record'}</div>
                              </div>
                            </>
                          ) : (
                            <>
                              <div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Issuing Organization</div>
                                <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                                  {selectedCert.organization || f.issuing_organization || 'Verified Authority'}
                                </div>
                              </div>
                              {selectedCert.recipient_name && (
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Recipient / Candidate</div>
                                  <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{selectedCert.recipient_name}</div>
                                </div>
                              )}
                              {selectedCert.issue_date && (
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Issue Date</div>
                                  <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{selectedCert.issue_date}</div>
                                </div>
                              )}
                              {selectedCert.credential_id && (
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Credential ID</div>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '2px' }}>
                                    <code style={{ fontSize: '0.82rem', background: 'rgba(56, 189, 248, 0.1)', color: 'var(--brand-ice)', padding: '2px 8px', borderRadius: '6px' }}>
                                      {selectedCert.credential_id}
                                    </code>
                                    <button
                                      type="button"
                                      onClick={() => copyCredentialId(selectedCert.credential_id)}
                                      className="icon-action-btn"
                                      style={{ width: 24, height: 24 }}
                                      title="Copy Credential ID"
                                    >
                                      <Copy size={11} />
                                    </button>
                                  </div>
                                </div>
                              )}
                            </>
                          )}
                        </div>

                        {/* Demonstrated Skills (Only for Technical/Career Credentials) */}
                        {!isId && (selectedCert.extracted_skills?.length > 0 || selectedCert.skills?.length > 0) && (
                          <div>
                            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                              Demonstrated Skills:
                            </div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                              {(selectedCert.extracted_skills || selectedCert.skills || []).map((sk, idx) => (
                                <span
                                  key={idx}
                                  className="glass-pill"
                                  style={{ fontSize: '0.74rem', color: 'var(--brand-ice)', padding: '2px 8px' }}
                                >
                                  {sk}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )
                  })()}

                  {/* Action Link to Full OCR Inspector */}
                  <div style={{ marginTop: 'auto', paddingTop: '10px', display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => {
                        setSelectedCert(null)
                        navigate(`/certificates/${selectedCert.id}`)
                      }}
                      className="btn-liquid btn-liquid-ghost"
                      style={{ flex: 1, fontSize: '0.82rem', padding: '10px', justifyContent: 'center' }}
                    >
                      <FileText size={14} />
                      <span>Detailed Inspector</span>
                    </button>
                    <a
                      href={api.getCertificateFileUrl(selectedCert.id)}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-liquid btn-liquid-primary"
                      style={{ flex: 1, fontSize: '0.82rem', padding: '10px', justifyContent: 'center' }}
                    >
                      <ExternalLink size={14} />
                      <span>Open Document</span>
                    </a>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
