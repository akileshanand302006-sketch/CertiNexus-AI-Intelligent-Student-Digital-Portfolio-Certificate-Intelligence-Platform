/**
 * CertiNexus AI — Skills Intelligence Constellation & Certificate Skill Viewer
 *
 * Provides comprehensive visualization of all detected skills without cutoff,
 * and allows users to choose any uploaded certificate or identity document
 * to inspect the exact skills extracted specifically from that credential.
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Sparkles, Search, Award, Upload, ArrowRight, FileText, CheckCircle2,
  Code2, Cpu, Wrench, BookOpen, Layers, ShieldCheck, ChevronRight,
  ExternalLink, Filter, HelpCircle
} from 'lucide-react'
import api from '../lib/api.js'

// Domain classification mapping
const categorizeSkill = (name = '') => {
  const lower = name.toLowerCase()
  if (['python', 'typescript', 'javascript', 'java', 'sql', 'c', 'c++', 'html', 'css', 'go', 'rust', 'php'].includes(lower)) {
    return { category: 'Languages', color: 'var(--brand-cyan)', icon: Code2 }
  }
  if (['fastapi', 'react', 'scikit-learn', 'pandas', 'numpy', 'next.js', 'tailwind css', 'django', 'flask', 'tensorflow', 'pytorch'].includes(lower)) {
    return { category: 'Frameworks & ML', color: 'var(--brand-primary-light)', icon: Cpu }
  }
  if (['sqlite', 'git', 'docker', 'postgresql', 'redis', 'aws', 'linux', 'github', 'mongodb', 'mysql'].includes(lower)) {
    return { category: 'Tools & Databases', color: 'var(--brand-emerald)', icon: Wrench }
  }
  if (['software development', 'frontend development', 'backend development', 'ai', 'machine learning', 'system architecture'].includes(lower)) {
    return { category: 'Engineering Concepts', color: 'var(--brand-ice)', icon: Layers }
  }
  return { category: 'Professional Competencies', color: 'var(--brand-amber)', icon: Award }
}

// Helper to extract clean titles for pills & dropdowns
const getCleanCertTitle = (cert) => {
  const docType = (cert.document_type || '').toLowerCase()
  const rawTitle = cert.title || 'Document'
  
  if (docType === 'aadhaar' || rawTitle.toLowerCase().includes('aadhaar')) {
    return 'Aadhaar Card'
  }
  if (docType === 'voter_id' || docType === 'voter' || rawTitle.toLowerCase().includes('voter')) {
    return 'Voter ID (EPIC)'
  }
  if (rawTitle.toLowerCase().includes('flowcv') || cert.organization?.includes('FlowCV')) {
    return 'FlowCV Resume'
  }
  if (rawTitle.toLowerCase().includes('internship')) {
    return 'Internship Program'
  }
  if (docType === 'resume' || rawTitle.toLowerCase().includes('resume') || rawTitle.toLowerCase().includes('curriculum vitae')) {
    return 'Candidate Resume'
  }
  return rawTitle.replace(/Student Portfolio & Skill Profile — /g, '').replace(/FlowCV Resume — /g, '').slice(0, 26)
}

const getSkillCount = (cert) => {
  if (Array.isArray(cert?.extracted_skills)) return cert.extracted_skills.length
  if (typeof cert?.extracted_skills === 'string') {
    try {
      return JSON.parse(cert.extracted_skills).length
    } catch {
      return 0
    }
  }
  return 0
}

export default function Skills() {
  const navigate = useNavigate()
  const [filterQuery, setFilterQuery] = useState('')
  const [selectedDocId, setSelectedDocId] = useState('all')
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('All')

  // Load analytics & full portfolio data
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(),
    placeholderData: (prev) => prev,
  })

  const { data: portfolio, isLoading: portfolioLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: () => api.getPortfolio(),
    placeholderData: (prev) => prev,
  })

  const certificates = useMemo(() => portfolio?.certificates || [], [portfolio])

  // Map each skill to the certificates where it was detected
  const skillToDocsMap = useMemo(() => {
    const map = {}
    certificates.forEach((cert) => {
      let certSkills = []
      if (Array.isArray(cert.extracted_skills)) {
        certSkills = cert.extracted_skills
      } else if (typeof cert.extracted_skills === 'string') {
        try {
          certSkills = JSON.parse(cert.extracted_skills)
        } catch {
          certSkills = []
        }
      }
      certSkills.forEach((skillName) => {
        if (!map[skillName]) map[skillName] = []
        map[skillName].push({
          id: cert.id,
          title: cert.title || 'Untitled Document',
          organization: cert.organization || 'Accredited Authority',
          document_type: cert.document_type || 'certificate',
          issue_date: cert.issue_date,
        })
      })
    })
    return map
  }, [certificates])

  // Selected certificate object (if specific doc chosen)
  const selectedCert = useMemo(() => {
    if (selectedDocId === 'all') return null
    return certificates.find((c) => c.id === selectedDocId) || null
  }, [selectedDocId, certificates])

  // Skills for the currently active view (All vs Specific Document)
  const activeSkillsList = useMemo(() => {
    if (selectedDocId !== 'all' && selectedCert) {
      let raw = []
      if (Array.isArray(selectedCert.extracted_skills)) {
        raw = selectedCert.extracted_skills
      } else if (typeof selectedCert.extracted_skills === 'string') {
        try {
          raw = JSON.parse(selectedCert.extracted_skills)
        } catch {
          raw = []
        }
      }
      return raw.map((name) => ({
        name,
        count: 1,
        docs: [
          {
            id: selectedCert.id,
            title: selectedCert.title,
            organization: selectedCert.organization,
            document_type: selectedCert.document_type,
          },
        ],
        ...categorizeSkill(name),
      }))
    }

    // "All" mode: Gather all detected skills from analytics or portfolio
    const analyticsSkills = Object.entries(analytics?.skills_distribution || {}).map(([name, count]) => ({
      name,
      count,
      docs: skillToDocsMap[name] || [],
      ...categorizeSkill(name),
    }))

    // If analytics is still hydrating or missing some skills from portfolio, merge seamlessly
    const seen = new Set(analyticsSkills.map((s) => s.name.toLowerCase()))
    const extraFromPortfolio = []
    Object.keys(skillToDocsMap).forEach((name) => {
      if (!seen.has(name.toLowerCase())) {
        extraFromPortfolio.push({
          name,
          count: skillToDocsMap[name]?.length || 1,
          docs: skillToDocsMap[name] || [],
          ...categorizeSkill(name),
        })
        seen.add(name.toLowerCase())
      }
    })

    return [...analyticsSkills, ...extraFromPortfolio].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
  }, [selectedDocId, selectedCert, analytics, skillToDocsMap])

  // Filter by search query and category
  const filteredSkills = useMemo(() => {
    return activeSkillsList.filter((item) => {
      const matchesSearch = item.name.toLowerCase().includes(filterQuery.toLowerCase())
      const matchesCategory = activeCategoryFilter === 'All' || item.category === activeCategoryFilter
      return matchesSearch && matchesCategory
    })
  }, [activeSkillsList, filterQuery, activeCategoryFilter])

  // Categories present in the current view
  const categoriesPresent = useMemo(() => {
    const set = new Set(activeSkillsList.map((s) => s.category))
    return ['All', ...Array.from(set)]
  }, [activeSkillsList])

  const isLoading = analyticsLoading && portfolioLoading

  if (isLoading) {
    return (
      <div className="single-screen-tab-wrapper" style={{ maxWidth: 1240, width: '100%', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 36, height: 36, borderRadius: '50%', border: '2px solid var(--brand-ice)', borderTopColor: 'transparent', animation: 'spin 0.8s linear infinite' }} />
      </div>
    )
  }

  return (
    <div className="single-screen-tab-wrapper" style={{ maxWidth: 1240, width: '100%', margin: '0 auto', height: '100%', maxHeight: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Top Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '10px', flexShrink: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
            <span className="status-beacon" />
            <span style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--brand-ice)' }}>
              Entity Extraction & Accreditation Intelligence
            </span>
            <span className="badge badge-primary" style={{ fontSize: '0.68rem', padding: '1px 7px' }}>
              {activeSkillsList.length} Skills Identified
            </span>
          </div>
          <h1 className="spatial-hero-title" style={{ fontSize: '1.45rem', margin: 0 }}>
            Skills & Competencies Intelligence
          </h1>
        </div>

        {/* Action Button & Search Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ position: 'relative', width: '220px' }}>
            <Search size={13} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              className="glass-input-spatial"
              placeholder="Search detected skills..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              style={{ paddingLeft: '30px', paddingRight: '10px', paddingTop: '6px', paddingBottom: '6px', fontSize: '0.78rem', borderRadius: 'var(--radius-full)' }}
            />
          </div>

          <button onClick={() => navigate('/upload')} className="btn-liquid btn-liquid-primary" style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
            <Upload size={13} />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* DOCUMENT SELECTOR STRIP (Interactive Certificate Filter — 100% Visible & Clickable) */}
      <div
        className="glass-panel"
        style={{
          padding: '10px 14px',
          marginBottom: '10px',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          flexShrink: 0,
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--glass-border)',
        }}
      >
        {/* Top bar of selector: Label + Dropdown selector for instant 1-click access to ALL documents */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.76rem', fontWeight: 700, color: 'var(--brand-ice)' }}>
              <Filter size={13} />
              <span>Filter by Document:</span>
            </div>

            {/* Direct Dropdown: Guarantees every single document can be selected without any scrolling */}
            <select
              value={selectedDocId}
              onChange={(e) => {
                setSelectedDocId(e.target.value)
                setActiveCategoryFilter('All')
              }}
              style={{
                fontSize: '0.74rem',
                padding: '4px 10px',
                borderRadius: '8px',
                background: 'rgba(15, 23, 42, 0.95)',
                border: '1px solid var(--glass-border)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                outline: 'none',
                minWidth: '240px',
              }}
            >
              <option value="all" style={{ background: '#0f172a', color: '#fff' }}>
                ✨ All Documents ({certificates.length}) — {Object.keys(skillToDocsMap).length || 22} total skills
              </option>
              {certificates.map((cert) => {
                const count = getSkillCount(cert)
                const shortTitle = getCleanCertTitle(cert)
                const docType = (cert.document_type || '').toLowerCase()
                const isIdDoc = ['aadhaar', 'voter_id', 'voter', 'pan'].includes(docType)
                const isResume = docType === 'resume'
                return (
                  <option key={cert.id} value={cert.id} style={{ background: '#0f172a', color: '#fff' }}>
                    {isResume ? '📄' : isIdDoc ? '💳' : '🏆'} {shortTitle} {count > 0 ? `(${count} skills)` : '(Identity Record)'}
                  </option>
                )
              })}
            </select>
          </div>

          <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>
            {selectedDocId === 'all'
              ? `Showing all ${filteredSkills.length} competencies across ${certificates.length} credentials`
              : `Showing ${filteredSkills.length} competencies from selected credential`}
          </div>
        </div>

        {/* Document Filter Pills: Wrapped so ALL 6 pills are completely visible and clickable */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
          <button
            onClick={() => {
              setSelectedDocId('all')
              setActiveCategoryFilter('All')
            }}
            className={`glass-pill ${selectedDocId === 'all' ? 'active' : ''}`}
            style={{ fontSize: '0.74rem', padding: '5px 12px', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Sparkles size={12} />
            <span>All Documents ({certificates.length})</span>
            <span style={{ fontSize: '0.64rem', background: 'rgba(56, 189, 248, 0.2)', padding: '1px 6px', borderRadius: '8px', fontWeight: 700 }}>
              {Object.keys(skillToDocsMap).length || 22} skills
            </span>
          </button>

          {certificates.map((cert) => {
            const count = getSkillCount(cert)
            const shortTitle = getCleanCertTitle(cert)
            const docType = (cert.document_type || '').toLowerCase()
            const isIdDoc = ['aadhaar', 'voter_id', 'voter', 'pan'].includes(docType)
            const isResume = docType === 'resume'

            return (
              <button
                key={cert.id}
                onClick={() => {
                  setSelectedDocId(cert.id)
                  setActiveCategoryFilter('All')
                }}
                className={`glass-pill ${selectedDocId === cert.id ? 'active' : ''}`}
                style={{
                  fontSize: '0.74rem',
                  padding: '5px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  border: selectedDocId === cert.id ? '1px solid var(--brand-ice)' : '1px solid var(--glass-border)',
                }}
                title={cert.title}
              >
                {isResume ? <FileText size={12} style={{ color: 'var(--brand-cyan)' }} /> : isIdDoc ? <ShieldCheck size={12} style={{ color: 'var(--brand-emerald)' }} /> : <Award size={12} style={{ color: 'var(--brand-amber)' }} />}
                <span>{shortTitle}</span>
                <span
                  style={{
                    fontSize: '0.64rem',
                    background: count > 0 ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255, 255, 255, 0.08)',
                    color: count > 0 ? 'var(--brand-ice)' : 'var(--text-tertiary)',
                    padding: '1px 6px',
                    borderRadius: '8px',
                    fontWeight: 700,
                  }}
                >
                  {count > 0 ? `${count} skills` : 'ID Card'}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* SELECTED DOCUMENT DETAIL BANNER (When viewing a specific certificate) */}
      {selectedCert && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel glass-specular-glow"
          style={{
            padding: '10px 14px',
            marginBottom: '10px',
            borderRadius: '14px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '10px',
            flexShrink: 0,
            border: '1px solid rgba(56, 189, 248, 0.2)',
            background: 'linear-gradient(90deg, rgba(56, 189, 248, 0.08), rgba(99, 102, 241, 0.04))',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: 34, height: 34, borderRadius: '10px', background: 'rgba(56, 189, 248, 0.18)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--brand-ice)', flexShrink: 0 }}>
              {selectedCert.document_type === 'resume' ? <FileText size={16} /> : selectedCert.document_type?.includes('aadhaar') || selectedCert.document_type?.includes('voter') ? <ShieldCheck size={16} /> : <Award size={16} />}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  {selectedCert.title || 'Verified Document'}
                </span>
                <span className="badge badge-primary" style={{ fontSize: '0.64rem', padding: '1px 6px' }}>
                  {selectedCert.category || selectedCert.document_type || 'Accredited'}
                </span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '1px' }}>
                {selectedCert.organization || 'Verified Authority'} • {selectedCert.issue_date || 'Accredited on record'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={() => navigate(`/portfolio?certId=${selectedCert.id}`)}
              className="btn-liquid btn-liquid-secondary"
              style={{ fontSize: '0.74rem', padding: '5px 12px', display: 'flex', alignItems: 'center', gap: '5px' }}
            >
              <span>View in Portfolio</span>
              <ExternalLink size={12} />
            </button>
            <button
              onClick={() => setSelectedDocId('all')}
              className="glass-pill"
              style={{ fontSize: '0.72rem', padding: '4px 10px' }}
            >
              Back to All Skills
            </button>
          </div>
        </motion.div>
      )}

      {/* Category Filter Pills (When multiple categories exist) */}
      {categoriesPresent.length > 2 && (
        <div style={{ display: 'flex', gap: '6px', marginBottom: '10px', overflowX: 'auto', flexShrink: 0, paddingBottom: '2px' }}>
          {categoriesPresent.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategoryFilter(cat)}
              className={`glass-pill ${activeCategoryFilter === cat ? 'active' : ''}`}
              style={{ fontSize: '0.72rem', padding: '4px 10px' }}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* SKILLS CONSTELLATION GRID (Single Screen, Internally Scrollable) */}
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', paddingRight: '4px' }}>
        {filteredSkills.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '10px' }}>
            {filteredSkills.map((item) => {
              const IconComponent = item.icon || Sparkles

              return (
                <motion.div
                  key={item.name}
                  layout
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ y: -2, borderColor: 'var(--brand-ice)' }}
                  className="glass-card-spatial glass-specular-glow"
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    borderRadius: '14px',
                    border: '1px solid var(--glass-border)',
                    background: 'var(--glass-elevated)',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  {/* Top: Icon + Skill Name + Category Badge */}
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div
                          style={{
                            width: 32,
                            height: 32,
                            borderRadius: '10px',
                            background: `rgba(${item.color === 'var(--brand-cyan)' ? '6, 182, 212' : item.color === 'var(--brand-emerald)' ? '16, 185, 129' : '99, 102, 241'}, 0.15)`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: item.color,
                            flexShrink: 0,
                          }}
                        >
                          <IconComponent size={15} />
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.2 }}>
                            {item.name}
                          </div>
                          <div style={{ fontSize: '0.68rem', color: item.color, fontWeight: 600, marginTop: '2px' }}>
                            {item.category}
                          </div>
                        </div>
                      </div>

                      <span
                        className="glass-pill active"
                        style={{
                          fontSize: '0.66rem',
                          padding: '2px 7px',
                          flexShrink: 0,
                          background: item.count > 1 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(56, 189, 248, 0.12)',
                          color: item.count > 1 ? 'var(--brand-emerald)' : 'var(--brand-ice)',
                        }}
                      >
                        {item.count > 1 ? `${item.count}× Verified` : 'Verified'}
                      </span>
                    </div>

                    {/* Source Certificates Attribution */}
                    <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <div style={{ fontSize: '0.66rem', color: 'var(--text-tertiary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Detected In:
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {item.docs && item.docs.length > 0 ? (
                          item.docs.map((doc, idx) => (
                            <span
                              key={idx}
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedDocId(doc.id)
                              }}
                              style={{
                                fontSize: '0.68rem',
                                color: 'var(--text-secondary)',
                                background: 'rgba(255, 255, 255, 0.04)',
                                border: '1px solid var(--glass-border)',
                                padding: '2px 6px',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                transition: 'all 0.15s',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '3px',
                              }}
                              title="Click to view this document's skills"
                              onMouseEnter={(e) => {
                                e.currentTarget.style.color = 'var(--brand-ice)'
                                e.currentTarget.style.borderColor = 'var(--brand-ice)'
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.color = 'var(--text-secondary)'
                                e.currentTarget.style.borderColor = 'var(--glass-border)'
                              }}
                            >
                              <FileText size={10} style={{ opacity: 0.7 }} />
                              <span style={{ maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                {(doc.title || 'Document').replace(/Student Portfolio & Skill Profile — /g, '').replace(/FlowCV Resume — /g, '')}
                              </span>
                            </span>
                          ))
                        ) : (
                          <span style={{ fontSize: '0.68rem', color: 'var(--text-tertiary)' }}>Accredited Portfolio</span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        ) : selectedCert ? (
          /* Empty state for a specific document (e.g. Identity Document with 0 programming skills) */
          <div className="glass-panel" style={{ textAlign: 'center', padding: '40px 24px', borderRadius: '20px', maxWidth: '640px', margin: '30px auto' }}>
            <ShieldCheck size={40} style={{ color: 'var(--brand-emerald)', marginBottom: '12px' }} />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
              Verified Identity Credential
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', lineHeight: 1.5, margin: '0 auto 16px', maxWidth: '480px' }}>
              <strong>{selectedCert.title}</strong> is a verified legal identification document issued by {selectedCert.organization || 'Government Authority'}.
              It validates your identity and legal accreditation without embedding software technical skills.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
              <button onClick={() => navigate(`/portfolio?certId=${selectedCert.id}`)} className="btn-liquid btn-liquid-primary" style={{ padding: '7px 16px', fontSize: '0.8rem' }}>
                <ExternalLink size={13} />
                <span>Inspect Credential Record</span>
              </button>
              <button onClick={() => setSelectedDocId('all')} className="btn-liquid btn-liquid-secondary" style={{ padding: '7px 16px', fontSize: '0.8rem' }}>
                <span>Back to All Skills</span>
              </button>
            </div>
          </div>
        ) : (
          /* General empty state */
          <div className="glass-panel" style={{ textAlign: 'center', padding: '48px 24px', borderRadius: '24px' }}>
            <Sparkles size={36} style={{ color: 'var(--brand-ice)', marginBottom: '12px' }} />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
              No Skills Matching Criteria
            </h2>
            <p style={{ color: 'var(--text-secondary)', maxWidth: '420px', margin: '0 auto 18px', fontSize: '0.86rem' }}>
              Try adjusting your search filter or select another uploaded document from the selector above.
            </p>
            <button onClick={() => { setFilterQuery(''); setActiveCategoryFilter('All'); setSelectedDocId('all') }} className="btn-liquid btn-liquid-primary" style={{ padding: '8px 18px', fontSize: '0.84rem' }}>
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
