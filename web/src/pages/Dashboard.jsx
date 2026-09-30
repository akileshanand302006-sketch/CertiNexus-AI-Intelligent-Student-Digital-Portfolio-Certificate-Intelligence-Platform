/**
 * CertiNexus AI — Dashboard (Bento Grid)
 */

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Award, Sparkles, FolderOpen, TrendingUp, Upload, ArrowRight } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import api from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'

const CHART_COLORS = ['#6366f1', '#a855f7', '#22d3ee', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6', '#14b8a6', '#f97316', '#06b6d4']

const fadeUp = (i) => ({
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.5 } }
})

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.getAnalytics(),
  })

  const stats = [
    { icon: Award, label: 'Certificates', value: analytics?.total_certificates || 0, color: '#6366f1' },
    { icon: Sparkles, label: 'Skills Detected', value: analytics?.total_skills || 0, color: '#a855f7' },
    { icon: FolderOpen, label: 'Categories', value: analytics?.total_categories || 0, color: '#22d3ee' },
    { icon: TrendingUp, label: 'Completeness', value: `${analytics?.portfolio_completeness || 0}%`, color: '#10b981' },
  ]

  const catData = Object.entries(analytics?.category_distribution || {}).map(([name, value]) => ({ name, value }))

  return (
    <div>
      <div className="page-header">
        <h1>Welcome back, {user?.full_name || user?.username || 'Student'}</h1>
        <p>Your intelligent portfolio at a glance</p>
      </div>

      {/* Stats Grid */}
      <div className="bento-grid" style={{ marginBottom: '24px' }}>
        {stats.map((stat, i) => (
          <motion.div key={i} variants={fadeUp(i)} initial="hidden" animate="visible" className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{
                width: 40, height: 40, borderRadius: '10px', background: `${stat.color}18`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <stat.icon size={20} style={{ color: stat.color }} />
              </div>
            </div>
            <div className="stat-value">{isLoading ? '—' : stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </motion.div>
        ))}

        {/* Category Chart */}
        <motion.div variants={fadeUp(4)} initial="hidden" animate="visible" className="glass-card">
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', fontSize: '0.95rem' }}>
            Category Distribution
          </h3>
          {catData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={catData} cx="50%" cy="50%" innerRadius={50} outerRadius={85}
                  paddingAngle={3} dataKey="value" strokeWidth={0}>
                  {catData.map((_, idx) => (
                    <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{
                  background: 'rgba(30,32,48,0.95)', border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px', color: '#f1f5f9',
                }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              No certificates yet
            </div>
          )}
          {catData.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
              {catData.map((item, idx) => (
                <div key={idx} style={{
                  fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '4px',
                  color: 'var(--text-secondary)',
                }}>
                  <span style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: CHART_COLORS[idx % CHART_COLORS.length],
                  }} />
                  {item.name}
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Quick Actions */}
        <motion.div variants={fadeUp(5)} initial="hidden" animate="visible" className="glass-card">
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', fontSize: '0.95rem' }}>
            Quick Actions
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button className="btn btn-primary" onClick={() => navigate('/upload')}
              style={{ width: '100%', justifyContent: 'flex-start' }}>
              <Upload size={16} /> Upload Certificate
            </button>
            <button className="btn btn-ghost" onClick={() => navigate('/certificates')}
              style={{ width: '100%', justifyContent: 'flex-start' }}>
              <Award size={16} /> View Certificates
            </button>
            <button className="btn btn-ghost" onClick={() => navigate('/analytics')}
              style={{ width: '100%', justifyContent: 'flex-start' }}>
              <TrendingUp size={16} /> View Analytics
            </button>
            <button className="btn btn-ghost" onClick={() => navigate('/research')}
              style={{ width: '100%', justifyContent: 'flex-start' }}>
              <Sparkles size={16} /> ML Research
            </button>
          </div>
        </motion.div>
      </div>

      {/* Recent Certificates */}
      {analytics?.recent_certificates?.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600 }}>Recent Certificates</h3>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/certificates')}>
              View All <ArrowRight size={14} />
            </button>
          </div>
          <div className="grid-cards">
            {analytics.recent_certificates.map((cert, i) => (
              <motion.div key={cert.id} className="glass-card"
                initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 + i * 0.1 }}
                onClick={() => navigate(`/certificates/${cert.id}`)}
                style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span className="category-badge">{cert.category || 'Uncategorized'}</span>
                  {cert.ai_confidence != null && (
                    <span className={`confidence-badge confidence-${cert.ai_confidence_level || 'medium'}`}>
                      {(cert.ai_confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <h4 style={{ fontWeight: 600, marginBottom: '4px', fontSize: '0.95rem' }}>
                  {cert.title || cert.original_filename || 'Untitled'}
                </h4>
                <p style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>
                  {cert.organization || 'Unknown Organization'}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {!isLoading && (!analytics || analytics.total_certificates === 0) && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="glass-card"
          style={{ textAlign: 'center', padding: '64px 32px', marginTop: '24px' }}>
          <Award size={48} style={{ color: 'var(--color-primary)', marginBottom: '16px' }} />
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '8px' }}>
            Your achievement story starts here
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', maxWidth: '400px', margin: '0 auto 24px' }}>
            Upload your first certificate and let AI organize your achievements into a smart digital portfolio.
          </p>
          <button className="btn btn-primary" onClick={() => navigate('/upload')}>
            <Upload size={18} /> Upload First Certificate
          </button>
        </motion.div>
      )}
    </div>
  )
}
