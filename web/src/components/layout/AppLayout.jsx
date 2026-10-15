/**
 * CertiNexus AI — Ultra-Premium iOS Liquid Glass App Layout
 * Floating Navigation Island + 3D Cinematic Background Environment
 */

import { Outlet, useLocation } from 'react-router-dom'
import FloatingNavbar from './FloatingNavbar.jsx'
import MobileDock from './MobileDock.jsx'
import AIChatbot from '../chat/AIChatbot.jsx'
import ErrorBoundary from '../common/ErrorBoundary.jsx'
import { usePointerDepth } from '../../hooks/usePointerDepth.js'

export default function AppLayout() {
  const location = useLocation()

  // Track cursor position for liquid specular highlights
  usePointerDepth()

  return (
    <div className="certinexus-app-container" style={{ height: '100vh', maxHeight: '100vh', overflow: 'hidden', position: 'relative', display: 'flex', flexDirection: 'column' }}>
      {/* Atmospheric Gradients & Blueprint Linework Base */}
      <div className="atmospheric-ambient" />
      <div className="spatial-grid-overlay" />

      {/* Floating Top Liquid Glass Navigation Island */}
      <FloatingNavbar />

      {/* Main Page Content Layer */}
      <main className="app-main-content">
        <ErrorBoundary key={location.pathname}>
          <Outlet />
        </ErrorBoundary>
      </main>

      {/* Intelligent AI Chatbot Assistant (suppressed on dedicated AI Assistant tab) */}
      {location.pathname !== '/assistant' && <AIChatbot />}

      {/* Mobile Glass Bottom Dock */}
      <MobileDock />
    </div>
  )
}
