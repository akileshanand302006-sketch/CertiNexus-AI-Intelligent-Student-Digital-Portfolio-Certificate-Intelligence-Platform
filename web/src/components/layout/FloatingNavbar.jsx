import { useState, useRef, useEffect } from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Upload, Award, Sparkles, BarChart3,
  User, Bot, FileText, Moon, Sun, LogOut, ChevronDown, Bell
} from 'lucide-react'
import { useAuth } from '../../lib/auth.jsx'
import { useTheme } from '../../context/ThemeContext.jsx'

export const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload', icon: Upload, label: 'Upload' },
  { to: '/portfolio', icon: User, label: 'Portfolio' },
  { to: '/skills', icon: Sparkles, label: 'Skills' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/resume', icon: FileText, label: 'Resume' },
  { to: '/assistant', icon: Bot, label: 'AI Assistant' },
]

export default function FloatingNavbar() {
  const { user, logout } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setUserMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <header className="floating-nav-island" role="navigation" aria-label="Main Navigation">
      {/* Brand Identity with Status Beacon */}
      <div
        className="nav-brand-island"
        onClick={() => navigate('/dashboard')}
        role="button"
        tabIndex={0}
      >
        <div className="nav-brand-logo">C</div>
        <div className="nav-brand-text">
          <span>CertiNexus</span>
          <span className="nav-brand-badge">AI 2.0</span>
        </div>
        <span className="status-beacon" title="AI Intelligence Online" />
      </div>

      {/* Floating Center Capsule Links with Liquid Active Pill */}
      <nav className="nav-links-island">
        {navItems.map(({ to, icon: Icon, label }) => {
          const isActive = location.pathname === to || (to !== '/dashboard' && location.pathname.startsWith(to))
          return (
            <NavLink
              key={to}
              to={to}
              className={`nav-link-capsule ${isActive ? 'active' : ''}`}
            >
              {isActive && (
                <motion.div
                  layoutId="activeNavPill"
                  className="nav-active-pill"
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
              <Icon size={16} style={{ transition: 'transform 0.2s', transform: isActive ? 'scale(1.1)' : 'scale(1)' }} />
              <span>{label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Actions: Theme Toggle + User Menu */}
      <div className="nav-actions-island" ref={menuRef}>
        {/* Liquid Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="icon-action-btn"
          title={`Switch to ${isDark ? 'Pearl Daylight' : 'Obsidian Dark'} mode`}
          aria-label="Toggle theme"
        >
          <AnimatePresence mode="wait" initial={false}>
            {isDark ? (
              <motion.div
                key="moon"
                initial={{ rotate: -45, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 45, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Moon size={16} />
              </motion.div>
            ) : (
              <motion.div
                key="sun"
                initial={{ rotate: -45, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 45, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Sun size={16} style={{ color: '#f59e0b' }} />
              </motion.div>
            )}
          </AnimatePresence>
        </button>

        {/* User Capsule */}
        <div style={{ position: 'relative', flexShrink: 0 }}>
          <div
            className="user-avatar-pill"
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            role="button"
            tabIndex={0}
          >
            <div className="avatar-circle">
              {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
            </div>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap' }}>
              {(user?.full_name || user?.username || 'Student').split(' ')[0]}
            </span>
            <ChevronDown size={13} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
          </div>

          <AnimatePresence>
            {userMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.18 }}
                className="glass-dropdown"
              >
                <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--glass-border)' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {user?.full_name || user?.username}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                    {user?.email}
                  </div>
                </div>

                <div style={{ padding: '4px 0' }}>
                  <button
                    onClick={() => { setUserMenuOpen(false); navigate('/portfolio'); }}
                    className="glass-dropdown-item"
                  >
                    <User size={15} />
                    <span>My Digital Portfolio</span>
                  </button>
                  <button
                    onClick={() => { setUserMenuOpen(false); navigate('/upload'); }}
                    className="glass-dropdown-item"
                  >
                    <Upload size={15} />
                    <span>Scan New Certificate</span>
                  </button>
                  <button
                    onClick={() => { setUserMenuOpen(false); logout(); }}
                    className="glass-dropdown-item danger"
                  >
                    <LogOut size={15} />
                    <span>Sign Out</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  )
}
