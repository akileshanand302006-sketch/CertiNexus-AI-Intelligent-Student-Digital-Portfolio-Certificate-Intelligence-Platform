import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Upload, Award, Sparkles, BarChart3, User, FileText
} from 'lucide-react'

const mobileItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dash' },
  { to: '/upload', icon: Upload, label: 'Upload' },
  { to: '/portfolio', icon: User, label: 'Portfolio' },
  { to: '/skills', icon: Sparkles, label: 'Skills' },
  { to: '/analytics', icon: BarChart3, label: 'Stats' },
  { to: '/assistant', icon: Sparkles, label: 'Assistant' },
]

export default function MobileDock() {
  const location = useLocation()

  return (
    <nav className="mobile-glass-dock" role="navigation" aria-label="Mobile Navigation">
      {mobileItems.map(({ to, icon: Icon, label }) => {
        const isActive = location.pathname === to || (to !== '/dashboard' && location.pathname.startsWith(to))
        return (
          <NavLink
            key={to}
            to={to}
            className={`mobile-dock-item ${isActive ? 'active' : ''}`}
          >
            <Icon size={19} />
            <span>{label}</span>
          </NavLink>
        )
      })}
    </nav>
  )
}
