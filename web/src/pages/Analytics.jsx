/**
 * CertiNexus AI — Analytics & Academic Portfolio Evaluation
 */
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer,
  Tooltip, CartesianGrid
} from 'recharts'
import { Award, Compass, TrendingUp, CheckCircle2, ShieldCheck, Printer } from 'lucide-react'
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

  // Calculate student evaluation metrics
  const totalCerts = analytics?.total_certificates || 0
  const totalSkills = analytics?.total_skills || 0
  const readinessScore = Math.min(100, Math.round((totalCerts * 25) + (totalSkills * 12)))

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1>Portfolio Analytics & Evaluation</h1>
          <p>Comprehensive academic verification and competency assessment</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>
          <Printer size={15} /> Print Evaluation Report
        </button>
      </div>

      {/* Stats */}
      <div className="grid-stats" style={{ marginBottom: '24px' }}>
        {[
          { label: 'Total Verified Certificates', value: totalCerts },
          { label: 'Demonstrated Skills', value: totalSkills },
          { label: 'Achievement Categories', value: analytics?.total_categories || 0 },
          { label: 'Career Readiness Index', value: `${readinessScore}%` },
        ].map((stat, i) => (
          <motion.div key={i} className="stat-card" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Academic Evaluation Summary Card */}
      <motion.div
        className="glass-card"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <ShieldCheck size={20} style={{ color: 'var(--color-success)' }} />
          <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.15rem', margin: 0 }}>
            Student Evaluation & Readiness Assessment
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          <div style={{
            padding: '16px', borderRadius: 'var(--radius-md)',
            background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-primary-light)', marginBottom: '8px' }}>
              <Award size={16} /> Domain Competency Profile
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              {catData.length > 0
                ? `Primary experience is concentrated in ${catData.map(c => c.name).join(', ')}. Demonstrated practical industry engagement through verified completion credentials.`
                : 'Upload certificates to generate your automated academic competency profile.'}
            </p>
          </div>

          <div style={{
            padding: '16px', borderRadius: 'var(--radius-md)',
            background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-success)', marginBottom: '8px' }}>
              <TrendingUp size={16} /> Learning Velocity & Growth
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              {totalSkills > 0
                ? `Acquired ${totalSkills} distinct technical and professional skills across verified achievement records. Demonstrates strong initiative in real-world application.`
                : 'Skills will automatically appear here as certificates are parsed by the AI extractor.'}
            </p>
          </div>

          <div style={{
            padding: '16px', borderRadius: 'var(--radius-md)',
            background: 'rgba(168,85,247,0.08)', border: '1px solid rgba(168,85,247,0.2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-secondary-light)', marginBottom: '8px' }}>
              <Compass size={16} /> Recommended Next Milestones
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
              Expand portfolio breadth by participating in a Hackathon or technical workshop to balance internship industry experience with competitive problem-solving.
            </p>
          </div>
        </div>
      </motion.div>

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

