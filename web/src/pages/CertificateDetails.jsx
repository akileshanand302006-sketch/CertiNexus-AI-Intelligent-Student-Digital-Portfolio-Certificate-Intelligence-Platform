/**
 * CertiNexus AI — Certificate Details
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Edit3, Trash2, CheckCircle, Brain } from 'lucide-react'
import { useState } from 'react'
import api from '../lib/api.js'
import toast from 'react-hot-toast'

export default function CertificateDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [editData, setEditData] = useState({})

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
      toast.success('Certificate updated')
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
      <div className="skeleton" style={{ height: '32px', width: '200px', marginBottom: '24px' }} />
      <div className="glass-card"><div className="skeleton" style={{ height: '300px' }} /></div>
    </div>
  )

  if (!cert) return <div>Certificate not found</div>

  const startEdit = () => {
    setEditData({ title: cert.title, organization: cert.organization, category: cert.category, issue_date: cert.issue_date })
    setEditing(true)
  }

  return (
    <div>
      <button className="btn btn-ghost btn-sm" onClick={() => navigate('/certificates')} style={{ marginBottom: '20px' }}>
        <ArrowLeft size={16} /> Back
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Left — Details */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.3rem' }}>Certificate Details</h2>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-ghost btn-sm" onClick={startEdit}><Edit3 size={14} /> Edit</button>
              <button className="btn btn-ghost btn-sm" onClick={() => { if(confirm('Delete?')) deleteMutation.mutate() }}
                style={{ color: 'var(--color-error)' }}>
                <Trash2 size={14} />
              </button>
            </div>
          </div>

          {editing ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {['title', 'organization', 'category', 'issue_date'].map(field => (
                <div key={field}>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block', textTransform: 'capitalize' }}>{field.replace('_', ' ')}</label>
                  <input className="glass-input" value={editData[field] || ''} onChange={e => setEditData(d => ({ ...d, [field]: e.target.value }))} />
                </div>
              ))}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-primary btn-sm" onClick={() => updateMutation.mutate(editData)}>Save</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setEditing(false)}>Cancel</button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {[
                ['Title', cert.title], ['Organization', cert.organization],
                ['Event', cert.event], ['Date', cert.issue_date],
                ['Certificate ID', cert.certificate_id_extracted],
                ['File', cert.original_filename], ['Status', cert.status],
              ].map(([label, value]) => value && (
                <div key={label}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '2px' }}>{label}</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{value}</div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Right — AI Analysis */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card" style={{ padding: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.3rem', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Brain size={20} style={{ color: 'var(--color-primary)' }} /> AI Analysis
          </h2>

          {/* Prediction */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '6px' }}>Predicted Category</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="category-badge" style={{ fontSize: '0.9rem', padding: '6px 16px' }}>{cert.category}</span>
              {cert.ai_confidence != null && (
                <span className={`confidence-badge confidence-${cert.ai_confidence_level}`}>
                  {(cert.ai_confidence * 100).toFixed(1)}%
                </span>
              )}
            </div>
            {cert.is_correction && (
              <div style={{ fontSize: '0.75rem', color: 'var(--color-warning)', marginTop: '6px' }}>
                User corrected from: {cert.ai_category}
              </div>
            )}
          </div>

          {/* Model info */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>Model Version</div>
            <div style={{ fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>{cert.model_version || 'N/A'}</div>
          </div>

          {cert.processing_time_ms && (
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>Processing Time</div>
              <div style={{ fontSize: '0.85rem' }}>{cert.processing_time_ms.toFixed(0)}ms</div>
            </div>
          )}

          {/* Skills */}
          {cert.extracted_skills?.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '8px' }}>Detected Skills</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {cert.extracted_skills.map((s, i) => (
                  <span key={i} style={{
                    padding: '4px 10px', borderRadius: 'var(--radius-full)',
                    background: 'rgba(168,85,247,0.12)', border: '1px solid rgba(168,85,247,0.2)',
                    fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-secondary-light)',
                  }}>{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Important Terms */}
          {cert.ai_important_terms?.length > 0 && (
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '8px' }}>Influential Model Features</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {cert.ai_important_terms.slice(0, 8).map((t, i) => (
                  <span key={i} style={{
                    padding: '3px 8px', borderRadius: 'var(--radius-sm)',
                    background: 'var(--glass-bg)', border: '1px solid var(--glass-border)',
                    fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)',
                  }}>{t.term}</span>
                ))}
              </div>
            </div>
          )}

          {/* OCR Text */}
          {cert.raw_ocr_text && (
            <div style={{ marginTop: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '6px' }}>OCR Extracted Text</div>
              <div style={{
                padding: '12px', borderRadius: 'var(--radius-md)',
                background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)',
                fontSize: '0.8rem', lineHeight: 1.6, color: 'var(--text-secondary)',
                maxHeight: '200px', overflowY: 'auto', fontFamily: 'var(--font-mono)',
              }}>{cert.raw_ocr_text}</div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
