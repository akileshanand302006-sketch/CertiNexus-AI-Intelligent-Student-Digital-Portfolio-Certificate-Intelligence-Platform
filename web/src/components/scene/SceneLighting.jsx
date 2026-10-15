import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useTheme } from '../../context/ThemeContext.jsx'

export default function SceneLighting() {
  const { isDark } = useTheme()
  const rimLightRef = useRef()

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (rimLightRef.current) {
      // Gentle atmospheric pulsing
      rimLightRef.current.intensity = (isDark ? 3.2 : 2.0) + Math.sin(t * 1.5) * 0.3
    }
  })

  return (
    <>
      {/* Ambient Fill */}
      <ambientLight intensity={isDark ? 0.65 : 1.2} />

      {/* Key Studio Light (Ice Blue / Cyan AI Key) */}
      <directionalLight
        position={[4, 6, 4]}
        intensity={isDark ? 2.5 : 2.0}
        color={isDark ? '#38bdf8' : '#ffffff'}
        castShadow
        shadow-mapSize={[1024, 1024]}
        shadow-bias={-0.0001}
      />

      {/* Fill Light (Deep Indigo / Violet) */}
      <directionalLight
        position={[-5, 3, -2]}
        intensity={isDark ? 1.4 : 0.8}
        color={isDark ? '#818cf8' : '#e0e7ff'}
      />

      {/* Brilliant Rim / Contour Backlight (Highlights hoodie, hair, desk edge) */}
      <spotLight
        ref={rimLightRef}
        position={[0, 4, -4.5]}
        target-position={[0, 0.8, 0]}
        intensity={isDark ? 3.2 : 2.0}
        color={isDark ? '#06b6d4' : '#38bdf8'}
        angle={0.65}
        penumbra={0.8}
      />

      {/* Desk Surface Underglow */}
      <pointLight
        position={[0, 0.4, 0.3]}
        intensity={isDark ? 0.9 : 0.5}
        color="#22d3ee"
        distance={2.5}
      />
    </>
  )
}
