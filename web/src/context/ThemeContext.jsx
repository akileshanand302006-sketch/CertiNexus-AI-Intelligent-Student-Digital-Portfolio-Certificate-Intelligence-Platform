import { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => {
    try {
      const saved = localStorage.getItem('certinexus_theme')
      if (saved === 'dark' || saved === 'light' || saved === 'system') return saved
    } catch {}
    return 'dark'
  })

  const [resolvedTheme, setResolvedTheme] = useState(() => {
    if (theme === 'system') {
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return theme || 'dark'
  })

  useEffect(() => {
    const updateTheme = () => {
      let active = theme
      if (theme === 'system') {
        active = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      }
      setResolvedTheme(active)
      document.documentElement.setAttribute('data-theme', active)
      document.body.setAttribute('data-theme', active)
      try {
        localStorage.setItem('certinexus_theme', theme)
      } catch {}
    }

    updateTheme()

    if (theme === 'system' && window.matchMedia) {
      const media = window.matchMedia('(prefers-color-scheme: dark)')
      const listener = () => updateTheme()
      media.addEventListener('change', listener)
      return () => media.removeEventListener('change', listener)
    }
  }, [theme])

  const setTheme = (newTheme) => {
    // Add liquid transition ripple effect
    document.documentElement.classList.add('theme-transitioning')
    setThemeState(newTheme)
    setTimeout(() => {
      document.documentElement.classList.remove('theme-transitioning')
    }, 450)
  }

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
  }

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, isDark: resolvedTheme === 'dark', setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
