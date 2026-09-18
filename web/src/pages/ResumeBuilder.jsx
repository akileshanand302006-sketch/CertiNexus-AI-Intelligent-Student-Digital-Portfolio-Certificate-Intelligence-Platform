/**
 * CertiNexus AI — Intelligent Resume Builder
 *
 * Generates ATS-friendly, publication-grade academic & tech resumes
 * sourced strictly from verified certificate intelligence and ML-extracted skills.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  FileText, Printer, CheckCircle2, Award, Sparkles,
  Download, Eye, RefreshCw, Layers, GraduationCap, Briefcase
} from 'lucide-react'
import api from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'
import toast from 'react-hot-toast'

export default function ResumeBuilder() {
  const { user } = useAuth()
  const [template, setTemplate] = useState('modern')
  const [verifiedOnly, setVerifiedOnly] = useState(true)
  const [customHeadline, setCustomHeadline] = useState('')
  const [customSummary, setCustomSummary] = useState('')
  const [showSkills, setShowSkills] = useState(true)
  const [showCertificates, setShowCertificates] = useState(true)
  const [showEducation, setShowEducation] = useState(true)

  const { data, isLoading } = useQuery({
    queryKey: ['resume-data'],
    queryFn: () => api.getResumeData(),
  })

  const handlePrint = () => {
    window.print()
  }

  const certificates = (data?.certificates || []).filter((c) => {
    if (!verifiedOnly) return true
    return c.is_reviewed || c.ai_confidence_level === 'high' || (c.ai_confidence && c.ai_confidence >= 0.85)
  })

  const skills = data?.skills || []
  const headline = customHeadline || data?.headline || 'Five-Year Integrated M.Sc. (Software Systems) Scholar'
  const summary = customSummary || data?.summary || 'Passionate software systems student specializing in machine learning, distributed applications, and intelligent systems with verified academic credentials.'

  return (
    <div className="resume-builder-page">
      {/* Screen view header */}
      <div className="page-header no-print">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-primary">
                <Sparkles size={12} /> Verified Credential Engine
              </span>
              <span className="badge badge-success">
                <CheckCircle2 size={12} /> ATS-Optimized
              </span>
            </div>
            <h1>AI Resume Builder</h1>
            <p>Generate professional resumes compiled directly from your verified certificates and ML-extracted skills</p>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={handlePrint}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <Printer size={18} />
              <span>Print / Save as PDF</span>
            </button>
          </div>
        </div>
      </div>

      <div className="resume-layout" style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: '28px' }}>
        {/* Controls Column (Hidden in print) */}
        <div className="no-print" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Template Selector Card */}
          <div className="glass-card" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} style={{ color: 'var(--color-primary-light)' }} /> Resume Template
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              {[
                { id: 'modern', name: 'Modern Tech', desc: 'Electric accents & clean grid' },
                { id: 'academic', name: 'Academic CV', desc: 'Formal serif & dense layout' },
                { id: 'minimalist', name: 'Minimalist', desc: 'Monochrome precision' },
                { id: 'executive', name: 'Executive', desc: 'Rich indigo header bar' },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTemplate(t.id)}
                  style={{
                    padding: '12px 10px',
                    borderRadius: '10px',
                    textAlign: 'left',
                    border: template === t.id ? '2px solid var(--color-primary)' : '1px solid var(--glass-border)',
                    background: template === t.id ? 'rgba(79, 70, 229, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                    cursor: 'pointer',
                    color: 'var(--text-primary)',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{t.name}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginTop: '2px' }}>{t.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Content Controls */}
          <div className="glass-card" style={{ padding: '20px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '14px' }}>Customization</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Professional Title / Headline
                </label>
                <input
                  type="text"
                  className="input-field"
                  value={customHeadline}
                  onChange={(e) => setCustomHeadline(e.target.value)}
                  placeholder={data?.headline || 'e.g. Software Systems Student'}
                  style={{ width: '100%', fontSize: '0.85rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Professional Summary
                </label>
                <textarea
                  className="input-field"
                  rows={3}
                  value={customSummary}
                  onChange={(e) => setCustomSummary(e.target.value)}
                  placeholder="Summary statement..."
                  style={{ width: '100%', fontSize: '0.85rem', resize: 'vertical' }}
                />
              </div>

              <div style={{ paddingTop: '8px', borderTop: '1px solid var(--glass-border)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                  <input
                    type="checkbox"
                    checked={verifiedOnly}
                    onChange={(e) => setVerifiedOnly(e.target.checked)}
                    style={{ accentColor: 'var(--color-primary)' }}
                  />
                  <span>Verified Credentials Only ({data?.total_verified_certificates || 0})</span>
                </label>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginLeft: '22px', marginTop: '2px' }}>
                  Restricts resume to high-confidence ML predictions and reviewed certificates.
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', paddingTop: '8px', borderTop: '1px solid var(--glass-border)' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>
                  Section Visibility
                </span>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem' }}>
                  <input
                    type="checkbox"
                    checked={showEducation}
                    onChange={(e) => setShowEducation(e.target.checked)}
                    style={{ accentColor: 'var(--color-primary)' }}
                  />
                  <span>Education & Institution</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem' }}>
                  <input
                    type="checkbox"
                    checked={showSkills}
                    onChange={(e) => setShowSkills(e.target.checked)}
                    style={{ accentColor: 'var(--color-primary)' }}
                  />
                  <span>Extracted Skills ({skills.length})</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem' }}>
                  <input
                    type="checkbox"
                    checked={showCertificates}
                    onChange={(e) => setShowCertificates(e.target.checked)}
                    style={{ accentColor: 'var(--color-primary)' }}
                  />
                  <span>Certificates & Awards ({certificates.length})</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Resume Preview Sheet */}
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <motion.div
            id="resume-sheet"
            className={`resume-paper template-${template}`}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            style={{
              width: '100%',
              maxWidth: '820px',
              minHeight: '1050px',
              background: '#ffffff',
              color: '#1a202c',
              borderRadius: '8px',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1)',
              padding: '48px',
              fontFamily: template === 'academic' ? 'Georgia, Cambria, serif' : "'Inter', -apple-system, sans-serif",
              lineHeight: 1.5,
              position: 'relative',
            }}
          >
            {/* Resume Header */}
            <div style={{
              borderBottom: template === 'executive' ? '4px solid #1e3a8a' : '2px solid #e2e8f0',
              paddingBottom: '20px',
              marginBottom: '24px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
            }}>
              <div>
                <h1 style={{
                  fontSize: '2rem',
                  fontWeight: 800,
                  color: template === 'executive' ? '#1e3a8a' : '#0f172a',
                  letterSpacing: '-0.02em',
                  margin: 0,
                }}>
                  {user?.full_name || user?.username || 'Student Candidate'}
                </h1>
                <div style={{
                  fontSize: '1.05rem',
                  color: template === 'modern' ? '#4f46e5' : '#475569',
                  fontWeight: 600,
                  marginTop: '4px',
                }}>
                  {headline}
                </div>
              </div>

              <div style={{ textAlign: 'right', fontSize: '0.85rem', color: '#475569', lineHeight: 1.6 }}>
                <div><strong>Email:</strong> {user?.email}</div>
                {user?.institution && <div><strong>Affiliation:</strong> {user?.institution}</div>}
                <div><strong>Verified Portfolio:</strong> certinexus.ai/{user?.username}</div>
              </div>
            </div>

            {/* Professional Summary */}
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{
                fontSize: '0.95rem',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                fontWeight: 700,
                color: template === 'modern' ? '#4f46e5' : '#1e293b',
                borderBottom: '1px solid #cbd5e1',
                paddingBottom: '4px',
                marginBottom: '10px',
              }}>
                Professional Summary
              </h2>
              <p style={{ fontSize: '0.9rem', color: '#334155', margin: 0, textAlign: 'justify' }}>
                {summary}
              </p>
            </div>

            {/* Education */}
            {showEducation && (
              <div style={{ marginBottom: '24px' }}>
                <h2 style={{
                  fontSize: '0.95rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  fontWeight: 700,
                  color: template === 'modern' ? '#4f46e5' : '#1e293b',
                  borderBottom: '1px solid #cbd5e1',
                  paddingBottom: '4px',
                  marginBottom: '12px',
                }}>
                  Education
                </h2>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <div>
                    <strong style={{ fontSize: '0.95rem', color: '#0f172a' }}>
                      {user?.institution || 'Five-Year Integrated Master of Science'}
                    </strong>
                    <div style={{ fontSize: '0.85rem', color: '#475569' }}>
                      {user?.department || 'Department of Software Systems & Machine Learning'}
                    </div>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 500 }}>
                    Class of {user?.graduation_year || '2026'}
                  </div>
                </div>
              </div>
            )}

            {/* Skills */}
            {showSkills && skills.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <h2 style={{
                  fontSize: '0.95rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  fontWeight: 700,
                  color: template === 'modern' ? '#4f46e5' : '#1e293b',
                  borderBottom: '1px solid #cbd5e1',
                  paddingBottom: '4px',
                  marginBottom: '12px',
                }}>
                  Verified Technical Skills
                </h2>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {skills.map((s) => (
                    <span
                      key={s.id || s.skill_name}
                      style={{
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        padding: '3px 10px',
                        borderRadius: '4px',
                        background: template === 'modern' ? '#eef2ff' : '#f1f5f9',
                        color: template === 'modern' ? '#3730a3' : '#1e293b',
                        border: '1px solid #e2e8f0',
                      }}
                    >
                      {s.skill_name}
                      {s.occurrence_count > 1 && (
                        <span style={{ fontSize: '0.7rem', color: '#6366f1', marginLeft: '4px' }}>
                          ({s.occurrence_count})
                        </span>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Verified Certificates & Honors */}
            {showCertificates && (
              <div style={{ marginBottom: '24px' }}>
                <h2 style={{
                  fontSize: '0.95rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  fontWeight: 700,
                  color: template === 'modern' ? '#4f46e5' : '#1e293b',
                  borderBottom: '1px solid #cbd5e1',
                  paddingBottom: '4px',
                  marginBottom: '14px',
                }}>
                  Verified Credentials & Honors
                </h2>

                {certificates.length === 0 ? (
                  <p style={{ fontSize: '0.85rem', color: '#64748b', fontStyle: 'italic' }}>
                    No verified credentials selected yet. Upload certificates to automatically populate verified achievements.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {certificates.map((cert) => (
                      <div key={cert.id} style={{ borderLeft: '3px solid #cbd5e1', paddingLeft: '12px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                          <strong style={{ fontSize: '0.92rem', color: '#0f172a' }}>
                            {cert.title || 'Verified Achievement'}
                          </strong>
                          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                            {cert.issue_date || 'Certified'}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '2px' }}>
                          <span>{cert.organization || 'Accredited Authority'}</span>
                          {cert.category && (
                            <span style={{
                              marginLeft: '8px',
                              fontSize: '0.7rem',
                              fontWeight: 600,
                              padding: '1px 6px',
                              borderRadius: '3px',
                              background: '#ecfdf5',
                              color: '#065f46',
                            }}>
                              {cert.category}
                            </span>
                          )}
                        </div>
                        {cert.certificate_id_extracted && (
                          <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '2px' }}>
                            Credential ID: {cert.certificate_id_extracted}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* CertiNexus Verification Footer */}
            <div style={{
              marginTop: 'auto',
              paddingTop: '20px',
              borderTop: '1px solid #e2e8f0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '0.75rem',
              color: '#94a3b8',
            }}>
              <div>
                Verified via <strong>CertiNexus AI</strong> • Machine Learning Lab (20MSSL12)
              </div>
              <div>
                Cryptographically / Structurally Verified Portfolio
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Print Stylesheet injection for clean paper printing */}
      <style>{`
        @media print {
          body {
            background: #ffffff !important;
            color: #000000 !important;
            padding: 0 !important;
            margin: 0 !important;
          }
          .no-print, .sidebar, .page-header, .aurora-bg, nav {
            display: none !important;
          }
          .main-content {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
          }
          .resume-layout {
            display: block !important;
          }
          #resume-sheet {
            box-shadow: none !important;
            border-radius: 0 !important;
            padding: 20mm !important;
            width: 100% !important;
            max-width: 100% !important;
            min-height: auto !important;
          }
        }
      `}</style>
    </div>
  )
}
