/**
 * CertiNexus AI — Analytics Dashboard
 */
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from 'recharts'
import api from '../lib/api.js'

const COLORS = ['#6366f1', '#a855f7', '#22d3ee', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6', '#14b8a6', '#f97316', '#06b6d4']

const chartTooltipStyle = {
  background: 'rgba(30,32,48,0.95)', border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '8px', color: '#f1f5f9', fontSize: '0.8rem',
}

export default function Analytics() {
  const { data: analytics, isLoading } = useQuery({ queryKey: ['analytics'], queryFn: () => api.getAnalytics() })

  const catData = Object.entries(analytics?.category_distribution || {}).map(([name, value]) => ({ name, value }))
  const skillData = Object.entries(analytics?.skills_distribution || {}).slice(0, 12).map(([name, value]) => ({ name, value }))
  const monthlyData = Object.entries(analytics?.monthly_activity || {}).map(([name, value]) => ({ name, value }))

  return (
    <div>
      <div className="page-header">
        <h1>Analytics</h1>
        <p>Insights from your certificate portfolio</p>
      </div>

      {/* Stats */}
      <div className="grid-stats" style={{ marginBottom: '24px' }}>
        {[
          { label: 'Total Certificates', value: analytics?.total_certificates || 0 },
          { label: 'Skills Detected', value: analytics?.total_skills || 0 },
          { label: 'Categories', value: analytics?.total_categories || 0 },
          { label: 'Completeness', value: `${analytics?.portfolio_completeness || 0}%` },
        ].map((stat, i) => (
          <motion.div key={i} className="stat-card" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        <motion.div className="glass-card" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', fontSize: '0.95rem' }}>Category Distribution</h3>
          {catData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={catData} cx="50%" cy="50%" innerRadius={55} outerRadius={95} paddingAngle={3} dataKey="value" strokeWidth={0}>
                  {catData.map((_, idx) => <Cell key={idx} fill={COLORS[idx % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={chartTooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          ) : <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No data</div>}
        </motion.div>

        <motion.div className="glass-card" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', fontSize: '0.95rem' }}>Skills Distribution</h3>
          {skillData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={skillData} layout="vertical" margin={{ left: 80 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} width={80} />
                <Tooltip contentStyle={chartTooltipStyle} />
                <Bar dataKey="value" fill="#a855f7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No data</div>}
        </motion.div>
      </div>

      {/* Monthly Activity */}
      {monthlyData.length > 0 && (
        <motion.div className="glass-card" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '16px', fontSize: '0.95rem' }}>Monthly Activity</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}
    </div>
  )
}
