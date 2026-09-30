/**
 * CertiNexus AI — Skills Page
 */
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import api from '../lib/api.js'

export default function Skills() {
  const { data: analytics } = useQuery({ queryKey: ['analytics'], queryFn: () => api.getAnalytics() })
  const skills = Object.entries(analytics?.skills_distribution || {})

  return (
    <div>
      <div className="page-header">
        <h1>Skills Detected</h1>
        <p>Skills automatically extracted from your certificates by AI</p>
      </div>
      {skills.length > 0 ? (
        <div className="grid-cards">
          {skills.map(([name, count], i) => (
            <motion.div key={name} className="glass-card" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: 40, height: 40, borderRadius: '10px', background: 'rgba(168,85,247,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Sparkles size={18} style={{ color: 'var(--color-secondary)' }} />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{name}</div>
                  <div style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>{count} certificate{count !== 1 ? 's' : ''}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="glass-card" style={{ textAlign: 'center', padding: '64px' }}>
          <Sparkles size={48} style={{ color: 'var(--text-muted)', marginBottom: '16px' }} />
          <h3 style={{ fontFamily: 'var(--font-display)', fontWeight: 600, marginBottom: '8px' }}>No skills detected yet</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Upload certificates to have AI extract your skills</p>
        </div>
      )}
    </div>
  )
}
