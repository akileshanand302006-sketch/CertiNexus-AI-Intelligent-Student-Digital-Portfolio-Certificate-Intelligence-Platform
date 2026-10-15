/**
 * CertiNexus AI — Single-Screen Cinematic Experience & Liquid Glass System
 * Seamless single-page tab switcher without vertical scrolling
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Upload, Sparkles, BarChart3,
  User, FileText, Bot, ArrowRight, Play, Sun, Moon,
  ChevronRight, ChevronLeft, Award, ShieldCheck, Zap
} from 'lucide-react'
import StudentExperience from '../components/scene/StudentExperience.jsx'
import { usePointerDepth } from '../hooks/usePointerDepth.js'
import { useTheme } from '../context/ThemeContext.jsx'

export const landingTabs = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    badge: 'Spatial Workspace',
    title: 'Intelligent Student Workspace',
    description: 'Transform verified credentials and achievements into structured, searchable intelligence with live metrics and skill synthesis.',
    action: 'Enter Dashboard',
    route: '/dashboard',
    scene: 0,
  },
  {
    id: 'upload',
    label: 'Upload',
    icon: Upload,
    badge: 'Scanning Chamber',
    title: 'Document Processing & Auto-Extraction',
    description: 'Drag & drop certificates directly into a translucent scanning chamber with real-time text detection, organization recognition, and entity extraction.',
    action: 'Upload Certificate',
    route: '/upload',
    scene: 2,
  },
  {
    id: 'portfolio',
    label: 'Portfolio',
    icon: User,
    badge: 'Digital Credential Web',
    title: 'Verified Digital Portfolio & Document Viewer',
    description: 'Interactive digital portfolio with instant document preview, verified achievement badges, competency profiles, and shareable public links.',
    action: 'Preview Portfolio',
    route: '/portfolio',
    scene: 3,
  },
  {
    id: 'skills',
    label: 'Skills',
    icon: Sparkles,
    badge: 'Competency Graph',
    title: 'Skill Intelligence Constellation',
    description: 'Extracted competencies form glowing glass chips mapping academic achievements into verified industry and software skills.',
    action: 'Explore Skills',
    route: '/skills',
    scene: 5,
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    badge: 'Achievement Analytics',
    title: 'Visual Analytics & Readiness Index',
    description: 'Comprehensive visual breakdowns of your achievements across categories, skill growth timelines, and academic readiness indices.',
    action: 'View Analytics',
    route: '/analytics',
    scene: 4,
  },
  {
    id: 'resume',
    label: 'Resume',
    icon: FileText,
    badge: 'ATS-Optimized Engine',
    title: 'Automated Resume Synthesis',
    description: 'Generate formatted, ATS-compliant resumes directly from verified certificate achievements, course milestones, and extracted skills.',
    action: 'Build Resume',
    route: '/resume',
    scene: 5,
  },
  {
    id: 'assistant',
    label: 'AI Assistant',
    icon: Bot,
    badge: 'Intelligent Advisor',
    title: 'Certificate & Career AI Assistant',
    description: 'Ask questions about your uploaded certificates, query verified skills and dates, detect career skill gaps, and receive personalized certification suggestions.',
    action: 'Launch Assistant',
    route: '/assistant',
    scene: 5,
  },
]

export default function Landing() {
  usePointerDepth()
  const { isDark, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [activeTabIdx, setActiveTabIdx] = useState(0)

  const currentTab = landingTabs[activeTabIdx] || landingTabs[0]

  const nextTab = () => {
    setActiveTabIdx((prev) => (prev + 1) % landingTabs.length)
  }

  const prevTab = () => {
    setActiveTabIdx((prev) => (prev - 1 + landingTabs.length) % landingTabs.length)
  }

  return (
    <div style={{ height: '100vh', width: '100vw', overflow: 'hidden', position: 'relative' }}>
      {/* Atmospheric Base Overlays */}
      <div className="atmospheric-ambient" />
      <div className="spatial-grid-overlay" />

      {/* 3D Student Cinematic Film Experience */}
      <StudentExperience
        progress={activeTabIdx / (landingTabs.length - 1)}
        scene={currentTab.scene}
        showCertificate={activeTabIdx >= 1}
      />

      {/* Floating Top Liquid Glass Navigation Island */}
      <header className="floating-nav-island" role="navigation" aria-label="Main Navigation">
        <div className="nav-brand-island" onClick={() => navigate('/')}>
          <div className="nav-brand-logo">C</div>
          <div className="nav-brand-text">
            <span>CertiNexus</span>
            <span className="nav-brand-badge">STUDIO</span>
          </div>
          <span className="status-beacon" title="System Active" />
        </div>

        {/* Exact Tab Names Navigation Pills */}
        <nav className="nav-links-island">
          {landingTabs.map((tab, idx) => {
            const Icon = tab.icon
            const isActive = activeTabIdx === idx
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTabIdx(idx)}
                className={`nav-link-capsule ${isActive ? 'active' : ''}`}
                style={{ cursor: 'pointer', background: 'transparent', border: 'none' }}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeLandingTabPill"
                    className="nav-active-pill"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
                <Icon size={15} style={{ transition: 'transform 0.2s', transform: isActive ? 'scale(1.1)' : 'scale(1)' }} />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>

        {/* Actions: Theme Toggle + Sign In / Register */}
        <div className="nav-actions-island">
          <button
            onClick={toggleTheme}
            className="icon-action-btn"
            title={`Switch to ${isDark ? 'Pearl Daylight' : 'Obsidian Dark'} mode`}
            aria-label="Toggle theme"
          >
            {isDark ? <Moon size={16} /> : <Sun size={16} style={{ color: '#f59e0b' }} />}
          </button>
          <button
            onClick={() => navigate('/login')}
            className="btn-liquid btn-liquid-ghost"
            style={{ padding: '7px 16px', fontSize: '0.84rem' }}
          >
            Sign In
          </button>
          <button
            onClick={() => navigate('/register')}
            className="btn-liquid btn-liquid-primary"
            style={{ padding: '7px 18px', fontSize: '0.84rem' }}
          >
            Get Started
          </button>
        </div>
      </header>

      {/* Floating Spatial Information Sheet (Single-Screen Centered Bottom) */}
      <div style={{
        position: 'fixed',
        bottom: 32,
        left: '50%',
        transform: 'translateX(-50%)',
        width: 'calc(100% - 48px)',
        maxWidth: '860px',
        zIndex: 20,
      }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={currentTab.id}
            initial={{ opacity: 0, y: 18, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -14, scale: 0.98 }}
            transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
            className="glass-panel glass-specular-glow"
            style={{ padding: '28px 34px', borderRadius: '30px' }}
          >
            {/* Top Pill Bar */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="glass-pill active" style={{ fontSize: '0.74rem', padding: '5px 12px' }}>
                  <span className="status-beacon" style={{ width: 6, height: 6 }} />
                  {currentTab.badge}
                </span>
                <span className="glass-pill" style={{ fontSize: '0.74rem', padding: '5px 12px', textTransform: 'uppercase' }}>
                  {currentTab.label} ({activeTabIdx + 1} OF {landingTabs.length})
                </span>
              </div>

              {/* Quick Skip to App */}
              <button
                onClick={() => navigate('/dashboard')}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-tertiary)',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                Enter App <ChevronRight size={14} />
              </button>
            </div>

            {/* Section Title & Description */}
            <h1 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(1.6rem, 2.8vw, 2.2rem)',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              lineHeight: 1.15,
              marginBottom: '10px',
              color: 'var(--text-primary)',
            }}>
              {currentTab.title}
            </h1>

            <p style={{
              color: 'var(--text-secondary)',
              fontSize: '0.96rem',
              lineHeight: 1.55,
              maxWidth: '680px',
              marginBottom: '22px',
            }}>
              {currentTab.description}
            </p>

            {/* Interactive Action Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <button
                onClick={() => navigate(currentTab.route)}
                className="btn-liquid btn-liquid-primary"
                style={{ padding: '10px 22px' }}
              >
                <span>{currentTab.action}</span>
                <ArrowRight size={16} />
              </button>

              <button
                onClick={prevTab}
                className="btn-liquid btn-liquid-ghost"
                style={{ padding: '10px 14px' }}
                title="Previous Tab"
              >
                <ChevronLeft size={16} />
              </button>

              <button
                onClick={nextTab}
                className="btn-liquid btn-liquid-ghost"
                style={{ padding: '10px 18px', gap: '6px' }}
                title="Next Tab"
              >
                <span>Next Tab</span>
                <ChevronRight size={16} />
              </button>

              {/* Tab Progress Indicator */}
              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
                {landingTabs.map((t, idx) => (
                  <div
                    key={t.id}
                    onClick={() => setActiveTabIdx(idx)}
                    style={{
                      width: activeTabIdx === idx ? 24 : 8,
                      height: 6,
                      borderRadius: 3,
                      background: activeTabIdx === idx ? 'var(--brand-ice)' : 'rgba(255, 255, 255, 0.2)',
                      cursor: 'pointer',
                      transition: 'all 0.25s ease',
                    }}
                    title={t.label}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
