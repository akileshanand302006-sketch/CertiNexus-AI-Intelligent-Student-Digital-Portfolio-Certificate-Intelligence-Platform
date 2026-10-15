/**
 * CertiNexus AI — Ultra-Premium Spatial AI Dashboard
 * Liquid Glass Metrics, Real MongoDB Data, and Animated Intelligence Counters
 */

import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  Award, Sparkles, FolderOpen, TrendingUp, Upload,
  ArrowRight, ShieldCheck, Zap, ArrowUpRight, CheckCircle2, ChevronRight
} from 'lucide-react'
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts'
import api from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'

// Native smooth ease-out counter animation (Zero external dependency)
function animateCounter(el, target, duration = 1400) {
  if (!el) return
  const endVal = Number(target) || 0
  const startTime = performance.now()
  const step = (now) => {
    const progress = Math.min((now - startTime) / duration, 1)
    const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
    el.innerHTML = Math.round(endVal * ease)
    if (progress < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

const CHART_PALETTE = [
  '#38bdf8', '#06b6d4', '#6366f1', '#818cf8',
  '#10b981', '#f59e0b', '#ec4899', '#a855f7',
]

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(),
    placeholderData: (prev) => prev,
  })

  // Refs for number counting
  const certsNumRef = useRef(null)
  const skillsNumRef = useRef(null)
  const catsNumRef = useRef(null)
  const compNumRef = useRef(null)

  useEffect(() => {
    if (!isLoading && analytics) {
      animateCounter(certsNumRef.current, analytics.total_certificates || 0, 1400)
      animateCounter(skillsNumRef.current, analytics.total_skills || 0, 1600)
      animateCounter(catsNumRef.current, analytics.total_categories || 0, 1500)
      animateCounter(compNumRef.current, analytics.portfolio_completeness || 0, 1800)
    }
  }, [isLoading, analytics])

  const catData = Object.entries(analytics?.category_distribution || {}).map(([name, value]) => ({
    name,
    value,
  }))

  const firstName = (user?.full_name || user?.username || 'Student').split(' ')[0]

  return (
    <div className="single-screen-tab-wrapper" style={{ maxWidth: 1240, width: '100%', margin: '0 auto' }}>
      {/* --- HERO GLASS PANEL (Compact Spatial Island) --- */}
      <div
        className="glass-panel glass-specular-glow"
        style={{
          padding: '12px 20px',
          marginBottom: '10px',
          borderRadius: '18px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          flexShrink: 0,
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
            <span className="status-beacon green" />
            <span style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--brand-ice)' }}>
              Intelligent Credential Space
            </span>
          </div>

          <h1 className="spatial-hero-title" style={{ fontSize: '1.35rem', margin: 0 }}>
            Welcome back, {firstName}
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => navigate('/upload')}
            className="btn-liquid btn-liquid-primary"
            style={{ padding: '8px 16px', fontSize: '0.84rem' }}
          >
            <Upload size={15} />
            <span>Scan Certificate</span>
          </button>
          <button
            onClick={() => navigate('/portfolio')}
            className="btn-liquid btn-liquid-ghost"
            style={{ padding: '8px 16px', fontSize: '0.84rem' }}
          >
            <Sparkles size={15} />
            <span>Digital Portfolio</span>
          </button>
        </div>
      </div>

      {/* --- FLOATING METRICS GRID (Instant Render) --- */}
      <div className="stats-spatial-grid">
        {/* Metric 1: Certificates */}
        <div className="metric-spatial-card glass-specular-glow">
          <div className="metric-header">
            <div className="metric-icon-box" style={{ background: 'rgba(56, 189, 248, 0.1)', borderColor: 'rgba(56, 189, 248, 0.25)' }}>
              <Award size={20} style={{ color: 'var(--brand-ice)' }} />
            </div>
            <span className="glass-pill" style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
              Verified
            </span>
          </div>
          <div className="metric-value-num">
            <span ref={certsNumRef}>{analytics?.total_certificates || 0}</span>
          </div>
          <div className="metric-label-txt">Certificates Processed</div>
        </div>

        {/* Metric 2: Skills Detected */}
        <div className="metric-spatial-card glass-specular-glow">
          <div className="metric-header">
            <div className="metric-icon-box" style={{ background: 'rgba(99, 102, 241, 0.1)', borderColor: 'rgba(99, 102, 241, 0.25)' }}>
              <Sparkles size={20} style={{ color: 'var(--brand-primary-light)' }} />
            </div>
            <span className="glass-pill" style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
              NLP Extracted
            </span>
          </div>
          <div className="metric-value-num">
            <span ref={skillsNumRef}>{analytics?.total_skills || 0}</span>
          </div>
          <div className="metric-label-txt">Skills Normalized</div>
        </div>

        {/* Metric 3: Categories */}
        <div className="metric-spatial-card glass-specular-glow">
          <div className="metric-header">
            <div className="metric-icon-box" style={{ background: 'rgba(6, 182, 212, 0.1)', borderColor: 'rgba(6, 182, 212, 0.25)' }}>
              <FolderOpen size={20} style={{ color: 'var(--brand-cyan)' }} />
            </div>
            <span className="glass-pill" style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
              11 Classes
            </span>
          </div>
          <div className="metric-value-num">
            <span ref={catsNumRef}>{analytics?.total_categories || 0}</span>
          </div>
          <div className="metric-label-txt">Achievement Domains</div>
        </div>

        {/* Metric 4: Portfolio Completeness */}
        <div className="metric-spatial-card glass-specular-glow">
          <div className="metric-header">
            <div className="metric-icon-box" style={{ background: 'rgba(16, 185, 129, 0.1)', borderColor: 'rgba(16, 185, 129, 0.25)' }}>
              <TrendingUp size={20} style={{ color: 'var(--brand-emerald)' }} />
            </div>
            <span className="glass-pill" style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
              Progress
            </span>
          </div>
          <div className="metric-value-num" style={{ display: 'flex', alignItems: 'baseline' }}>
            <span ref={compNumRef}>{analytics?.portfolio_completeness || 0}</span>
            <span style={{ fontSize: '1.4rem', color: 'var(--brand-emerald)', marginLeft: 2 }}>%</span>
          </div>
          <div className="metric-label-txt">Portfolio Completeness</div>
        </div>
      </div>

      {/* --- MAIN DASHBOARD CONTENT GRID --- */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.35fr 1fr', gap: '12px', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        {/* Category Radial Constellation */}
        <div
          className="glass-panel glass-specular-glow"
          style={{ padding: '14px 18px', display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', flexShrink: 0 }}>
            <div>
              <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                Category Distribution
              </h2>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', margin: 0 }}>
                Accredited distribution of achievements
              </p>
            </div>
            <span className="glass-pill" style={{ fontSize: '0.72rem', padding: '2px 8px' }}>
              Real-time
            </span>
          </div>

          {catData.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: '150px 1fr', alignItems: 'center', gap: '14px', flex: 1, minHeight: 0 }}>
              <div style={{ height: 145, width: 150, minHeight: 145, position: 'relative', margin: '0 auto' }}>
                <ResponsiveContainer width={150} height={145}>
                  <PieChart>
                    <Pie
                      data={catData}
                      cx="50%"
                      cy="50%"
                      innerRadius={42}
                      outerRadius={65}
                      paddingAngle={3}
                      dataKey="value"
                      stroke="transparent"
                      isAnimationActive={false}
                    >
                      {catData.map((_, idx) => (
                        <Cell key={idx} fill={CHART_PALETTE[idx % CHART_PALETTE.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: 'var(--glass-elevated)',
                        borderColor: 'var(--glass-border-light)',
                        borderRadius: '12px',
                        backdropFilter: 'blur(16px)',
                        color: 'var(--text-primary)',
                        fontSize: '0.78rem',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
                    {catData.reduce((acc, curr) => acc + curr.value, 0)}
                  </div>
                  <div style={{ fontSize: '0.62rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginTop: '2px' }}>
                    Records
                  </div>
                </div>
              </div>

              {/* Category Nodes with Percentage & Visual Progress */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '7px', overflowY: 'auto', maxHeight: '100%', paddingRight: '4px' }}>
                {catData.map((item, idx) => {
                  const total = catData.reduce((acc, curr) => acc + curr.value, 0) || 1
                  const pct = Math.round((item.value / total) * 100)
                  const color = CHART_PALETTE[idx % CHART_PALETTE.length]
                  return (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '3px',
                        padding: '6px 10px',
                        borderRadius: '10px',
                        background: 'var(--glass-pill)',
                        border: '1px solid var(--glass-border)',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-primary)', minWidth: 0 }}>
                          <span
                            style={{
                              width: 8,
                              height: 8,
                              borderRadius: '50%',
                              background: color,
                              flexShrink: 0,
                            }}
                          />
                          <span style={{ fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {item.name}
                          </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                          <span style={{ fontSize: '0.74rem', color: 'var(--text-tertiary)' }}>
                            {item.value} doc{item.value !== 1 ? 's' : ''}
                          </span>
                          <span style={{ fontSize: '0.74rem', fontWeight: 700, color: color, minWidth: '32px', textAlign: 'right' }}>
                            {pct}%
                          </span>
                        </div>
                      </div>
                      <div style={{ width: '100%', height: '4px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '2px' }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '48px 20px', color: 'var(--text-tertiary)' }}>
              <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'var(--glass-pill)', margin: '0 auto 12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <FolderOpen size={22} style={{ color: 'var(--brand-ice)' }} />
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>No category data yet</p>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Scan your first certificate to populate the intelligence graph</p>
            </div>
          )}
        </div>

        {/* Floating Quick Action Glass Objects */}
        <div
          className="glass-panel glass-specular-glow"
          style={{ padding: '14px 18px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: 0, overflow: 'hidden' }}
        >
          <div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
              Quick Navigation
            </h2>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>
              Direct access to intelligent modules
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={() => navigate('/upload')}
                className="glass-pill"
                style={{ width: '100%', justifyContent: 'space-between', padding: '8px 12px', borderRadius: '12px' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: 28, height: 28, borderRadius: '8px', background: 'rgba(56, 189, 248, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Upload size={14} style={{ color: 'var(--brand-ice)' }} />
                  </div>
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>Scan Certificate</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Upload & Auto-Process</div>
                  </div>
                </div>
                <ArrowRight size={14} />
              </button>

              <button
                onClick={() => navigate('/portfolio')}
                className="glass-pill"
                style={{ width: '100%', justifyContent: 'space-between', padding: '8px 12px', borderRadius: '12px' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: 28, height: 28, borderRadius: '8px', background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Award size={14} style={{ color: 'var(--brand-primary-light)' }} />
                  </div>
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>Digital Portfolio</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Verified certificates & profile</div>
                  </div>
                </div>
                <ArrowRight size={14} />
              </button>

              <button
                onClick={() => navigate('/skills')}
                className="glass-pill"
                style={{ width: '100%', justifyContent: 'space-between', padding: '8px 12px', borderRadius: '12px' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: 28, height: 28, borderRadius: '8px', background: 'rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Sparkles size={14} style={{ color: 'var(--brand-cyan)' }} />
                  </div>
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>Skills Constellation</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>NLP extracted competencies</div>
                  </div>
                </div>
                <ArrowRight size={14} />
              </button>

              <button
                onClick={() => navigate('/assistant')}
                className="glass-pill"
                style={{ width: '100%', justifyContent: 'space-between', padding: '8px 12px', borderRadius: '12px' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: 28, height: 28, borderRadius: '8px', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Sparkles size={14} style={{ color: 'var(--brand-emerald)' }} />
                  </div>
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>AI Assistant</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Ask certificate & career advice</div>
                  </div>
                </div>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>

          {/* Bottom helper card */}
          <div
            style={{
              padding: '10px 14px',
              borderRadius: '12px',
              background: 'rgba(56, 189, 248, 0.06)',
              border: '1px solid rgba(56, 189, 248, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: '8px',
            }}
          >
            <div>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--brand-ice)' }}>Ask AI for Job Advice</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Developer vs AI vs Testing evaluation</div>
            </div>
            <button
              onClick={() => navigate('/assistant')}
              className="btn-liquid btn-liquid-cyan"
              style={{ padding: '5px 12px', fontSize: '0.75rem', borderRadius: '8px' }}
            >
              Open
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
