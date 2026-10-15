import { forwardRef } from 'react'
import { useTheme } from '../../context/ThemeContext.jsx'

const OfficeChair = forwardRef(function OfficeChair({ position = [0, 0, 0.75], rotation = [0, 0, 0], compression = 0 }, ref) {
  const { isDark } = useTheme()

  return (
    <group ref={ref} position={position} rotation={rotation}>
      {/* 5-Star Caster Base Wheels */}
      <group position={[0, 0.04, 0]}>
        {[0, 1, 2, 3, 4].map((i) => {
          const angle = (i * Math.PI * 2) / 5
          const rx = Math.cos(angle) * 0.28
          const rz = Math.sin(angle) * 0.28
          return (
            <group key={i} position={[rx, 0, rz]}>
              {/* Wheel Spoke */}
              <mesh position={[-rx * 0.5, 0.02, -rz * 0.5]} rotation={[0, -angle, 0]}>
                <boxGeometry args={[0.26, 0.025, 0.03]} />
                <meshStandardMaterial color={isDark ? '#0f172a' : '#64748b'} metalness={0.9} roughness={0.3} />
              </mesh>
              {/* Roller Caster Wheel */}
              <mesh position={[0, -0.015, 0]} rotation={[0, 0, Math.PI / 2]}>
                <cylinderGeometry args={[0.025, 0.025, 0.02, 16]} />
                <meshStandardMaterial color="#020617" roughness={0.7} />
              </mesh>
            </group>
          )
        })}
        {/* Base Hub */}
        <mesh position={[0, 0.03, 0]}>
          <cylinderGeometry args={[0.05, 0.06, 0.05, 16]} />
          <meshStandardMaterial color="#1e293b" metalness={0.9} roughness={0.2} />
        </mesh>
      </group>

      {/* Hydraulic Gas-Lift Cylinder (compresses when seated) */}
      <mesh position={[0, 0.22 - compression * 0.04, 0]}>
        <cylinderGeometry args={[0.022, 0.025, 0.32 - compression * 0.04, 16]} />
        <meshStandardMaterial color="#475569" metalness={0.95} roughness={0.1} />
      </mesh>

      {/* Seat Mechanism & Ergonomic Cushion */}
      <group position={[0, 0.44 - compression * 0.04, 0]}>
        {/* Seat Cushion */}
        <mesh castShadow receiveShadow position={[0, 0, 0]}>
          <boxGeometry args={[0.48, 0.06, 0.46]} />
          <meshStandardMaterial
            color={isDark ? '#1e2230' : '#475569'}
            roughness={0.65}
            metalness={0.2}
          />
        </mesh>

        {/* Seat Bevel Piping Highlight */}
        <mesh position={[0, 0.032, 0.22]}>
          <boxGeometry args={[0.46, 0.005, 0.01]} />
          <meshBasicMaterial color={isDark ? '#38bdf8' : '#94a3b8'} transparent opacity={0.5} />
        </mesh>

        {/* Ergonomic Curved Mesh Backrest */}
        <group position={[0, 0.32, -0.22]} rotation={[-0.08, 0, 0]}>
          {/* Backrest Spine Column */}
          <mesh position={[0, 0, -0.02]}>
            <boxGeometry args={[0.06, 0.58, 0.03]} />
            <meshStandardMaterial color="#0f172a" metalness={0.8} roughness={0.3} />
          </mesh>
          {/* Contoured Back Cushion */}
          <mesh castShadow position={[0, 0.06, 0]}>
            <boxGeometry args={[0.44, 0.52, 0.04]} />
            <meshStandardMaterial
              color={isDark ? '#151926' : '#334155'}
              roughness={0.7}
              metalness={0.15}
            />
          </mesh>
          {/* Headrest */}
          <mesh position={[0, 0.36, 0.01]} castShadow>
            <boxGeometry args={[0.26, 0.12, 0.05]} />
            <meshStandardMaterial color={isDark ? '#1e2230' : '#1e293b'} roughness={0.6} />
          </mesh>
        </group>

        {/* Left Armrest */}
        <group position={[-0.26, 0.15, 0]}>
          <mesh position={[0, -0.06, 0]}>
            <cylinderGeometry args={[0.015, 0.015, 0.22, 12]} />
            <meshStandardMaterial color="#0f172a" metalness={0.9} />
          </mesh>
          <mesh position={[0, 0.05, 0.02]} castShadow>
            <boxGeometry args={[0.07, 0.025, 0.24]} />
            <meshStandardMaterial color="#020617" roughness={0.5} />
          </mesh>
        </group>

        {/* Right Armrest */}
        <group position={[0.26, 0.15, 0]}>
          <mesh position={[0, -0.06, 0]}>
            <cylinderGeometry args={[0.015, 0.015, 0.22, 12]} />
            <meshStandardMaterial color="#0f172a" metalness={0.9} />
          </mesh>
          <mesh position={[0, 0.05, 0.02]} castShadow>
            <boxGeometry args={[0.07, 0.025, 0.24]} />
            <meshStandardMaterial color="#020617" roughness={0.5} />
          </mesh>
        </group>
      </group>
    </group>
  )
})

export default OfficeChair
