import { useTheme } from '../../context/ThemeContext.jsx'

export default function SceneFallback() {
  const { isDark } = useTheme()

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1440 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ opacity: isDark ? 0.4 : 0.2 }}
      >
        <circle cx="720" cy="450" r="320" stroke={isDark ? '#38bdf8' : '#0284c7'} strokeWidth="1" strokeDasharray="6 6" />
        <circle cx="720" cy="450" r="480" stroke={isDark ? '#818cf8' : '#6366f1'} strokeWidth="1" strokeDasharray="12 12" />
        <rect x="520" y="280" width="400" height="240" rx="20" stroke={isDark ? '#38bdf8' : '#0ea5e9'} strokeWidth="2" fill="none" />
        <line x1="520" y1="400" x2="920" y2="400" stroke="#06b6d4" strokeWidth="2" opacity="0.6" />
      </svg>
    </div>
  )
}
