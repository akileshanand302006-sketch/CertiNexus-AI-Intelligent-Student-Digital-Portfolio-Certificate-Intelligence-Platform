/**
 * CertiNexus AI — Certificate Upload (Drag & Drop with AI Processing Animation)
 */

import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Brain, Sparkles, CheckCircle2, AlertTriangle, Eye, Search, Shield } from 'lucide-react'
import api from '../lib/api.js'
import toast from 'react-hot-toast'

const processingSteps = [
  { icon: Upload, label: 'Uploading document', key: 'uploading' },
  { icon: FileText, label: 'Reading document (OCR)', key: 'ocr' },
  { icon: Search, label: 'Extracting information', key: 'extracting' },
  { icon: Brain, label: 'AI classification', key: 'classifying' },
  { icon: Sparkles, label: 'Detecting skills', key: 'skills' },
  { icon: Shield, label: 'Checking duplicates', key: 'duplicates' },
  { icon: CheckCircle2, label: 'Complete', key: 'complete' },
]

export default function CertificateUpload() {
  const [uploading, setUploading] = useState(false)
  const [currentStep, setCurrentStep] = useState(-1)
  const [result, setResult] = useState(null)
  const navigate = useNavigate()

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    const file = acceptedFiles[0]

    setUploading(true)
    setCurrentStep(0)
    setResult(null)

    // Simulate progressive steps (real processing is synchronous via API)
    const stepDelay = (ms) => new Promise(r => setTimeout(r, ms))

    try {
      setCurrentStep(0) // uploading
      await stepDelay(400)
      setCurrentStep(1) // OCR
      await stepDelay(300)
      setCurrentStep(2) // extracting

      // Actual API call
      const cert = await api.uploadCertificate(file)

      setCurrentStep(3) // classifying
      await stepDelay(400)
      setCurrentStep(4) // skills
      await stepDelay(300)
      setCurrentStep(5) // duplicates
      await stepDelay(200)
      setCurrentStep(6) // complete

      setResult(cert)
      toast.success('Certificate processed successfully!')
    } catch (err) {
      toast.error(err.message || 'Upload failed')
      setCurrentStep(-1)
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/webp': ['.webp'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled: uploading,
  })

  const reset = () => {
    setUploading(false)
    setCurrentStep(-1)
    setResult(null)
  }

  return (
    <div>
      <div className="page-header">
        <h1>Upload Certificate</h1>
        <p>Drop your certificate and let AI process it</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '24px', maxWidth: '1000px' }}>
        {/* Upload / Processing */}
        <div>
          {!uploading && !result && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div {...getRootProps()} className={`upload-zone ${isDragActive ? 'drag-active' : ''}`}>
                <input {...getInputProps()} />
                <Upload size={48} style={{ color: isDragActive ? 'var(--color-accent)' : 'var(--text-muted)', marginBottom: '16px' }} />
                <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '8px' }}>
                  {isDragActive ? 'Drop it here!' : 'Drop your certificate here'}
                </h3>
                <p style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '16px' }}>
                  or click to browse files
                </p>
                <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', flexWrap: 'wrap' }}>
                  {['PDF', 'PNG', 'JPG', 'JPEG', 'WebP'].map(ext => (
                    <span key={ext} style={{
                      padding: '4px 10px', borderRadius: 'var(--radius-full)',
                      background: 'var(--glass-bg)', border: '1px solid var(--glass-border)',
                      fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-tertiary)',
                      fontFamily: 'var(--font-mono)',
                    }}>{ext}</span>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* Processing Steps */}
          {uploading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="glass-card" style={{ padding: '32px' }}>
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '24px' }}>
                AI Processing Pipeline
              </h3>
              <div className="processing-steps">
                {processingSteps.map((step, i) => {
                  const status = i < currentStep ? 'completed' : i === currentStep ? 'active' : 'pending'
                  return (
                    <motion.div key={step.key}
                      className={`processing-step ${status}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: '8px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: status === 'active' ? 'rgba(99,102,241,0.15)' :
                          status === 'completed' ? 'rgba(16,185,129,0.15)' : 'var(--glass-bg)',
                      }}>
                        {status === 'completed' ? <CheckCircle2 size={16} /> :
                         status === 'active' ? (
                           <motion.div animate={{ rotate: 360 }}
                             transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                             <step.icon size={16} />
                           </motion.div>
                         ) : <step.icon size={16} />}
                      </div>
                      <span style={{ fontWeight: status === 'active' ? 600 : 400 }}>
                        {step.label}
                      </span>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}
        </div>

        {/* Result */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="glass-card" style={{ padding: '32px' }}>
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '20px' }}>
                AI Extraction Results
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Category */}
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px', display: 'block' }}>Predicted Category</label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className="category-badge" style={{ fontSize: '0.85rem', padding: '6px 14px' }}>
                      {result.category || 'Unknown'}
                    </span>
                    {result.ai_confidence != null && (
                      <span className={`confidence-badge confidence-${result.ai_confidence_level || 'medium'}`}>
                        {(result.ai_confidence * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                </div>

                {/* Fields */}
                {[
                  ['Title', result.title],
                  ['Organization', result.organization],
                  ['Event', result.event],
                  ['Date', result.issue_date],
                  ['Status', result.status],
                ].map(([label, value]) => value && (
                  <div key={label}>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '2px', display: 'block' }}>{label}</label>
                    <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{value}</div>
                  </div>
                ))}

                {/* Skills */}
                {result.extracted_skills?.length > 0 && (
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '6px', display: 'block' }}>Detected Skills</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {result.extracted_skills.map((skill, i) => (
                        <span key={i} style={{
                          padding: '4px 10px', borderRadius: 'var(--radius-full)',
                          background: 'rgba(168,85,247,0.12)', border: '1px solid rgba(168,85,247,0.2)',
                          fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-secondary-light)',
                        }}>{skill}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Important Terms */}
                {result.ai_important_terms?.length > 0 && (
                  <div>
                    <label style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '6px', display: 'block' }}>Influential Model Features</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {result.ai_important_terms.slice(0, 6).map((term, i) => (
                        <span key={i} style={{
                          padding: '3px 8px', borderRadius: 'var(--radius-sm)',
                          background: 'var(--glass-bg)', border: '1px solid var(--glass-border)',
                          fontSize: '0.7rem', fontFamily: 'var(--font-mono)',
                          color: 'var(--text-secondary)',
                        }}>{term.term}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
                  <button className="btn btn-primary btn-sm" onClick={() => navigate(`/certificates/${result.id}`)}>
                    <Eye size={14} /> View Details
                  </button>
                  <button className="btn btn-ghost btn-sm" onClick={reset}>
                    Upload Another
                  </button>
                </div>
              </div>

              {/* Low confidence warning */}
              {result.ai_confidence_level === 'low' && (
                <div style={{
                  marginTop: '16px', padding: '12px', borderRadius: 'var(--radius-md)',
                  background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)',
                  display: 'flex', alignItems: 'center', gap: '8px',
                  fontSize: '0.8rem', color: 'var(--color-warning-light)',
                }}>
                  <AlertTriangle size={16} />
                  Low confidence prediction. Please review and correct if needed.
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
