import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useTheme } from '../../context/ThemeContext.jsx'

export default function FloatingCertificate({ visible = true }) {
  const { isDark } = useTheme()
  const groupRef = useRef()
  const scanLineRef = useRef()
  const canvasRef = useRef(document.createElement('canvas'))
  const textureRef = useRef(null)

  // Generate procedural high-resolution certificate texture
  const certTexture = useMemo(() => {
    const canvas = canvasRef.current
    canvas.width = 512
    canvas.height = 700
    const ctx = canvas.getContext('2d')

    // Certificate parchment background
    ctx.fillStyle = isDark ? '#0b1120' : '#f8fafc'
    ctx.fillRect(0, 0, 512, 700)

    // Ornamental border
    ctx.strokeStyle = isDark ? '#38bdf8' : '#0284c7'
    ctx.lineWidth = 4
    ctx.strokeRect(16, 16, 480, 668)
    ctx.strokeStyle = isDark ? 'rgba(56, 189, 248, 0.3)' : 'rgba(2, 132, 199, 0.3)'
    ctx.lineWidth = 1.5
    ctx.strokeRect(26, 26, 460, 648)

    // Gold/Cyan crest emblem at top
    ctx.beginPath()
    ctx.arc(256, 80, 36, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(6, 182, 212, 0.2)'
    ctx.fill()
    ctx.strokeStyle = '#22d3ee'
    ctx.lineWidth = 2
    ctx.stroke()

    ctx.fillStyle = '#38bdf8'
    ctx.font = 'bold 18px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('AI', 256, 86)

    // Header Title
    ctx.fillStyle = isDark ? '#ffffff' : '#0f172a'
    ctx.font = 'bold 22px sans-serif'
    ctx.fillText('CERTIFICATE OF ACHIEVEMENT', 256, 150)

    ctx.font = '12px sans-serif'
    ctx.fillStyle = isDark ? '#94a3b8' : '#64748b'
    ctx.fillText('CERTINEXUS NEURAL CREDENTIAL INTELLIGENCE', 256, 175)

    // Decorative divider
    ctx.strokeStyle = '#06b6d4'
    ctx.beginPath()
    ctx.moveTo(120, 195)
    ctx.lineTo(392, 195)
    ctx.stroke()

    // Recipient & Body
    ctx.fillStyle = isDark ? '#f8fafc' : '#1e293b'
    ctx.font = 'italic 15px Georgia, serif'
    ctx.fillText('This credential is officially conferred upon', 256, 235)

    ctx.font = 'bold 24px sans-serif'
    ctx.fillStyle = '#38bdf8'
    ctx.fillText('Verified Scholar', 256, 275)

    ctx.font = '13px sans-serif'
    ctx.fillStyle = isDark ? '#cbd5e1' : '#475569'
    ctx.fillText('for exceptional mastery in Machine Learning, OCR Systems', 256, 315)
    ctx.fillText('& Automated Digital Portfolio Intelligence', 256, 335)

    // Detected CRAFT OCR Bounding Boxes
    const ocrFields = [
      { label: 'ISSUER: Stanford Online / AI Academy', y: 380 },
      { label: 'CLASSIFICATION: 96.8% HACKATHON / TECH', y: 418 },
      { label: 'EXTRACTED ENTITY: Python, FastAPI, CRAFT OCR', y: 456 },
      { label: 'VERIFICATION HASH: SHA-256 #8f92a1...bc74', y: 494 },
    ]

    ocrFields.forEach((field) => {
      ctx.fillStyle = 'rgba(6, 182, 212, 0.12)'
      ctx.fillRect(48, field.y, 416, 28)
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)'
      ctx.lineWidth = 1
      ctx.strokeRect(48, field.y, 416, 28)

      ctx.fillStyle = isDark ? '#38bdf8' : '#0284c7'
      ctx.font = 'bold 11px monospace'
      ctx.textAlign = 'left'
      ctx.fillText(field.label, 62, field.y + 18)
    })

    // QR Verification & Stamp Seal
    ctx.fillStyle = '#06b6d4'
    ctx.fillRect(60, 560, 70, 70)
    ctx.fillStyle = isDark ? '#0b1120' : '#f8fafc'
    ctx.fillRect(66, 566, 58, 58)
    ctx.fillStyle = '#38bdf8'
    ctx.font = '10px monospace'
    ctx.textAlign = 'center'
    ctx.fillText('QR VERIFIED', 95, 600)

    // Signature Line
    ctx.strokeStyle = isDark ? '#475569' : '#cbd5e1'
    ctx.beginPath()
    ctx.moveTo(300, 610)
    ctx.lineTo(440, 610)
    ctx.stroke()
    ctx.fillStyle = isDark ? '#94a3b8' : '#64748b'
    ctx.font = '11px sans-serif'
    ctx.fillText('Verified Registrar', 370, 628)

    const texture = new THREE.CanvasTexture(canvas)
    textureRef.current = texture
    return texture
  }, [isDark])

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (!groupRef.current) return

    // Gentle floating levitation
    groupRef.current.position.y = 1.35 + Math.sin(t * 1.5) * 0.04
    groupRef.current.rotation.y = -0.32 + Math.sin(t * 0.8) * 0.04
    groupRef.current.rotation.x = 0.05 + Math.cos(t * 0.9) * 0.02

    // Vertical scanning laser beam
    if (scanLineRef.current) {
      scanLineRef.current.position.y = Math.sin(t * 2.2) * 0.42
    }
  })

  if (!visible) return null

  return (
    <group ref={groupRef} position={[0.95, 1.35, 0.15]} rotation={[0.05, -0.32, 0]}>
      {/* Translucent Liquid Glass Certificate Plane */}
      <mesh castShadow receiveShadow>
        <planeGeometry args={[0.76, 1.02]} />
        <meshPhysicalMaterial
          map={certTexture}
          transmission={0.4}
          transparent
          opacity={0.96}
          roughness={0.15}
          ior={1.5}
          reflectivity={0.9}
        />
      </mesh>

      {/* Outer Illuminated Glass Bevel Rim */}
      <lineSegments position={[0, 0, 0.005]}>
        <edgesGeometry args={[new THREE.PlaneGeometry(0.76, 1.02)]} />
        <lineBasicMaterial color={isDark ? '#38bdf8' : '#0284c7'} transparent opacity={0.7} />
      </lineSegments>

      {/* Moving Laser Scanning Beam */}
      <mesh ref={scanLineRef} position={[0, 0, 0.012]}>
        <planeGeometry args={[0.74, 0.008]} />
        <meshBasicMaterial color="#22d3ee" transparent opacity={0.95} />
      </mesh>

      {/* Soft Cyan Laser Glow Light */}
      <pointLight position={[0, 0, 0.15]} intensity={0.8} color="#38bdf8" distance={1.2} />
    </group>
  )
}
