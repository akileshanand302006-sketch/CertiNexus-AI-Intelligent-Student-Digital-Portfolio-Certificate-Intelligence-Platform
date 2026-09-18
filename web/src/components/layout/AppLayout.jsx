/**
 * CertiNexus AI — App Layout with Glass Sidebar
 */

import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../lib/auth.jsx'
import {
  LayoutDashboard, Upload, Award, Sparkles, BarChart3,
  User, Brain, LogOut, Search, FolderOpen, FileText
} from 'lucide-react'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload', icon: Upload, label: 'Upload' },
  { to: '/certificates', icon: Award, label: 'Certificates' },
  { to: '/skills', icon: Sparkles, label: 'Skills' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/portfolio', icon: User, label: 'Portfolio' },
  { to: '/resume', icon: FileText, label: 'Resume' },
  { to: '/research', icon: Brain, label: 'ML Research' },
]

export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="app-layout">
      {/* Aurora Background */}
      <div className="aurora-bg">
        <div className="aurora-blob aurora-blob-1" />
        <div className="aurora-blob aurora-blob-2" />
        <div className="aurora-blob aurora-blob-3" />
      </div>

      {/* Sidebar */}
      <aside className="sidebar">
        <div style={{ marginBottom: '32px' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            cursor: 'pointer'
          }} onClick={() => navigate('/dashboard')}>
            <div style={{
              width: 36, height: 36, borderRadius: '10px',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.1rem', fontWeight: 800, color: 'white',
              fontFamily: 'var(--font-display)',
            }}>C</div>
            <div>
              <div style={{
                fontFamily: 'var(--font-display)', fontWeight: 700,
                fontSize: '1rem', color: 'var(--text-primary)'
              }}>CertiNexus</div>
              <div style={{
                fontSize: '0.65rem', color: 'var(--color-primary-light)',
                fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase',
              }}>AI Platform</div>
            </div>
          </div>
        </div>

        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User info */}
        <div style={{
          marginTop: 'auto', paddingTop: '16px',
          borderTop: '1px solid var(--glass-border)',
        }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '8px', marginBottom: '8px',
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.8rem', fontWeight: 700, color: 'white',
            }}>
              {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
            </div>
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                {user?.full_name || user?.username}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>
                {user?.email}
              </div>
            </div>
          </div>
          <button onClick={logout} className="nav-item" style={{
            width: '100%', border: 'none', background: 'transparent',
            color: 'var(--text-tertiary)', cursor: 'pointer',
          }}>
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
