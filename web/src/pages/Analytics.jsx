/**
 * CertiNexus AI — Spatial Portfolio Analytics & Evaluation Matrix
 * Liquid Glass Charts, Recharts Integration, and Academic Readiness Index
 */

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
  Tooltip, CartesianGrid
} from 'recharts'
import { Award, Compass, TrendingUp, ShieldCheck, Printer, Brain, Sparkles } from 'lucide-react'
import api from '../lib/api.js'

const CHART_PALETTE = [
  '#38bdf8', '#06b6d4', '#6366f1', '#818cf8',
  '#10b981', '#f59e0b', '#ec4899', '#a855f7',
]

export default function Analytics() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(),
    placeholderData: (prev) => prev,
  })

  if (isLoading) {
    return (
      <div className="single-screen-tab-wrapper" style={{ maxWidth: 1240, width: '100%', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 36, height: 36, borderRadius: '50%', border: '2px solid var(--brand-ice)', borderTopColor: 'transparent', animation: 'spin 0.8s linear infinite' }} />
      </div>
    )
  }

  const catData = Object.entries(analytics?.category_distribution || {}).map(([name, value]) => ({ name, value }))
  const skillData = Object.entries(analytics?.skills_distribution || {}).slice(0, 10).map(([name, value]) => ({ name, value }))
  const totalCerts = analytics?.total_certificates || 0
  const totalSkills = analytics?.total_skills || 0
  const readinessScore = analytics?.portfolio_completeness != null
    ? Math.round(analytics.portfolio_completeness)
    : Math.min(100, Math.round((totalCerts * 15) + Math.min(40, totalSkills * 2)))

  return (
    <div className="single-screen-tab-wrapper" style={{ maxWidth: 1240, width: '100%', margin: '0 auto', height: '100%', maxHeight: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Compact Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '10px', flexShrink: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
            <span className="status-beacon green" />
            <span style={{ fontSize: '0.74rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--brand-ice)' }}>
              Competency Evaluation Matrix
            </span>
          </div>
          <h1 className="spatial-hero-title" style={{ fontSize: '1.45rem', margin: 0 }}>
            Portfolio Analytics
          </h1>
        </div>

        <button onClick={() => window.print()} className="btn-liquid btn-liquid-ghost" style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
          <Printer size={14} />
          <span>Export Report</span>
        </button>
      </div>

      {/* Floating Metric Counters Strip */}
      <div className="stats-spatial-grid" style={{ marginBottom: '8px', gap: '8px', flexShrink: 0 }}>
        <div className="metric-spatial-card glass-specular-glow" style={{ padding: '8px 14px' }}>
          <div className="metric-header" style={{ marginBottom: '2px' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>Credentials</span>
            <Award size={15} style={{ color: 'var(--brand-ice)' }} />
          </div>
          <div className="metric-value-num" style={{ fontSize: '1.35rem', margin: 0 }}>{totalCerts}</div>
          <div className="metric-label-txt" style={{ fontSize: '0.7rem' }}>Accredited Certificates</div>
        </div>

        <div className="metric-spatial-card glass-specular-glow" style={{ padding: '8px 14px' }}>
          <div className="metric-header" style={{ marginBottom: '2px' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>Demonstrated Skills</span>
            <Sparkles size={15} style={{ color: 'var(--brand-primary-light)' }} />
          </div>
          <div className="metric-value-num" style={{ fontSize: '1.35rem', margin: 0 }}>{totalSkills}</div>
          <div className="metric-label-txt" style={{ fontSize: '0.7rem' }}>Extracted Competencies</div>
        </div>

        <div className="metric-spatial-card glass-specular-glow" style={{ padding: '8px 14px' }}>
          <div className="metric-header" style={{ marginBottom: '2px' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>Domains</span>
            <Compass size={15} style={{ color: 'var(--brand-cyan)' }} />
          </div>
          <div className="metric-value-num" style={{ fontSize: '1.35rem', margin: 0 }}>{analytics?.total_categories || 0}</div>
          <div className="metric-label-txt" style={{ fontSize: '0.7rem' }}>Achievement Verticals</div>
        </div>

        <div className="metric-spatial-card glass-specular-glow" style={{ padding: '8px 14px' }}>
          <div className="metric-header" style={{ marginBottom: '2px' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>Readiness Index</span>
            <TrendingUp size={15} style={{ color: 'var(--brand-emerald)' }} />
          </div>
          <div className="metric-value-num" style={{ fontSize: '1.35rem', margin: 0, color: 'var(--brand-emerald)' }}>{readinessScore}%</div>
          <div className="metric-label-txt" style={{ fontSize: '0.7rem' }}>AI Career Benchmark</div>
        </div>
      </div>

      {/* Main Single-Screen Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.35fr 1fr', gap: '10px', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        {/* Left Column: Visual Charts Split */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', minHeight: 0, height: '100%', overflow: 'hidden' }}>
          {/* Category Breakdown & Distribution Card */}
          <div className="glass-panel" style={{ padding: '12px 16px', flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', flexShrink: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                  Category Distribution
                </h2>
                <span className="glass-pill" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                  {catData.length} Active Domains
                </span>
              </div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)' }}>
                {totalCerts} Total Documents
              </span>
            </div>
            {catData.length > 0 ? (
              <div style={{ flex: 1, minHeight: 0, display: 'grid', gridTemplateColumns: '120px 1fr', gap: '12px', alignItems: 'center' }}>
                {/* Donut Chart with Centered Total */}
                <div style={{ width: 120, height: 120, position: 'relative', margin: '0 auto', flexShrink: 0 }}>
                  <ResponsiveContainer width={120} height={120}>
                    <PieChart>
                      <Pie data={catData} cx="50%" cy="50%" innerRadius={36} outerRadius={54} paddingAngle={4} dataKey="value" stroke="transparent" isAnimationActive={false}>
                        {catData.map((_, idx) => (
                          <Cell key={idx} fill={CHART_PALETTE[idx % CHART_PALETTE.length]} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ background: 'var(--glass-elevated)', borderColor: 'var(--glass-border-light)', borderRadius: 8, backdropFilter: 'blur(16px)', fontSize: '0.75rem' }} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
                    <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>{totalCerts}</div>
                    <div style={{ fontSize: '0.62rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginTop: '2px' }}>Docs</div>
                  </div>
                </div>

                {/* Right Breakdown List with Progress Bars */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto', maxHeight: '100%', paddingRight: '4px' }}>
                  {catData.map((item, idx) => {
                    const color = CHART_PALETTE[idx % CHART_PALETTE.length]
                    const pct = totalCerts > 0 ? Math.round((item.value / totalCerts) * 100) : 0
                    return (
                      <div key={item.name} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.76rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: 0 }}>
                            <span style={{ width: 7, height: 7, borderRadius: '50%', background: color, flexShrink: 0 }} />
                            <span style={{ color: 'var(--text-primary)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {item.name}
                            </span>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0, marginLeft: '6px' }}>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>{item.value}</span>
                            <span style={{ color: color, fontWeight: 600, fontSize: '0.72rem', minWidth: '32px', textAlign: 'right' }}>{pct}%</span>
                          </div>
                        </div>
                        <div style={{ width: '100%', height: '4px', background: 'var(--glass-pill)', borderRadius: '2px', overflow: 'hidden' }}>
                          <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '2px' }} />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>No certificate categories recorded yet</div>
            )}
          </div>

          {/* Skill Density Bar Chart */}
          <div className="glass-panel" style={{ padding: '12px 16px', flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px', flexShrink: 0 }}>
              <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                Top Skill Frequency
              </h2>
              <span className="glass-pill" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>Frequency</span>
            </div>
            {skillData.length > 0 ? (
              <div style={{ flex: 1, minHeight: 120, width: '100%' }}>
                <ResponsiveContainer width="100%" height={125}>
                  <BarChart data={skillData} layout="vertical" margin={{ left: 10, right: 10, top: 2, bottom: 2 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
                    <XAxis type="number" stroke="var(--text-muted)" fontSize={10} allowDecimals={false} domain={[0, 'dataMax + 1']} />
                    <YAxis type="category" dataKey="name" stroke="var(--text-muted)" fontSize={10} width={75} />
                    <Tooltip
                      contentStyle={{ background: 'var(--glass-elevated)', borderColor: 'var(--glass-border-light)', borderRadius: 10, backdropFilter: 'blur(16px)', fontSize: '0.8rem' }}
                      formatter={(val) => [`${val} occurrence${val === 1 ? '' : 's'}`, 'Frequency']}
                    />
                    <Bar dataKey="value" fill="#38bdf8" radius={[0, 4, 4, 0]} isAnimationActive={false} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>No skill data recorded yet</div>
            )}
          </div>
        </div>

        {/* Right Column: Student Evaluation & Readiness Assessment */}
        <div className="glass-panel" style={{ padding: '14px 18px', height: '100%', minHeight: 0, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexShrink: 0 }}>
            <ShieldCheck size={18} style={{ color: 'var(--brand-emerald)' }} />
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
              Readiness Assessment
            </h2>
          </div>

          <div className="glass-card-spatial" style={{ padding: '12px 14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--brand-ice)', fontSize: '0.82rem', fontWeight: 600, marginBottom: '4px' }}>
              <Award size={14} /> Domain Competency Profile
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.45, margin: 0 }}>
              {catData.length > 0
                ? `Primary experience is concentrated in ${catData.map((c) => c.name).join(', ')}. Demonstrated practical industry engagement through verified completion credentials.`
                : 'Upload certificates to generate your automated academic competency profile.'}
            </p>
          </div>

          <div className="glass-card-spatial" style={{ padding: '12px 14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--brand-emerald)', fontSize: '0.82rem', fontWeight: 600, marginBottom: '4px' }}>
              <TrendingUp size={14} /> Learning Velocity & Growth
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.45, margin: 0 }}>
              {totalSkills > 0
                ? `Acquired ${totalSkills} distinct technical and professional skills across verified achievement records. Demonstrates strong initiative in real-world application.`
                : 'Skills will automatically appear here once certificates are uploaded and processed by the OCR pipeline.'}
            </p>
          </div>

          <div className="glass-card-spatial" style={{ padding: '12px 14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--brand-primary-light)', fontSize: '0.82rem', fontWeight: 600, marginBottom: '4px' }}>
              <Brain size={14} /> Career & Role Recommendation
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.45, margin: 0 }}>
              Based on your verified skills in programming, databases, web technologies, and software systems, your profile strongly matches Software Developer & AI roles. Consult the AI Assistant tab for detailed role milestones.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
