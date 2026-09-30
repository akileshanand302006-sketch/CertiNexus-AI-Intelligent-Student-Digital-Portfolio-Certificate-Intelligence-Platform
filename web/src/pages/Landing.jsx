/**
 * CertiNexus AI — Landing Page
 * 
 * Premium landing with aurora background and feature showcase.
 * Three.js hero deferred for performance (uses CSS 3D effects instead).
 */

import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Award, Brain, Sparkles, Shield, Zap, Globe, ArrowRight } from 'lucide-react'

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] }
  })
}

const features = [
  { icon: Brain, title: 'AI Classification', desc: 'ML models automatically categorize your certificates with confidence scores', color: '#6366f1' },
  { icon: Sparkles, title: 'Skill Extraction', desc: 'NLP-powered skill detection and normalization from document text', color: '#a855f7' },
  { icon: Award, title: 'Digital Portfolio', desc: 'Auto-generated professional portfolio from your achievements', color: '#22d3ee' },
  { icon: Shield, title: 'Confidence Aware', desc: 'Low-confidence predictions routed to manual review automatically', color: '#10b981' },
  { icon: Zap, title: 'OCR Pipeline', desc: 'Extract text from PDFs and images with intelligent preprocessing', color: '#f59e0b' },
  { icon: Globe, title: 'Public Portfolio', desc: 'Share your achievements with a premium shareable portfolio page', color: '#ef4444' },
]

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div style={{ minHeight: '100vh', position: 'relative', overflow: 'hidden' }}>
      {/* Aurora Background */}
      <div className="aurora-bg">
        <div className="aurora-blob aurora-blob-1" />
        <div className="aurora-blob aurora-blob-2" />
        <div className="aurora-blob aurora-blob-3" />
      </div>

      {/* Nav */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        padding: '16px 32px',
        background: 'rgba(10, 11, 15, 0.7)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--glass-border)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: 32, height: 32, borderRadius: '8px',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 800, color: 'white', fontFamily: 'var(--font-display)',
            fontSize: '0.9rem',
          }}>C</div>
          <span style={{
            fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem'
          }}>CertiNexus AI</span>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/login')}>Sign In</button>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/register')}>Get Started</button>
        </div>
      </nav>

      {/* Hero */}
      <section style={{
        paddingTop: '160px', paddingBottom: '100px',
        textAlign: 'center', maxWidth: '800px', margin: '0 auto',
        padding: '160px 24px 100px',
      }}>
        <motion.div
          variants={fadeUp} initial="hidden" animate="visible" custom={0}
          style={{
            display: 'inline-block', padding: '6px 16px', borderRadius: 'var(--radius-full)',
            background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.2)',
            fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-primary-light)',
            marginBottom: '24px',
          }}>
          Powered by Machine Learning
        </motion.div>

        <motion.h1
          variants={fadeUp} initial="hidden" animate="visible" custom={1}
          style={{
            fontFamily: 'var(--font-display)', fontSize: 'clamp(2.5rem, 5vw, 4rem)',
            fontWeight: 800, lineHeight: 1.1, marginBottom: '24px',
            background: 'linear-gradient(135deg, #f1f5f9 30%, #6366f1 60%, #22d3ee 90%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}>
          Your Achievements.<br />Intelligently Organized.
        </motion.h1>

        <motion.p
          variants={fadeUp} initial="hidden" animate="visible" custom={2}
          style={{
            fontSize: '1.15rem', color: 'var(--text-secondary)',
            lineHeight: 1.7, marginBottom: '40px', maxWidth: '600px', margin: '0 auto 40px',
          }}>
          An intelligent document classification system that transforms your certificates
          into a structured digital portfolio using OCR, NLP, and machine learning.
        </motion.p>

        <motion.div
          variants={fadeUp} initial="hidden" animate="visible" custom={3}
          style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/register')}
            style={{ fontSize: '1rem' }}>
            Start Building Your Portfolio <ArrowRight size={18} />
          </button>
          <button className="btn btn-ghost btn-lg" onClick={() => navigate('/login')}
            style={{ fontSize: '1rem' }}>
            Sign In
          </button>
        </motion.div>

        {/* Floating glass cards */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          style={{
            marginTop: '80px',
            display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '16px', maxWidth: '600px', margin: '80px auto 0',
          }}>
          {[
            { label: 'Category', value: 'Hackathon', confidence: '94%' },
            { label: 'Skills', value: 'Python, ML', confidence: 'Detected' },
            { label: 'Status', value: 'Classified', confidence: 'High' },
          ].map((item, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 + i * 0.15 }}
              className="glass-card" style={{ padding: '16px', textAlign: 'left' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>
                {item.label}
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '4px' }}>
                {item.value}
              </div>
              <div className={`confidence-badge confidence-high`} style={{ fontSize: '0.65rem' }}>
                {item.confidence}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Features */}
      <section style={{
        padding: '80px 24px', maxWidth: '1200px', margin: '0 auto',
      }}>
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          style={{ textAlign: 'center', marginBottom: '60px' }}>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700,
            marginBottom: '12px',
          }}>
            Intelligent Certificate Processing
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto' }}>
            From unstructured documents to structured portfolio data, powered by ML.
          </p>
        </motion.div>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '20px',
        }}>
          {features.map((feat, i) => (
            <motion.div key={i}
              className="glass-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}>
              <div style={{
                width: 44, height: 44, borderRadius: '12px',
                background: `${feat.color}18`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: '16px',
              }}>
                <feat.icon size={22} style={{ color: feat.color }} />
              </div>
              <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '8px' }}>
                {feat.title}
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                {feat.desc}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '80px 24px 120px', textAlign: 'center' }}>
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          style={{
            maxWidth: '700px', margin: '0 auto', padding: '48px',
            background: 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(168,85,247,0.06))',
          }}>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontSize: '1.75rem', fontWeight: 700,
            marginBottom: '12px',
          }}>
            Ready to build your intelligent portfolio?
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '28px' }}>
            Upload your certificates and let AI organize your achievements.
          </p>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/register')}>
            Get Started Free <ArrowRight size={18} />
          </button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '24px', textAlign: 'center',
        borderTop: '1px solid var(--glass-border)',
        color: 'var(--text-muted)', fontSize: '0.8rem',
      }}>
        CertiNexus AI — 20MSSL12 Machine Learning Lab Project
      </footer>
    </div>
  )
}
