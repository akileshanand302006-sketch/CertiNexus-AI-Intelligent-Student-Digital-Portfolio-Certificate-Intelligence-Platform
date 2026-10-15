import { useTheme } from '../../context/ThemeContext.jsx'

export default function GlassEnvironment() {
  const { isDark } = useTheme()

  return (
    <>
      {/* Volumetric Studio Fog */}
      <fog
        attach="fog"
        args={[isDark ? '#07090e' : '#f1f4f9', 5, 14]}
      />

      {/* Dark/Light Studio Floor Plinth */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -0.01, 0]}
        receiveShadow
      >
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial
          color={isDark ? '#05070c' : '#f8fafc'}
          roughness={0.4}
          metalness={0.8}
        />
      </mesh>

      {/* Subtle Circular Radial Plinth Ring Under Desk */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.001, 0.4]}
      >
        <ringGeometry args={[1.4, 1.415, 64]} />
        <meshBasicMaterial
          color={isDark ? '#38bdf8' : '#cbd5e1'}
          transparent
          opacity={isDark ? 0.25 : 0.4}
        />
      </mesh>
    </>
  )
}
