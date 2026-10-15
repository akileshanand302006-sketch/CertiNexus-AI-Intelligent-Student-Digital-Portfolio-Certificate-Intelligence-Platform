import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useTheme } from '../../context/ThemeContext.jsx'

export default function NeuralNetworkScene() {
  const { isDark } = useTheme()
  const ringRef = useRef()
  const particlesRef = useRef()

  // Generate 80 floating particles in 3D space
  const [positions, connections] = useMemo(() => {
    const count = 75
    const pos = new Float32Array(count * 3)
    const points = []

    for (let i = 0; i < count; i++) {
      const x = (Math.random() - 0.5) * 8
      const y = Math.random() * 4 - 0.5
      const z = (Math.random() - 0.5) * 6 - 2
      pos[i * 3] = x
      pos[i * 3 + 1] = y
      pos[i * 3 + 2] = z
      points.push(new THREE.Vector3(x, y, z))
    }

    // Connect nearby pairs
    const linePoints = []
    for (let i = 0; i < count; i++) {
      for (let j = i + 1; j < count; j++) {
        if (points[i].distanceTo(points[j]) < 1.4) {
          linePoints.push(points[i].x, points[i].y, points[i].z)
          linePoints.push(points[j].x, points[j].y, points[j].z)
        }
      }
    }

    return [pos, new Float32Array(linePoints)]
  }, [])

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (ringRef.current) {
      ringRef.current.rotation.z = t * 0.05
      ringRef.current.rotation.x = Math.sin(t * 0.03) * 0.2
    }
    if (particlesRef.current) {
      particlesRef.current.rotation.y = t * 0.02
    }
  })

  return (
    <group position={[0, 0, -2]}>
      {/* Subtle Slow Rotating Geometric AI Rings */}
      <group ref={ringRef} position={[0, 1.8, -3]}>
        <mesh>
          <ringGeometry args={[2.8, 2.81, 64]} />
          <meshBasicMaterial
            color={isDark ? '#38bdf8' : '#94a3b8'}
            transparent
            opacity={isDark ? 0.25 : 0.15}
            side={THREE.DoubleSide}
          />
        </mesh>
        <mesh rotation={[0.4, 0.2, 0]}>
          <ringGeometry args={[3.4, 3.408, 64]} />
          <meshBasicMaterial
            color={isDark ? '#818cf8' : '#cbd5e1'}
            transparent
            opacity={isDark ? 0.18 : 0.12}
            side={THREE.DoubleSide}
          />
        </mesh>
      </group>

      {/* Floating Constellation Data Particles */}
      <group ref={particlesRef}>
        <points>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={positions.length / 3}
              array={positions}
              itemSize={3}
            />
          </bufferGeometry>
          <pointsMaterial
            size={0.04}
            color={isDark ? '#22d3ee' : '#0284c7'}
            transparent
            opacity={isDark ? 0.8 : 0.5}
            sizeAttenuation
          />
        </points>

        {/* Neural Spline Connections */}
        <lineSegments>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={connections.length / 3}
              array={connections}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial
            color={isDark ? '#38bdf8' : '#93c5fd'}
            transparent
            opacity={isDark ? 0.15 : 0.10}
          />
        </lineSegments>
      </group>
    </group>
  )
}
