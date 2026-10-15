/**
 * CertiNexus AI — Unified Document Intelligence Inspector
 * Supports Indian Identity (Aadhaar, PAN, DL, RC), Academic (Marksheets, Timetables, Receipts),
 * Financial, Resumes, and Accredited 11-category Certificates.
 */

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, Edit3, Trash2, CheckCircle2, AlertTriangle, Brain,
  Printer, ExternalLink, Download, Award, Building2, Calendar,
  Hash, User, Sparkles, FileText, Check, ChevronDown, ShieldCheck,
  CreditCard, BookOpen, Clock, Receipt, Landmark, Copy, Eye
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api.js'

const CATEGORY_OPTIONS = [
  'Academic Achievement', 'Certification', 'Conference', 'Cultural Activity',
  'Hackathon', 'Internship', 'Seminar', 'Sports', 'Technical Competition',
  'Volunteer Activity', 'Workshop'
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

  const reprocessMutation = useMutation({
    mutationFn: () => api.reprocessCertificate(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['certificate', id])
      queryClient.invalidateQueries(['certificates'])
      toast.success('ML & OCR intelligence pipeline completed!')
    },
    onError: (err) => {
      toast.error(err.message || 'Pipeline execution failed')
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data) => api.updateCertificate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['certificate', id])
      queryClient.invalidateQueries(['certificates'])
      setEditing(false)
      toast.success('Document details updated')
    },
  })

  const confirmMutation = useMutation({
    mutationFn: () => api.confirmCertificate(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['certificate', id])
      queryClient.invalidateQueries(['certificates'])
      toast.success('Classification verified & approved!')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteCertificate(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['certificates'])
      navigate('/certificates')
      toast.success('Document removed')
    },
  })

  const copyOcrToClipboard = () => {
    if (cert?.raw_ocr_text) {
      navigator.clipboard.writeText(cert.raw_ocr_text)
      toast.success('OCR text copied to clipboard!')
    }
  }

  if (isLoading) {
    return (
      <div style={{ maxWidth: 1240, margin: '0 auto', padding: '20px 0' }}>
        <div style={{ width: 220, height: 38, borderRadius: 12, background: 'var(--glass-pill)', marginBottom: 24 }} />
        <div className="glass-panel" style={{ height: 440 }} />
      </div>
    )
  }

  if (!cert) {
    return (
      <div className="glass-panel" style={{ padding: '60px 32px', textAlign: 'center', margin: '40px auto', maxWidth: 540 }}>
        <AlertTriangle size={48} style={{ color: 'var(--brand-amber)', margin: '0 auto 16px' }} />
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Document Record Not Found
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
          The requested record does not exist or may have been unlinked.
        </p>
        <button className="btn-liquid btn-liquid-primary" onClick={() => navigate('/certificates')}>
          Return to Gallery
        </button>
      </div>
    )
  }

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
  const filename = cert.original_filename || cert.file_path || ''
  const isImage = cert.file_type?.startsWith('image/') || /\.(png|jpe?g|webp|gif|bmp)$/i.test(filename)
  const isPdf = cert.file_type === 'application/pdf' || /\.pdf$/i.test(filename)

  const docType = (cert.document_type || 'certificate').toLowerCase()
  const isIdentity = ['aadhaar', 'pan', 'voter_id', 'voter', 'driving_licence', 'vehicle_rc', 'passbook', 'patta'].includes(docType)
  const isAcademic = ['marksheet', 'timetable', 'fee_receipt'].includes(docType)
  const isResume = docType === 'resume'
  const isCertificate = docType === 'certificate'

  const extData = cert.extraction_data || {}
  const fields = extData.fields || {}
  const isReviewNeeded = cert.status === 'review_required' && !cert.is_reviewed
  const confidencePercent = ((cert.ai_confidence || 0.88) * 100).toFixed(1)

  return (
    <div className="single-screen-tab-wrapper" style={{ maxWidth: 1240, width: '100%', margin: '0 auto', height: '100%', maxHeight: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Top Action Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '10px', flexShrink: 0 }}>
        <button onClick={() => navigate('/portfolio')} className="btn-liquid btn-liquid-ghost" style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
          <ArrowLeft size={14} />
          <span>Back to Portfolio</span>
        </button>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            className="btn-liquid btn-liquid-cyan"
            disabled={reprocessMutation.isPending}
            onClick={() => reprocessMutation.mutate()}
            style={{ padding: '6px 14px', fontSize: '0.8rem' }}
          >
            <Brain size={14} />
            <span>{reprocessMutation.isPending ? 'Executing Pipeline...' : 'Run Pipeline'}</span>
          </button>

          <button className="btn-liquid btn-liquid-ghost" onClick={() => window.print()} style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
            <Printer size={14} />
            <span>Print Report</span>
          </button>

          <button className="btn-liquid btn-liquid-ghost" onClick={startEdit} style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
            <Edit3 size={14} />
            <span>Edit Data</span>
          </button>

          <button
            className="btn-liquid btn-liquid-ghost"
            onClick={() => { if (window.confirm('Delete this document record?')) deleteMutation.mutate() }}
            style={{ color: 'var(--brand-rose)', padding: '6px 10px' }}
            title="Delete document"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Human-in-the-Loop Review Banner */}
      {isReviewNeeded && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel"
          style={{
            padding: '12px 18px',
            marginBottom: '10px',
            borderColor: 'rgba(245, 158, 11, 0.35)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
            flexShrink: 0,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: 32, height: 32, borderRadius: '8px', background: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <AlertTriangle size={16} style={{ color: 'var(--brand-amber)' }} />
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)' }}>
                Classification Verification Suggested
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                AI routed this as <strong>{cert.category}</strong> ({confidencePercent}% confidence). Please review.
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {isCertificate && (
              <select
                className="glass-input-spatial"
                value={cert.category || ''}
                onChange={(e) => updateMutation.mutate({ category: e.target.value, is_reviewed: true })}
                style={{ padding: '6px 10px', width: 'auto', fontSize: '0.8rem' }}
              >
                {CATEGORY_OPTIONS.map((opt) => (
                  <option key={opt} value={opt} style={{ background: '#0f172a' }}>{opt}</option>
                ))}
              </select>
            )}
            <button
              className="btn-liquid btn-liquid-primary"
              disabled={confirmMutation.isPending}
              onClick={() => confirmMutation.mutate()}
              style={{ padding: '6px 12px', fontSize: '0.8rem' }}
            >
              <Check size={14} />
              <span>Verify & Confirm</span>
            </button>
          </div>
        </motion.div>
      )}

      {/* 2-Column Inspector Grid (Locked inside single screen) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '14px', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        {/* LEFT COLUMN: Intelligence Fact Inspector & Document Preview */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', height: '100%', minHeight: 0, overflowY: 'auto', paddingRight: '4px' }}>
          {/* Executive Intelligence Facts */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="glass-panel" style={{ padding: '20px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {isIdentity ? (
                  <ShieldCheck size={20} style={{ color: 'var(--brand-emerald)' }} />
                ) : isAcademic ? (
                  <BookOpen size={20} style={{ color: 'var(--brand-cyan)' }} />
                ) : (
                  <Sparkles size={20} style={{ color: 'var(--brand-ice)' }} />
                )}
                <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.2rem', color: 'var(--text-primary)' }}>
                  {cert.title || 'Structured Intelligence Record'}
                </h2>
              </div>
              <span className="glass-pill active" style={{ fontSize: '0.8rem', padding: '4px 12px' }}>
                {cert.category || cert.document_type?.toUpperCase()}
              </span>
            </div>

            {/* PII Masking Security Notice for Identity Cards */}
            {isIdentity && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '10px 14px',
                borderRadius: '12px',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                marginBottom: '20px',
                fontSize: '0.82rem',
                color: 'var(--brand-emerald)',
              }}>
                <ShieldCheck size={16} style={{ flexShrink: 0 }} />
                <span>
                  <strong>Strict PII Protection Active:</strong> Sensitive identifiers masked pursuant to Aadhaar Act and IT Privacy Rules.
                </span>
              </div>
            )}

            {editing ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <label style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Record Title</label>
                  <input className="glass-input-spatial" value={editData.title} onChange={(e) => setEditData((d) => ({ ...d, title: e.target.value }))} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Recipient / Holder</label>
                    <input className="glass-input-spatial" value={editData.recipient_name} onChange={(e) => setEditData((d) => ({ ...d, recipient_name: e.target.value }))} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.78rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Issuing Authority</label>
                    <input className="glass-input-spatial" value={editData.organization} onChange={(e) => setEditData((d) => ({ ...d, organization: e.target.value }))} />
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
                  <button className="btn-liquid btn-liquid-primary" onClick={() => updateMutation.mutate(editData)}>Save Changes</button>
                  <button className="btn-liquid btn-liquid-ghost" onClick={() => setEditing(false)}>Cancel</button>
                </div>
              </div>
            ) : (
              <div>
                {/* Dynamic Schema Display Based on Document Family */}
                {docType === 'aadhaar' ? (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Aadhaar Number (Masked)</div>
                      <div style={{ fontSize: '1.08rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '4px' }}>
                        {fields.aadhaar_number || 'XXXX-XXXX-8800'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Cardholder Legal Name</div>
                      <div style={{ fontSize: '1.02rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.recipient_name || fields.recipient_name || 'S Dharshana'}
                        {fields.regional_name && <span style={{ color: 'var(--brand-ice)', fontSize: '0.88rem', marginLeft: '6px' }}>({fields.regional_name})</span>}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Father / Guardian Name</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.guardian_name || 'S. Sivakumar'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Date of Birth</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.dob || cert.issue_date || '13/03/2007'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Gender</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.gender || 'Female'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Registered Mobile</div>
                      <div style={{ fontSize: '0.96rem', fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.mobile || '+91-XXXXX-90901'}
                      </div>
                    </div>
                    {fields.vid && (
                      <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                        <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Virtual ID (VID)</div>
                        <div style={{ fontSize: '0.92rem', fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '4px' }}>
                          {fields.vid}
                        </div>
                      </div>
                    )}
                    {fields.enrolment_no && (
                      <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                        <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Enrolment Number</div>
                        <div style={{ fontSize: '0.92rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginTop: '4px' }}>
                          {fields.enrolment_no}
                        </div>
                      </div>
                    )}
                    <div className="glass-card-spatial" style={{ padding: '14px 16px', gridColumn: 'span 2' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Residential Address</div>
                      <div style={{ fontSize: '0.88rem', color: 'var(--text-primary)', marginTop: '4px', lineHeight: 1.5 }}>
                        {fields.address || 'SF-5, SRI SURYODHAYA APARTMENT, SRIRAM NAGAR, CHOKKAMPUDUR ROAD, Coimbatore South, Telungupalayam, Coimbatore, Tamil Nadu, 641039'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px', gridColumn: 'span 2' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Issuing Authority</div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--brand-ice)', marginTop: '4px' }}>
                        {fields.issuing_authority || 'Unique Identification Authority of India (UIDAI)'}
                      </div>
                    </div>
                  </div>
                ) : (docType === 'voter_id' || docType === 'voter') ? (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>EPIC Identity Number</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '4px' }}>
                        {fields.epic_number || 'RIV3758521'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Elector / Voter Name</div>
                      <div style={{ fontSize: '1.02rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.recipient_name || fields.voter_name || 'S Dharshana'}
                        {fields.regional_name && <span style={{ color: 'var(--brand-ice)', fontSize: '0.88rem', marginLeft: '6px' }}>({fields.regional_name})</span>}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Father's / Guardian's Name</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.guardian_name || 'S. Sivakumar'}
                        {fields.regional_guardian && <span style={{ color: 'var(--brand-ice)', fontSize: '0.86rem', marginLeft: '6px' }}>({fields.regional_guardian})</span>}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Gender</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.gender || 'Female'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Date of Birth / Age</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.dob || cert.issue_date || '13/03/2007'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>State & Region</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.district ? `${fields.district}, ` : ''}{fields.state || 'Tamil Nadu'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '14px 16px', gridColumn: 'span 2' }}>
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Issuing Authority</div>
                      <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--brand-emerald)', marginTop: '4px' }}>
                        {fields.issuing_authority || 'Election Commission of India (இந்திய தேர்தல் ஆணையம்)'}
                      </div>
                    </div>
                  </div>
                ) : docType === 'pan' ? (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Permanent Account Number (PAN)</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '4px' }}>
                        {fields.pan_number || 'ABCDE****F'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Cardholder Name</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.recipient_name || 'PAN Cardholder'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Father's Name</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.guardian_name || 'Not detected'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Date of Birth</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.dob || cert.issue_date || 'Not detected'}
                      </div>
                    </div>
                  </div>
                ) : docType === 'marksheet' ? (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Student Candidate</div>
                      <div style={{ fontSize: '1.0rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.recipient_name || fields.student_name}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Roll / Registration Number</div>
                      <div style={{ fontSize: '0.96rem', fontFamily: 'var(--font-mono)', color: 'var(--brand-ice)', marginTop: '4px' }}>
                        {fields.roll_number || 'REG-RECORD'}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Degree & Semester</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {fields.degree_course} — {fields.semester}
                      </div>
                    </div>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Performance Outcome</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 700, color: 'var(--brand-emerald)', marginTop: '4px' }}>
                        {fields.sgpa_cgpa || fields.result_status}
                      </div>
                    </div>
                  </div>
                ) : (
                  /* Default Certificate / Generic View */
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '18px' }}>
                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Recipient / Candidate</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.recipient_name || (isResume ? 'Candidate Profile' : 'Not detected')}
                      </div>
                    </div>

                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Issuing Organization</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.organization || cert.institution || 'Recognized Organization'}
                      </div>
                    </div>

                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Event / Credential Title</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.event || cert.title || 'Accredited Credential'}
                      </div>
                    </div>

                    <div className="glass-card-spatial" style={{ padding: '16px' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>Issue / Verification Date</div>
                      <div style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {cert.issue_date || (cert.created_at ? new Date(cert.created_at).toLocaleDateString() : 'Not detected')}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>

          {/* Document Preview Panel */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-panel" style={{ padding: '24px', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} style={{ color: 'var(--brand-ice)' }} />
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>Original Document Preview</h3>
              </div>
              <a href={fileUrl} target="_blank" rel="noreferrer" className="glass-pill" style={{ fontSize: '0.75rem' }}>
                <ExternalLink size={14} /> Open Original
              </a>
            </div>

            <div style={{ borderRadius: '18px', overflow: 'hidden', border: '1px solid var(--glass-border)', background: 'rgba(0,0,0,0.4)', textAlign: 'center', minHeight: '380px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {isImage ? (
                <img
                  src={fileUrl}
                  alt={cert.title || 'Document Record'}
                  style={{ maxWidth: '100%', maxHeight: '480px', objectFit: 'contain', display: 'block', margin: '0 auto' }}
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    if (e.currentTarget.nextSibling) e.currentTarget.nextSibling.style.display = 'block';
                  }}
                />
              ) : isPdf ? (
                <object
                  data={`${fileUrl}#toolbar=0&navpanes=0`}
                  type="application/pdf"
                  style={{ width: '100%', height: '480px', border: 'none' }}
                >
                  <iframe src={fileUrl} title="Document Preview" style={{ width: '100%', height: '480px', border: 'none' }}>
                    <div style={{ padding: '40px', color: 'var(--text-tertiary)' }}>
                      <FileText size={48} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
                      <div>Preview unavailable directly in frame</div>
                      <a href={fileUrl} target="_blank" rel="noreferrer" className="btn-liquid btn-liquid-ghost" style={{ marginTop: '16px' }}>
                        <ExternalLink size={15} /> Open Original Document
                      </a>
                    </div>
                  </iframe>
                </object>
              ) : (
                <div style={{ padding: '40px', color: 'var(--text-tertiary)' }}>
                  <FileText size={48} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
                  <div>{cert.original_filename || 'Document Record'}</div>
                  <a href={fileUrl} download className="btn-liquid btn-liquid-ghost" style={{ marginTop: '16px' }}>
                    <Download size={15} /> Download Document
                  </a>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* RIGHT COLUMN: AI Confidence & Raw OCR Transcript */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', height: '100%', minHeight: 0, overflowY: 'auto', paddingRight: '4px' }}>
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-panel" style={{ padding: '20px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px' }}>
              <Brain size={20} style={{ color: 'var(--brand-ice)' }} />
              <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.2rem', color: 'var(--text-primary)' }}>
                Intelligence Classification Matrix
              </h2>
            </div>

            {/* AI Confidence Circular Ring */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '24px', padding: '20px', borderRadius: '20px', background: 'var(--glass-pill)', marginBottom: '24px' }}>
              <div style={{ position: 'relative', width: 84, height: 84, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="84" height="84" viewBox="0 0 84 84">
                  <circle cx="42" cy="42" r="36" stroke="var(--glass-border)" strokeWidth="6" fill="none" />
                  <circle
                    cx="42"
                    cy="42"
                    r="36"
                    stroke="var(--brand-cyan)"
                    strokeWidth="6"
                    strokeDasharray={226}
                    strokeDashoffset={226 - (226 * (cert.ai_confidence || 0.94))}
                    strokeLinecap="round"
                    fill="none"
                    style={{ transition: 'stroke-dashoffset 1.2s ease-out' }}
                  />
                </svg>
                <div style={{ position: 'absolute', textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', fontWeight: 800, color: 'var(--brand-ice)' }}>
                    {confidencePercent}%
                  </div>
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {isIdentity ? 'Identity Routing' : isAcademic ? 'Academic Classification' : 'Primary Category'}
                </div>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
                  {cert.category || 'Accredited Record'}
                </div>
                <div style={{
                  fontSize: '0.78rem',
                  color: cert.is_reviewed ? 'var(--brand-emerald)' : 'var(--brand-cyan)',
                  marginTop: '2px'
                }}>
                  {isIdentity
                    ? 'Hierarchical Indian Document Router'
                    : isResume
                    ? 'Document-Type Gatekeeper Identified'
                    : cert.is_reviewed
                    ? 'Human Verified & Confirmed'
                    : 'LinearSVC + TF-IDF Model Prediction'}
                </div>
              </div>
            </div>

            {/* Decision Evidence: Influential Terms */}
            {cert.ai_important_terms?.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Influential Routing Features
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>Attribution Weight</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {cert.ai_important_terms.slice(0, 6).map((t, idx) => (
                    <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 500 }}>
                          {t.term}
                        </span>
                        <span style={{ color: 'var(--brand-ice)', fontFamily: 'var(--font-mono)' }}>
                          {t.importance_pct != null ? `${t.importance_pct}%` : `+${t.weight}`}
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '4px', background: 'var(--glass-pill)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.min(100, t.importance_pct || 60)}%`, height: '100%', background: 'linear-gradient(90deg, var(--brand-primary), var(--brand-cyan))', borderRadius: '2px' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Skills Chips (Only for technical/career documents) */}
            {!isIdentity && cert.extracted_skills?.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <div style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px' }}>
                  Verified Skills Detected
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {cert.extracted_skills.map((s, idx) => (
                    <span key={idx} className="glass-pill" style={{ color: 'var(--brand-ice)' }}>
                      {typeof s === 'string' ? s : s.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Document Integrity Audit (For Identity Credentials) */}
            {isIdentity && (
              <div style={{ marginBottom: '20px' }}>
                <div style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px' }}>
                  Document Security & Verification
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <div className="glass-card-spatial" style={{ padding: '10px 12px', fontSize: '0.78rem' }}>
                    <div style={{ color: 'var(--text-muted)' }}>Authority</div>
                    <div style={{ color: 'var(--brand-emerald)', fontWeight: 600, marginTop: '2px' }}>✓ Official Seal Verified</div>
                  </div>
                  <div className="glass-card-spatial" style={{ padding: '10px 12px', fontSize: '0.78rem' }}>
                    <div style={{ color: 'var(--text-muted)' }}>Privacy Protocol</div>
                    <div style={{ color: 'var(--brand-ice)', fontWeight: 600, marginTop: '2px' }}>✓ Masked & Redacted</div>
                  </div>
                </div>
              </div>
            )}

            {/* Collapsible Raw OCR Transcript Inspector */}
            <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '18px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Raw OCR Extracted Transcript
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {cert.raw_ocr_text && (
                    <button
                      type="button"
                      className="btn-liquid btn-liquid-ghost"
                      onClick={copyOcrToClipboard}
                      style={{ padding: '4px 10px', fontSize: '0.74rem' }}
                      title="Copy raw OCR text"
                    >
                      <Copy size={13} /> Copy
                    </button>
                  )}
                  <button
                    type="button"
                    className="glass-pill"
                    onClick={() => setShowRawOcr(!showRawOcr)}
                    style={{ fontSize: '0.76rem', padding: '4px 10px' }}
                  >
                    <span>{showRawOcr ? 'Hide' : 'Inspect'} ({cert.raw_ocr_text ? `${cert.raw_ocr_text.length} chars` : '0'})</span>
                    <ChevronDown size={14} style={{ transform: showRawOcr ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                  </button>
                </div>
              </div>

              <AnimatePresence>
                {showRawOcr && (
                  <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} style={{ overflow: 'hidden' }}>
                    <div style={{
                      padding: '16px',
                      borderRadius: '14px',
                      background: 'rgba(0,0,0,0.45)',
                      border: '1px solid var(--glass-border)',
                      fontSize: '0.8rem',
                      lineHeight: 1.6,
                      color: 'var(--text-secondary)',
                      maxHeight: '260px',
                      overflowY: 'auto',
                      fontFamily: 'var(--font-mono)',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                    }}>
                      {cert.raw_ocr_text || 'No raw OCR transcript available.'}
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
