import { useEffect } from 'react'

export function usePointerDepth() {
  useEffect(() => {
    let ticking = false

    const handlePointerMove = (e) => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const x = ((e.clientX / window.innerWidth) * 100).toFixed(1)
          const y = ((e.clientY / window.innerHeight) * 100).toFixed(1)
          document.documentElement.style.setProperty('--mouse-x', `${x}%`)
          document.documentElement.style.setProperty('--mouse-y', `${y}%`)
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener('pointermove', handlePointerMove, { passive: true })

    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
    }
  }, [])
}
