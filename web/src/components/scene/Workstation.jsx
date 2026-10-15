import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useTheme } from '../../context/ThemeContext.jsx'

export default function Workstation() {
  const { isDark } = useTheme()
  const canvasRef = useRef(document.createElement('canvas'))
  const textureRef = useRef(null)

  // Initialize procedural animated monitor screen texture
  const monitorTexture = useMemo(() => {
    const canvas = canvasRef.current
    canvas.width = 512
    canvas.height = 256
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#0a0d14'
    ctx.fillRect(0, 0, 512, 256)
    const texture = new THREE.CanvasTexture(canvas)
    textureRef.current = texture
    return texture
  }, [])

  // Animate monitor screen with live OCR scan boxes & neural waveforms
  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    // Screen background
    ctx.fillStyle = isDark ? '#080b12' : '#0f172a'
    ctx.fillRect(0, 0, 512, 256)

    // Top window bar
    ctx.fillStyle = '#1e293b'
    ctx.fillRect(0, 0, 512, 28)
    ctx.fillStyle = '#ef4444'
    ctx.beginPath(); ctx.arc(16, 14, 4, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#f59e0b'
    ctx.beginPath(); ctx.arc(28, 14, 4, 0, Math.PI * 2); ctx.fill()
    ctx.fillStyle = '#10b981'
    ctx.beginPath(); ctx.arc(40, 14, 4, 0, Math.PI * 2); ctx.fill()

    ctx.fillStyle = '#94a3b8'
    ctx.font = '10px sans-serif'
    ctx.fillText('CertiNexus AI — Neural Document Intelligence v2.0', 60, 18)

    // Certificate outline preview on screen
    ctx.strokeStyle = '#38bdf8'
    ctx.lineWidth = 1.5
    ctx.strokeRect(30, 48, 200, 140)

    // CRAFT detected OCR bounding boxes
    const scanOffset = (t * 50) % 140
    for (let i = 0; i < 4; i++) {
      const y = 60 + i * 26
      const isScanned = Math.abs((y - 48) - scanOffset) < 15
      ctx.fillStyle = isScanned ? 'rgba(6, 182, 212, 0.4)' : 'rgba(56, 189, 248, 0.15)'
      ctx.strokeStyle = isScanned ? '#22d3ee' : 'rgba(56, 189, 248, 0.4)'
      ctx.lineWidth = 1
      ctx.fillRect(45, y, 160 - (i % 2) * 30, 16)
      ctx.strokeRect(45, y, 160 - (i % 2) * 30, 16)
    }

    // Moving laser scanning line on screen
    ctx.strokeStyle = '#06b6d4'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(30, 48 + scanOffset)
    ctx.lineTo(230, 48 + scanOffset)
    ctx.stroke()

    // Right panel: Neural Classification Waveform
    ctx.fillStyle = 'rgba(255, 255, 255, 0.05)'
    ctx.fillRect(250, 48, 230, 180)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.strokeRect(250, 48, 230, 180)

    ctx.fillStyle = '#38bdf8'
    ctx.font = '11px sans-serif'
    ctx.fillText('CLASSIFICATION: 96.8% ACCREDITED', 260, 68)

    // Neural graph waveform
    ctx.strokeStyle = '#22d3ee'
    ctx.lineWidth = 1.5
    ctx.beginPath()
    for (let x = 0; x < 210; x += 5) {
      const py = 120 + Math.sin(x * 0.05 + t * 4) * 20 + Math.cos(x * 0.1 - t * 2) * 10
      if (x === 0) ctx.moveTo(260 + x, py)
      else ctx.lineTo(260 + x, py)
    }
    ctx.stroke()

    // Extracted Skills Chips
    const skills = ['Python', 'FastAPI', 'OCR', 'Three.js']
    skills.forEach((skill, idx) => {
      ctx.fillStyle = 'rgba(99, 102, 241, 0.25)'
      ctx.strokeStyle = '#818cf8'
      const sx = 260 + (idx % 2) * 105
      const sy = 160 + Math.floor(idx / 2) * 26
      ctx.fillRect(sx, sy, 95, 20)
      ctx.strokeRect(sx, sy, 95, 20)
      ctx.fillStyle = '#f8fafc'
      ctx.font = '9px sans-serif'
      ctx.fillText(skill, sx + 10, sy + 14)
    })

    if (textureRef.current) {
      textureRef.current.needsUpdate = true
    }
  })

  return (
    <group position={[0, 0, 0]}>
      {/* --- DESK SURFACE --- */}
      <mesh position={[0, 0.72, 0]} castShadow receiveShadow>
        <boxGeometry args={[2.3, 0.045, 0.95]} />
        <meshStandardMaterial
          color={isDark ? '#141824' : '#e2e8f0'}
          roughness={0.25}
          metalness={0.75}
        />
      </mesh>

      {/* Desk Top Bevel Highlight Edge */}
      <mesh position={[0, 0.744, 0.465]}>
        <boxGeometry args={[2.3, 0.002, 0.02]} />
        <meshBasicMaterial color={isDark ? '#38bdf8' : '#94a3b8'} transparent opacity={0.4} />
      </mesh>

      {/* Large Sleek Desk Mat */}
      <mesh position={[0, 0.744, 0.1]} receiveShadow>
        <boxGeometry args={[0.9, 0.002, 0.42]} />
        <meshStandardMaterial color={isDark ? '#0c0f17' : '#cbd5e1'} roughness={0.8} />
      </mesh>

      {/* Desk Legs (Sleek minimalist steel frame) */}
      <mesh position={[-1.05, 0.36, 0.38]} castShadow>
        <cylinderGeometry args={[0.025, 0.025, 0.72, 16]} />
        <meshStandardMaterial color={isDark ? '#0f121d' : '#94a3b8'} metalness={0.9} roughness={0.3} />
      </mesh>
      <mesh position={[1.05, 0.36, 0.38]} castShadow>
        <cylinderGeometry args={[0.025, 0.025, 0.72, 16]} />
        <meshStandardMaterial color={isDark ? '#0f121d' : '#94a3b8'} metalness={0.9} roughness={0.3} />
      </mesh>
      <mesh position={[-1.05, 0.36, -0.38]} castShadow>
        <cylinderGeometry args={[0.025, 0.025, 0.72, 16]} />
        <meshStandardMaterial color={isDark ? '#0f121d' : '#94a3b8'} metalness={0.9} roughness={0.3} />
      </mesh>
      <mesh position={[1.05, 0.36, -0.38]} castShadow>
        <cylinderGeometry args={[0.025, 0.025, 0.72, 16]} />
        <meshStandardMaterial color={isDark ? '#0f121d' : '#94a3b8'} metalness={0.9} roughness={0.3} />
      </mesh>

      {/* --- ULTRAWIDE MAIN MONITOR --- */}
      {/* Stand Base */}
      <mesh position={[0, 0.746, -0.25]} castShadow>
        <cylinderGeometry args={[0.15, 0.16, 0.015, 32]} />
        <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* Heavy-duty Articulating Monitor Arm Stem */}
      <mesh position={[0, 0.98, -0.28]} castShadow>
        <boxGeometry args={[0.045, 0.46, 0.045]} />
        <meshStandardMaterial color="#1e293b" metalness={0.9} roughness={0.2} />
      </mesh>

      {/* Main Curved Screen */}
      <group position={[0, 1.15, -0.22]}>
        <mesh castShadow>
          <boxGeometry args={[1.42, 0.66, 0.03]} />
          <meshStandardMaterial color="#090d16" roughness={0.4} metalness={0.9} />
        </mesh>
        <mesh position={[0, 0, 0.018]}>
          <planeGeometry args={[1.38, 0.62]} />
          <meshBasicMaterial map={monitorTexture} toneMapped={false} />
        </mesh>
        {/* Monitor Ambient Bias Backlight */}
        <pointLight position={[0, 0, -0.1]} intensity={1.2} color="#38bdf8" distance={1.4} />
      </group>

      {/* --- PC TOWER CHASSIS (from Sketchfab workstation reference) --- */}
      <group position={[0.95, 0.36, -0.1]}>
        {/* Main PC Case Body */}
        <mesh castShadow receiveShadow>
          <boxGeometry args={[0.24, 0.52, 0.48]} />
          <meshStandardMaterial color="#0f172a" metalness={0.85} roughness={0.3} />
        </mesh>

        {/* Tempered Glass Side Window Panel */}
        <mesh position={[-0.122, 0, 0]}>
          <boxGeometry args={[0.005, 0.48, 0.44]} />
          <meshPhysicalMaterial
            transmission={0.85}
            transparent
            opacity={0.8}
            roughness={0.1}
            ior={1.5}
            color="#38bdf8"
          />
        </mesh>

        {/* Internal Glowing RGB Fans & Liquid Cooling Reservoir */}
        <group position={[-0.08, 0.05, 0]}>
          {/* Cyan Intake Fan Ring 1 */}
          <mesh position={[0, 0.12, 0.16]}>
            <torusGeometry args={[0.045, 0.006, 8, 24]} />
            <meshBasicMaterial color="#06b6d4" />
          </mesh>
          {/* Cyan Intake Fan Ring 2 */}
          <mesh position={[0, -0.06, 0.16]}>
            <torusGeometry args={[0.045, 0.006, 8, 24]} />
            <meshBasicMaterial color="#38bdf8" />
          </mesh>
          {/* Liquid Cooling Tube Glow */}
          <mesh position={[0, 0.04, -0.04]} rotation={[0, 0, Math.PI / 4]}>
            <cylinderGeometry args={[0.008, 0.008, 0.18, 12]} />
            <meshBasicMaterial color="#22d3ee" />
          </mesh>
          {/* GPU Shroud with Cyan Logo Stripe */}
          <mesh position={[0, -0.08, -0.02]}>
            <boxGeometry args={[0.06, 0.04, 0.22]} />
            <meshStandardMaterial color="#1e293b" metalness={0.9} />
          </mesh>
          {/* Internal Chassis Light */}
          <pointLight position={[0, 0, 0]} intensity={0.9} color="#06b6d4" distance={0.8} />
        </group>
      </group>

      {/* --- DESKTOP STEREO MONITORS (Audio Speakers) --- */}
      {/* Left Studio Speaker */}
      <group position={[-0.82, 0.88, -0.18]} rotation={[0, 0.25, 0]}>
        <mesh castShadow>
          <boxGeometry args={[0.12, 0.22, 0.14]} />
          <meshStandardMaterial color="#0f172a" roughness={0.5} />
        </mesh>
        {/* Speaker Tweeter */}
        <mesh position={[0, 0.05, 0.071]}>
          <circleGeometry args={[0.022, 16]} />
          <meshStandardMaterial color="#334155" metalness={0.7} />
        </mesh>
        {/* Speaker Woofer with Cyan Ring */}
        <mesh position={[0, -0.04, 0.071]}>
          <circleGeometry args={[0.038, 24]} />
          <meshStandardMaterial color="#020617" roughness={0.3} />
        </mesh>
        <mesh position={[0, -0.04, 0.072]}>
          <ringGeometry args={[0.036, 0.039, 24]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>
      </group>

      {/* Right Studio Speaker */}
      <group position={[0.82, 0.88, -0.18]} rotation={[0, -0.25, 0]}>
        <mesh castShadow>
          <boxGeometry args={[0.12, 0.22, 0.14]} />
          <meshStandardMaterial color="#0f172a" roughness={0.5} />
        </mesh>
        <mesh position={[0, 0.05, 0.071]}>
          <circleGeometry args={[0.022, 16]} />
          <meshStandardMaterial color="#334155" metalness={0.7} />
        </mesh>
        <mesh position={[0, -0.04, 0.071]}>
          <circleGeometry args={[0.038, 24]} />
          <meshStandardMaterial color="#020617" roughness={0.3} />
        </mesh>
        <mesh position={[0, -0.04, 0.072]}>
          <ringGeometry args={[0.036, 0.039, 24]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>
      </group>

      {/* --- KEYBOARD & MOUSE --- */}
      {/* Keyboard with illuminated keys */}
      <mesh position={[0, 0.748, 0.15]} castShadow>
        <boxGeometry args={[0.42, 0.014, 0.14]} />
        <meshStandardMaterial color="#0f172a" roughness={0.3} metalness={0.7} />
      </mesh>
      {/* Glowing keyboard backlight stripe */}
      <mesh position={[0, 0.756, 0.15]}>
        <planeGeometry args={[0.4, 0.12]} rotation={[-Math.PI / 2, 0, 0]} />
        <meshBasicMaterial color="#06b6d4" transparent opacity={0.35} />
      </mesh>

      {/* Precision Mouse */}
      <mesh position={[0.3, 0.75, 0.15]} castShadow>
        <boxGeometry args={[0.065, 0.02, 0.10]} />
        <meshStandardMaterial color="#1e293b" roughness={0.2} metalness={0.8} />
      </mesh>
      {/* Mouse RGB Glow Ring */}
      <mesh position={[0.3, 0.76, 0.15]}>
        <ringGeometry args={[0.012, 0.015, 16]} />
        <meshBasicMaterial color="#38bdf8" />
      </mesh>

      {/* Holographic Credential Dock Stand on Left Desk Edge */}
      <group position={[-0.95, 0.76, 0.1]}>
        <mesh>
          <boxGeometry args={[0.18, 0.02, 0.12]} />
          <meshStandardMaterial color="#1e293b" metalness={0.9} roughness={0.2} />
        </mesh>
        {/* Upright Glass Award Plaque */}
        <mesh position={[0, 0.1, 0]}>
          <boxGeometry args={[0.14, 0.18, 0.01]} />
          <meshPhysicalMaterial
            transmission={0.9}
            opacity={1}
            transparent
            roughness={0.1}
            ior={1.5}
            color="#38bdf8"
          />
        </mesh>
      </group>

      {/* --- WARM CANDLE / DESK LIGHT (From Reference Art Left Desk Edge) --- */}
      <group position={[-0.72, 0.745, 0.22]}>
        {/* Candle Holder Base */}
        <mesh position={[0, 0.015, 0]}>
          <cylinderGeometry args={[0.032, 0.038, 0.03, 16]} />
          <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.3} />
        </mesh>
        {/* Wax Column */}
        <mesh position={[0, 0.05, 0]}>
          <cylinderGeometry args={[0.024, 0.024, 0.05, 16]} />
          <meshStandardMaterial color="#fef3c7" roughness={0.4} />
        </mesh>
        {/* Wick */}
        <mesh position={[0, 0.078, 0]}>
          <cylinderGeometry args={[0.002, 0.002, 0.012, 8]} />
          <meshBasicMaterial color="#1f2937" />
        </mesh>
        {/* Glowing Candle Flame */}
        <mesh position={[0, 0.09, 0]}>
          <sphereGeometry args={[0.008, 12, 12]} />
          <meshBasicMaterial color="#f59e0b" />
        </mesh>
        {/* Warm Ambient Candle Point Light (warm-cool contrast from Image 3) */}
        <pointLight position={[0, 0.1, 0]} intensity={1.1} color="#f59e0b" distance={1.2} />
      </group>

      {/* --- MODERN DESK GADGET / HEADPHONES (From Reference Art Right Desk Edge) --- */}
      <group position={[0.68, 0.748, 0.22]} rotation={[0, -0.4, 0]}>
        {/* Sleek Oval Earcups */}
        <mesh position={[-0.04, 0.025, 0]}>
          <boxGeometry args={[0.025, 0.05, 0.06]} />
          <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.3} />
        </mesh>
        <mesh position={[0.04, 0.025, 0]}>
          <boxGeometry args={[0.025, 0.05, 0.06]} />
          <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.3} />
        </mesh>
        {/* Headband Arc */}
        <mesh position={[0, 0.045, -0.01]}>
          <torusGeometry args={[0.042, 0.005, 8, 16, Math.PI]} />
          <meshStandardMaterial color="#334155" metalness={0.9} roughness={0.2} />
        </mesh>
      </group>
    </group>
  )
}
