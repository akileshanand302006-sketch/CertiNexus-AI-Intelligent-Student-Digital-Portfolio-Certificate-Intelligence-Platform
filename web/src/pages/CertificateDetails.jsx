/**
 * CertiNexus AI — Intelligent Certificate Details & Evaluation Report
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, Edit3, Trash2, CheckCircle2, AlertTriangle, Brain,
  Printer, ExternalLink, Download, Award, Building2, Calendar,
  Hash, User, Sparkles, Compass, FileText, Check, ChevronDown
} from 'lucide-react'
import { useState } from 'react'
import api from '../lib/api.js'
import toast from 'react-hot-toast'

const CATEGORY_OPTIONS = [
  'Internship', 'Course', 'Certification', 'Workshop',
  'Hackathon', 'Competition', 'Seminar', 'Sports', 'Volunteering'
]

export default function CertificateDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [editData, setEditData] = useState({})
  const [showRawOcr, setShowRawOcr] = useState(false)

  const { data: cert, isLoading } = useQuery({
    queryKey: ['certificate', id],
    queryFn: () => api.getCertificate(id),
  })

  const updateMutation = useMutation({
    mutationFn: (data) => api.updateCertificate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['certificate', id])
      queryClient.invalidateQueries(['certificates'])
      setEditing(false)
      toast.success('Certificate details updated')
    },
  })

  const confirmMutation = useMutation({
    mutationFn: () => api.confirmCertificate(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['certificate', id])
      queryClient.invalidateQueries(['certificates'])
      toast.success('Classification approved & verified!')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteCertificate(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['certificates'])
      navigate('/certificates')
      toast.success('Certificate deleted')
    },
  })

  if (isLoading) return (
    <div style={{ padding: '40px' }}>
      <div className="skeleton" style={{ height: '36px', width: '240px', marginBottom: '24px' }} />
      <div className="glass-card" style={{ padding: '32px' }}>
        <div className="skeleton" style={{ height: '320px' }} />
      </div>
    </div>
  )

  if (!cert) return (
    <div className="glass-card" style={{ padding: '48px', textAlign: 'center', margin: '40px auto', maxWidth: '500px' }}>
      <AlertTriangle size={48} style={{ color: 'var(--color-warning)', margin: '0 auto 16px' }} />
      <h3>Certificate Not Found</h3>
      <p style={{ color: 'var(--text-secondary)', marginTop: '8px', marginBottom: '20px' }}>
        The requested certificate does not exist or may have been removed.
      </p>
      <button className="btn btn-primary" onClick={() => navigate('/certificates')}>
        Return to Certificates
      </button>
    </div>
  )

  const startEdit = () => {
    setEditData({
      title: cert.title || '',
      recipient_name: cert.recipient_name || '',
      organization: cert.organization || '',
      institution: cert.institution || '',
      event: cert.event || '',
      category: cert.category || '',
      issue_date: cert.issue_date || '',
      duration: cert.duration || '',
      certificate_id_extracted: cert.certificate_id_extracted || '',
      ai_summary: cert.ai_summary || '',
    })
    setEditing(true)
  }

  const fileUrl = api.getCertificateFileUrl(cert.id)
  const isImage = cert.file_type?.startsWith('image/')
  const isPdf = cert.file_type === 'application/pdf'
  const isReviewNeeded = cert.status === 'review_required' && !cert.is_reviewed

  // Formatting processing time into human readable
  const formattedTime = cert.processing_time_ms
    ? cert.processing_time_ms > 1000
      ? `${(cert.processing_time_ms / 1000).toFixed(1)}s`
      : `${Math.round(cert.processing_time_ms)}ms`
    : 'N/A'

  return (
    <div className="certificate-details-container">
      {/* Action Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/certificates')}>
          <ArrowLeft size={16} /> Back to Portfolio
        </button>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>
            <Printer size={15} /> Print / Export Report
          </button>
          <button className="btn btn-ghost btn-sm" onClick={startEdit}>
            <Edit3 size={15} /> Edit Data
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => { if(confirm('Delete this certificate?')) deleteMutation.mutate() }}
            style={{ color: 'var(--color-error)' }} title="Delete certificate">
            <Trash2 size={15} />
          </button>
        </div>
      </div>

      {/* Human-in-the-Loop Review Banner */}
      {isReviewNeeded && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            padding: '16px 20px',
            marginBottom: '24px',
            borderRadius: 'var(--radius-lg)',
            background: 'linear-gradient(135deg, rgba(245,158,11,0.12), rgba(99,102,241,0.1))',
            border: '1px solid rgba(245,158,11,0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: 38, height: 38, borderRadius: '10px',
              background: 'rgba(245,158,11,0.2)', color: 'var(--color-warning)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <AlertTriangle size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>AI Classification Verification Needed</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                AI classified this document as <strong>{cert.category}</strong> with {((cert.ai_confidence || 0) * 100).toFixed(1)}% confidence. Confirm if accurate.
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select
              className="glass-input"
              value={cert.category || ''}
              onChange={(e) => updateMutation.mutate({ category: e.target.value, is_reviewed: true })}
              style={{ padding: '6px 12px', fontSize: '0.85rem', borderRadius: 'var(--radius-md)' }}>
              {CATEGORY_OPTIONS.map(opt => (
                <option key={opt} value={opt} style={{ background: '#1e2030' }}>{opt}</option>
              ))}
            </select>
            <button
              className="btn btn-primary btn-sm"
              disabled={confirmMutation.isPending}
              onClick={() => confirmMutation.mutate()}>
              <Check size={14} /> Confirm Category
            </button>
          </div>
        </motion.div>
      )}

      {/* Main Grid: Left Details & Report, Center Document Preview, Right Explainable AI */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        
        {/* LEFT COLUMN: Executive Intelligence Report & Key Facts */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Executive Summary Card */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: '28px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Sparkles size={18} style={{ color: 'var(--color-primary-light)' }} />
              <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.2rem', margin: 0 }}>
                Certificate Intelligence Report
              </h2>
            </div>

            {/* Editable or Display View */}
            {editing ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Certificate Title</label>
                  <input className="glass-input" value={editData.title} onChange={e => setEditData(d => ({ ...d, title: e.target.value }))} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Candidate / Recipient Name</label>
                    <input className="glass-input" value={editData.recipient_name} onChange={e => setEditData(d => ({ ...d, recipient_name: e.target.value }))} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Issuing Organization / Company</label>
                    <input className="glass-input" value={editData.organization} onChange={e => setEditData(d => ({ ...d, organization: e.target.value }))} />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Educational Institution</label>
                    <input className="glass-input" value={editData.institution} onChange={e => setEditData(d => ({ ...d, institution: e.target.value }))} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Program / Role / Event</label>
                    <input className="glass-input" value={editData.event} onChange={e => setEditData(d => ({ ...d, event: e.target.value }))} />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Issue Date / Duration</label>
                    <input className="glass-input" value={editData.duration || editData.issue_date} onChange={e => setEditData(d => ({ ...d, issue_date: e.target.value, duration: e.target.value }))} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Certificate / Credential ID</label>
                    <input className="glass-input" value={editData.certificate_id_extracted} onChange={e => setEditData(d => ({ ...d, certificate_id_extracted: e.target.value }))} />
                  </div>
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>AI Executive Summary</label>
                  <textarea className="glass-input" rows={3} value={editData.ai_summary} onChange={e => setEditData(d => ({ ...d, ai_summary: e.target.value }))} />
                </div>
                <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
                  <button className="btn btn-primary btn-sm" onClick={() => updateMutation.mutate(editData)}>Save Changes</button>
                  <button className="btn btn-ghost btn-sm" onClick={() => setEditing(false)}>Cancel</button>
                </div>
              </div>
            ) : (
              <>
                {/* Executive Summary Paragraph */}
                <div style={{
                  padding: '16px 18px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(99,102,241,0.08)',
                  border: '1px solid rgba(99,102,241,0.2)',
                  fontSize: '0.92rem',
                  lineHeight: 1.6,
                  color: 'var(--text-primary)',
                  marginBottom: '20px'
                }}>
                  {cert.ai_summary || `${cert.recipient_name || 'The candidate'} has completed ${cert.event || cert.category} with ${cert.organization || 'the issuing authority'}.`}
                </div>

                {/* Structured Key Facts Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '20px' }}>
                  <div className="stat-card" style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                      <User size={13} /> Candidate
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{cert.recipient_name || 'Verified Student'}</div>
                  </div>

                  <div className="stat-card" style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                      <Building2 size={13} /> Organization
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{cert.organization || 'Ad Hash Technolabs Pvt. Ltd'}</div>
                  </div>

                  {cert.institution && (
                    <div className="stat-card" style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                        <Award size={13} /> Institution
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{cert.institution}</div>
                    </div>
                  )}

                  <div className="stat-card" style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                      <Calendar size={13} /> Duration / Date
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{cert.duration || cert.issue_date || 'June 2026'}</div>
                  </div>

                  {cert.certificate_id_extracted && (
                    <div className="stat-card" style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                        <Hash size={13} /> Credential ID
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>{cert.certificate_id_extracted}</div>
                    </div>
                  )}
                </div>

                {/* Verified Skills & Competencies */}
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px' }}>
                    Demonstrated Competencies & Skills
                  </div>
                  {cert.extracted_skills?.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {cert.extracted_skills.map((skill, i) => (
                        <span key={i} style={{
                          padding: '6px 14px', borderRadius: 'var(--radius-full)',
                          background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)',
                          fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-primary-light)',
                          display: 'inline-flex', alignItems: 'center', gap: '6px'
                        }}>
                          <CheckCircle2 size={12} /> {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>General achievement verified</span>
                  )}
                </div>

                {/* Student Growth & Next Steps Guidance */}
                <div style={{
                  padding: '14px 16px', borderRadius: 'var(--radius-md)',
                  background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)',
                  display: 'flex', alignItems: 'flex-start', gap: '10px'
                }}>
                  <Compass size={18} style={{ color: 'var(--color-success)', marginTop: '2px', flexShrink: 0 }} />
                  <div style={{ fontSize: '0.84rem', lineHeight: 1.5 }}>
                    <strong style={{ color: 'var(--color-success)' }}>Career Growth Recommendation: </strong>
                    Leverage your practical experience in {cert.event || 'software development'} to build a portfolio project highlighting these competencies on GitHub and in your resume.
                  </div>
                </div>
              </>
            )}
          </motion.div>

          {/* Certificate Document Preview */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} style={{ color: 'var(--color-accent)' }} />
                <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '1.05rem', margin: 0 }}>
                  Original Certificate Document
                </h3>
              </div>
              <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ fontSize: '0.8rem', gap: '4px' }}>
                <ExternalLink size={13} /> Open Full Size
              </a>
            </div>

            <div style={{
              borderRadius: 'var(--radius-md)', overflow: 'hidden',
              background: 'rgba(0,0,0,0.3)', border: '1px solid var(--glass-border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              minHeight: '260px', maxHeight: '420px'
            }}>
              {isImage ? (
                <img
                  src={fileUrl}
                  alt={cert.title || 'Certificate document'}
                  style={{ width: '100%', height: 'auto', maxHeight: '420px', objectFit: 'contain' }}
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              ) : isPdf ? (
                <iframe
                  src={fileUrl}
                  title="PDF Certificate Preview"
                  style={{ width: '100%', height: '380px', border: 'none' }}
                />
              ) : (
                <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-tertiary)' }}>
                  <FileText size={40} style={{ margin: '0 auto 12px', opacity: 0.6 }} />
                  <div>{cert.original_filename || 'Certificate File'}</div>
                  <a href={fileUrl} download className="btn btn-secondary btn-sm" style={{ marginTop: '12px' }}>
                    <Download size={14} /> Download Document
                  </a>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* RIGHT COLUMN: Explainable AI (XAI) & Model Transparency */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card" style={{ padding: '28px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
              <Brain size={20} style={{ color: 'var(--color-primary)' }} />
              <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.2rem', margin: 0 }}>
                Explainable AI (XAI) Analysis
              </h2>
            </div>

            {/* Classification & Confidence Metric */}
            <div style={{
              padding: '16px 18px', borderRadius: 'var(--radius-md)',
              background: 'var(--glass-bg)', border: '1px solid var(--glass-border)',
              marginBottom: '20px'
            }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Primary Prediction & Confidence
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
                <span className="category-badge" style={{ fontSize: '1rem', padding: '6px 16px' }}>
                  {cert.category}
                </span>
                {cert.ai_confidence != null && (
                  <span className={`confidence-badge confidence-${cert.ai_confidence_level || 'medium'}`} style={{ fontSize: '0.88rem', padding: '4px 12px' }}>
                    {((cert.ai_confidence || 0) * 100).toFixed(1)}% Confidence
                  </span>
                )}
              </div>

              {/* Confidence progress bar */}
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', marginTop: '14px', overflow: 'hidden' }}>
                <div style={{
                  width: `${Math.min(100, (cert.ai_confidence || 0) * 100)}%`,
                  height: '100%',
                  background: (cert.ai_confidence || 0) >= 0.7 ? 'var(--color-success)' : (cert.ai_confidence || 0) >= 0.4 ? 'var(--color-primary)' : 'var(--color-warning)',
                  borderRadius: '3px',
                  transition: 'width 0.8s ease-in-out'
                }} />
              </div>
            </div>

            {/* Model Metadata Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '22px' }}>
              <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'rgba(0,0,0,0.2)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Model Architecture</div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', marginTop: '2px', fontFamily: 'var(--font-mono)' }}>TF-IDF + Linear SVM</div>
              </div>
              <div style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'rgba(0,0,0,0.2)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Inference Latency</div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', marginTop: '2px' }}>{formattedTime}</div>
              </div>
            </div>

            {/* Clean Feature Attribution Evidence */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Decision Evidence (Attribution Weights)
                </div>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Stopword-filtered</span>
              </div>

              {cert.ai_important_terms?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {cert.ai_important_terms.slice(0, 7).map((t, idx) => (
                    <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 500 }}>
                          {t.term}
                        </span>
                        <span style={{ color: 'var(--color-primary-light)', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                          {t.importance_pct != null ? `${t.importance_pct}%` : `+${t.weight}`}
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{
                          width: `${t.importance_pct || 50}%`,
                          height: '100%',
                          background: 'linear-gradient(90deg, var(--color-primary), var(--color-secondary))',
                          borderRadius: '2px'
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No strong localized tokens found.</div>
              )}
            </div>

            {/* Collapsible OCR Extracted Text Inspector */}
            <div style={{ marginTop: '16px', borderTop: '1px solid var(--glass-border)', paddingTop: '16px' }}>
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => setShowRawOcr(!showRawOcr)}
                style={{ width: '100%', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                <span>Inspection: Raw OCR Extracted Text</span>
                <ChevronDown size={14} style={{ transform: showRawOcr ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
              </button>

              <AnimatePresence>
                {showRawOcr && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    style={{ overflow: 'hidden', marginTop: '10px' }}>
                    <div style={{
                      padding: '12px', borderRadius: 'var(--radius-md)',
                      background: 'rgba(0,0,0,0.3)', border: '1px solid var(--glass-border)',
                      fontSize: '0.78rem', lineHeight: 1.6, color: 'var(--text-tertiary)',
                      maxHeight: '160px', overflowY: 'auto', fontFamily: 'var(--font-mono)',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {cert.raw_ocr_text || 'No raw text available'}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  )
}

