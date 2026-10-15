import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useTheme } from '../../context/ThemeContext.jsx'

export default function StudentCharacter({
  progress = 0,
  scene = 5, // Default to scene 5 (working at desk) if not controlled by scroll
}) {
  const { isDark } = useTheme()

  // Joint & Body Hierarchy Refs
  const rootGroupRef = useRef()
  const spineRef = useRef()
  const headRef = useRef()
  const leftArmRef = useRef()
  const leftForearmRef = useRef()
  const rightArmRef = useRef()
  const rightForearmRef = useRef()
  const leftThighRef = useRef()
  const leftShinRef = useRef()
  const rightThighRef = useRef()
  const rightShinRef = useRef()

  // Materials & Colors matching Image 3 reference art
  const hoodieColor = isDark ? '#cbd5e1' : '#e2e8f0'
  const pantsColor = isDark ? '#111520' : '#1e293b'
  const skinColor = '#dfa06e'
  const hairColor = '#503222'
  const shoeColor = '#f8fafc'
  const accentColor = '#38bdf8'
  const collarColor = '#881337'

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    if (!rootGroupRef.current) return

    // Calculate effective scene stage (0 to 6) based on progress (0.0 to 1.0) or scene prop
    let stage = scene
    if (progress > 0) {
      stage = Math.min(6, Math.floor(progress * 7))
    }

    // --- KINEMATIC BEHAVIORS: SEATED CODER WORKSTATION (From Reference Art) ---
    // The student is always seated naturally facing the desk, keyboard, and glowing monitor
    rootGroupRef.current.position.set(0, 0, 0.64)
    rootGroupRef.current.rotation.set(0, Math.PI * 0.94, 0)

    // Seated hips & thighs resting on ergonomic chair
    if (spineRef.current) {
      // Natural breathing rhythm & subtle focus lean
      const breath = Math.sin(t * 1.8) * 0.008
      const lean = stage === 2 || stage === 4 ? 0.02 : 0
      spineRef.current.position.y = 0.48 + breath
      spineRef.current.rotation.x = 0.06 + lean + Math.sin(t * 1.2) * 0.012
      spineRef.current.rotation.y = Math.sin(t * 0.8) * 0.02
    }

    // Legs bent naturally in seated pose on chair
    if (leftThighRef.current && rightThighRef.current) {
      leftThighRef.current.rotation.x = -Math.PI * 0.5
      rightThighRef.current.rotation.x = -Math.PI * 0.5
      leftShinRef.current.rotation.x = Math.PI * 0.5
      rightShinRef.current.rotation.x = Math.PI * 0.5
    }

    // Dynamic typing motions on mechanical keyboard & mouse
    const typeSpeed = stage === 0 || stage === 5 ? 10 : 8
    const leftType = Math.sin(t * typeSpeed) * 0.045
    const rightType = Math.cos(t * (typeSpeed - 0.5)) * 0.045

    if (leftArmRef.current && leftForearmRef.current) {
      leftArmRef.current.rotation.x = -0.58 + leftType * 0.5
      leftArmRef.current.rotation.y = 0.22
      leftArmRef.current.rotation.z = -0.15
      leftForearmRef.current.rotation.x = -0.78 + leftType
    }

    if (rightArmRef.current && rightForearmRef.current) {
      // Right arm coordinates between keyboard typing and mouse steering
      const mouseBias = stage === 1 || stage === 4 ? 0.06 : 0
      rightArmRef.current.rotation.x = -0.60 + rightType * 0.5
      rightArmRef.current.rotation.y = -0.18 + Math.sin(t * 1.5) * 0.04 + mouseBias
      rightArmRef.current.rotation.z = 0.15
      rightForearmRef.current.rotation.x = -0.75 + rightType
    }

    // Head focused on glowing monitor screen with subtle scanning
    if (headRef.current) {
      const lookCertificate = stage === 3 || stage === 5 ? Math.sin(t * 0.7) * 0.14 : 0
      headRef.current.rotation.y = THREE.MathUtils.lerp(headRef.current.rotation.y, -0.05 + lookCertificate, 0.05)
      headRef.current.rotation.x = 0.04 + Math.sin(t * 1.4) * 0.015
    }
  })

  return (
    <group ref={rootGroupRef} position={[0, 0, 0.64]}>
      {/* --- PELVIS & LEGS --- */}
      {/* Pelvis / Hips */}
      <mesh position={[0, 0.44, 0]} castShadow>
        <boxGeometry args={[0.26, 0.12, 0.2]} />
        <meshStandardMaterial color={pantsColor} roughness={0.7} />
      </mesh>

      {/* Left Leg */}
      <group position={[-0.1, 0.42, 0]}>
        <group ref={leftThighRef}>
          {/* Upper Thigh */}
          <mesh position={[0, 0, -0.16]} castShadow>
            <boxGeometry args={[0.11, 0.1, 0.32]} />
            <meshStandardMaterial color={pantsColor} roughness={0.7} />
          </mesh>
          {/* Knee Joint */}
          <group position={[0, 0, -0.32]} ref={leftShinRef}>
            {/* Shin / Calf */}
            <mesh position={[0, -0.18, 0]} castShadow>
              <boxGeometry args={[0.09, 0.36, 0.1]} />
              <meshStandardMaterial color={pantsColor} roughness={0.7} />
            </mesh>
            {/* Left Sneaker (Modern Streetwear High-top) */}
            <group position={[0, -0.36, 0.06]}>
              {/* Shoe Body */}
              <mesh castShadow>
                <boxGeometry args={[0.1, 0.08, 0.2]} />
                <meshStandardMaterial color={shoeColor} roughness={0.4} />
              </mesh>
              {/* Shoe Sole with Cyan Stripe */}
              <mesh position={[0, -0.042, 0]}>
                <boxGeometry args={[0.105, 0.016, 0.21]} />
                <meshStandardMaterial color="#020617" roughness={0.8} />
              </mesh>
              <mesh position={[0, -0.03, 0]}>
                <boxGeometry args={[0.106, 0.006, 0.205]} />
                <meshBasicMaterial color={accentColor} />
              </mesh>
            </group>
          </group>
        </group>
      </group>

      {/* Right Leg */}
      <group position={[0.1, 0.42, 0]}>
        <group ref={rightThighRef}>
          {/* Upper Thigh */}
          <mesh position={[0, 0, -0.16]} castShadow>
            <boxGeometry args={[0.11, 0.1, 0.32]} />
            <meshStandardMaterial color={pantsColor} roughness={0.7} />
          </mesh>
          {/* Knee Joint */}
          <group position={[0, 0, -0.32]} ref={rightShinRef}>
            {/* Shin / Calf */}
            <mesh position={[0, -0.18, 0]} castShadow>
              <boxGeometry args={[0.09, 0.36, 0.1]} />
              <meshStandardMaterial color={pantsColor} roughness={0.7} />
            </mesh>
            {/* Right Sneaker */}
            <group position={[0, -0.36, 0.06]}>
              <mesh castShadow>
                <boxGeometry args={[0.1, 0.08, 0.2]} />
                <meshStandardMaterial color={shoeColor} roughness={0.4} />
              </mesh>
              <mesh position={[0, -0.042, 0]}>
                <boxGeometry args={[0.105, 0.016, 0.21]} />
                <meshStandardMaterial color="#020617" roughness={0.8} />
              </mesh>
              <mesh position={[0, -0.03, 0]}>
                <boxGeometry args={[0.106, 0.006, 0.205]} />
                <meshBasicMaterial color={accentColor} />
              </mesh>
            </group>
          </group>
        </group>
      </group>

      {/* --- SPINE & UPPER BODY --- */}
      <group ref={spineRef} position={[0, 0.5, 0]}>
        {/* Torso Hoodie Body */}
        <mesh position={[0, 0.2, 0]} castShadow>
          <boxGeometry args={[0.34, 0.38, 0.22]} />
          <meshStandardMaterial color={hoodieColor} roughness={0.65} />
        </mesh>

        {/* Inner Neck / Collar Accent (Warm Burgundy/Crimson contrast from reference) */}
        <mesh position={[0, 0.37, 0.04]}>
          <cylinderGeometry args={[0.065, 0.07, 0.04, 16]} />
          <meshStandardMaterial color="#881337" roughness={0.6} />
        </mesh>

        {/* Kangaroo Front Pocket Pouch */}
        <mesh position={[0, 0.12, 0.112]}>
          <boxGeometry args={[0.22, 0.12, 0.03]} />
          <meshStandardMaterial color={hoodieColor} roughness={0.7} />
        </mesh>

        {/* Backpack Straps & Buckles (as seen in student character reference) */}
        {/* Left Strap */}
        <mesh position={[-0.09, 0.22, 0.115]} rotation={[0, 0, 0.05]}>
          <boxGeometry args={[0.038, 0.32, 0.015]} />
          <meshStandardMaterial color="#0f172a" roughness={0.8} />
        </mesh>
        <mesh position={[-0.09, 0.16, 0.126]}>
          <boxGeometry args={[0.042, 0.024, 0.012]} />
          <meshStandardMaterial color="#38bdf8" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Right Strap */}
        <mesh position={[0.09, 0.22, 0.115]} rotation={[0, 0, -0.05]}>
          <boxGeometry args={[0.038, 0.32, 0.015]} />
          <meshStandardMaterial color="#0f172a" roughness={0.8} />
        </mesh>
        <mesh position={[0.09, 0.16, 0.126]}>
          <boxGeometry args={[0.042, 0.024, 0.012]} />
          <meshStandardMaterial color="#38bdf8" metalness={0.8} roughness={0.2} />
        </mesh>

        {/* Hoodie Drawstrings with Aglets */}
        <mesh position={[-0.035, 0.27, 0.12]}>
          <cylinderGeometry args={[0.003, 0.003, 0.13, 8]} />
          <meshStandardMaterial color="#f8fafc" />
        </mesh>
        <mesh position={[0.035, 0.27, 0.12]}>
          <cylinderGeometry args={[0.003, 0.003, 0.13, 8]} />
          <meshStandardMaterial color="#f8fafc" />
        </mesh>

        {/* Folded Hood on Back of Neck */}
        <mesh position={[0, 0.36, -0.1]} castShadow>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial color={hoodieColor} roughness={0.7} />
        </mesh>

        {/* --- LEFT ARM --- */}
        <group position={[-0.21, 0.34, 0]} ref={leftArmRef}>
          {/* Upper Arm Hoodie Sleeve */}
          <mesh position={[0, -0.13, 0]} castShadow>
            <cylinderGeometry args={[0.05, 0.045, 0.26, 12]} />
            <meshStandardMaterial color={hoodieColor} roughness={0.65} />
          </mesh>
          {/* Left Elbow Joint */}
          <group position={[0, -0.26, 0]} ref={leftForearmRef}>
            {/* Forearm Sleeve */}
            <mesh position={[0, -0.1, 0]} castShadow>
              <cylinderGeometry args={[0.042, 0.038, 0.2, 12]} />
              <meshStandardMaterial color={hoodieColor} roughness={0.65} />
            </mesh>
            {/* Burgundy Ribbed Sleeve Cuff (from character reference art) */}
            <mesh position={[0, -0.21, 0]}>
              <cylinderGeometry args={[0.039, 0.037, 0.04, 12]} />
              <meshStandardMaterial color="#881337" roughness={0.6} />
            </mesh>
            {/* Left Hand / Fingers Typing */}
            <mesh position={[0, -0.25, 0.02]} castShadow>
              <boxGeometry args={[0.04, 0.03, 0.07]} />
              <meshStandardMaterial color={skinColor} roughness={0.5} />
            </mesh>
          </group>
        </group>

        {/* --- RIGHT ARM --- */}
        <group position={[0.21, 0.34, 0]} ref={rightArmRef}>
          {/* Upper Arm Hoodie Sleeve */}
          <mesh position={[0, -0.13, 0]} castShadow>
            <cylinderGeometry args={[0.05, 0.045, 0.26, 12]} />
            <meshStandardMaterial color={hoodieColor} roughness={0.65} />
          </mesh>
          {/* Right Elbow Joint */}
          <group position={[0, -0.26, 0]} ref={rightForearmRef}>
            {/* Forearm Sleeve */}
            <mesh position={[0, -0.1, 0]} castShadow>
              <cylinderGeometry args={[0.042, 0.038, 0.2, 12]} />
              <meshStandardMaterial color={hoodieColor} roughness={0.65} />
            </mesh>
            {/* Burgundy Ribbed Sleeve Cuff */}
            <mesh position={[0, -0.21, 0]}>
              <cylinderGeometry args={[0.039, 0.037, 0.04, 12]} />
              <meshStandardMaterial color="#881337" roughness={0.6} />
            </mesh>
            {/* Right Hand on Mouse */}
            <mesh position={[0, -0.25, 0.02]} castShadow>
              <boxGeometry args={[0.04, 0.03, 0.07]} />
              <meshStandardMaterial color={skinColor} roughness={0.5} />
            </mesh>
          </group>
        </group>

        {/* --- HEAD, MODERN GLASSES & HAIR --- */}
        <group position={[0, 0.44, 0]} ref={headRef}>
          {/* Neck */}
          <mesh position={[0, -0.03, 0]} castShadow>
            <cylinderGeometry args={[0.042, 0.048, 0.08, 12]} />
            <meshStandardMaterial color={skinColor} roughness={0.6} />
          </mesh>

          {/* Stylized Head */}
          <mesh position={[0, 0.08, 0.02]} castShadow>
            <sphereGeometry args={[0.1, 24, 24]} />
            <meshStandardMaterial color={skinColor} roughness={0.55} />
          </mesh>

          {/* Nose Bridge */}
          <mesh position={[0, 0.075, 0.12]}>
            <boxGeometry args={[0.016, 0.028, 0.024]} />
            <meshStandardMaterial color={skinColor} roughness={0.55} />
          </mesh>

          {/* --- MODERN GLASSES (Direct from primary character reference) --- */}
          <group position={[0, 0.085, 0.125]}>
            {/* Left Round Frame */}
            <mesh position={[-0.038, 0, 0]}>
              <torusGeometry args={[0.024, 0.003, 8, 20]} />
              <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
            </mesh>
            {/* Left Glass Lens with subtle cyan reflection */}
            <mesh position={[-0.038, 0, 0]}>
              <circleGeometry args={[0.023, 20]} />
              <meshPhysicalMaterial
                transmission={0.92}
                transparent
                opacity={0.8}
                roughness={0.08}
                ior={1.5}
                color="#e0f2fe"
              />
            </mesh>

            {/* Right Round Frame */}
            <mesh position={[0.038, 0, 0]}>
              <torusGeometry args={[0.024, 0.003, 8, 20]} />
              <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
            </mesh>
            {/* Right Glass Lens */}
            <mesh position={[0.038, 0, 0]}>
              <circleGeometry args={[0.023, 20]} />
              <meshPhysicalMaterial
                transmission={0.92}
                transparent
                opacity={0.8}
                roughness={0.08}
                ior={1.5}
                color="#e0f2fe"
              />
            </mesh>

            {/* Nose Bridge Wire */}
            <mesh position={[0, 0.008, -0.002]}>
              <boxGeometry args={[0.03, 0.003, 0.004]} />
              <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
            </mesh>

            {/* Left & Right Temples (Frame Arms) */}
            <mesh position={[-0.062, 0.004, -0.045]} rotation={[0, 0.15, 0]}>
              <boxGeometry args={[0.003, 0.003, 0.09]} />
              <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
            </mesh>
            <mesh position={[0.062, 0.004, -0.045]} rotation={[0, -0.15, 0]}>
              <boxGeometry args={[0.003, 0.003, 0.09]} />
              <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
            </mesh>
          </group>

          {/* --- STYLIZED TOUSLED / WAVY HAIR (Volumetric tufts as in reference) --- */}
          {/* Main Hair Cap */}
          <mesh position={[0, 0.14, 0.01]} castShadow>
            <sphereGeometry args={[0.108, 16, 16]} />
            <meshStandardMaterial color={hairColor} roughness={0.9} />
          </mesh>
          {/* Front Center Volumetric Tufts */}
          <mesh position={[0, 0.18, 0.05]} rotation={[-0.3, 0, 0]} castShadow>
            <sphereGeometry args={[0.048, 12, 12]} />
            <meshStandardMaterial color={hairColor} roughness={0.85} />
          </mesh>
          <mesh position={[-0.04, 0.17, 0.04]} rotation={[-0.2, 0.2, 0]} castShadow>
            <sphereGeometry args={[0.042, 12, 12]} />
            <meshStandardMaterial color={hairColor} roughness={0.85} />
          </mesh>
          <mesh position={[0.04, 0.17, 0.04]} rotation={[-0.2, -0.2, 0]} castShadow>
            <sphereGeometry args={[0.042, 12, 12]} />
            <meshStandardMaterial color={hairColor} roughness={0.85} />
          </mesh>
          {/* Top Tousled Crest */}
          <mesh position={[0, 0.21, -0.01]} rotation={[0.2, 0.1, 0]} castShadow>
            <sphereGeometry args={[0.052, 12, 12]} />
            <meshStandardMaterial color={hairColor} roughness={0.85} />
          </mesh>

          {/* Ambient Screen Light Reflection on Face & Glasses */}
          <pointLight position={[0, 0.05, 0.25]} intensity={0.6} color="#38bdf8" distance={0.6} />

          {/* Left & Right Stylized Ears matching Image 3 */}
          <mesh position={[-0.105, 0.08, 0.02]} rotation={[0, 0, -0.2]}>
            <cylinderGeometry args={[0.024, 0.022, 0.012, 16]} />
            <meshStandardMaterial color={skinColor} roughness={0.6} />
          </mesh>
          <mesh position={[0.105, 0.08, 0.02]} rotation={[0, 0, 0.2]}>
            <cylinderGeometry args={[0.024, 0.022, 0.012, 16]} />
            <meshStandardMaterial color={skinColor} roughness={0.6} />
          </mesh>

          {/* Sweeping tousled wavy hair tufts matching Image 3 volume */}
          <mesh position={[0, 0.24, 0.03]} rotation={[-0.4, 0, 0]} castShadow>
            <sphereGeometry args={[0.046, 12, 12]} />
            <meshStandardMaterial color={hairColor} roughness={0.85} />
          </mesh>
          <mesh position={[-0.07, 0.20, 0.02]} rotation={[-0.3, 0.3, 0]} castShadow>
            <sphereGeometry args={[0.042, 12, 12]} />
            <meshStandardMaterial color={hairColor} roughness={0.85} />
          </mesh>
          <mesh position={[0.07, 0.20, 0.02]} rotation={[-0.3, -0.3, 0]} castShadow>
            <sphereGeometry args={[0.042, 12, 12]} />
            <meshStandardMaterial color={hairColor} roughness={0.85} />
          </mesh>

          {/* Image 3 Dynamic Cinematic Lighting: Cool Monitor Glow on Face & Hands */}
          <pointLight position={[0, 0.08, 0.32]} intensity={1.3} color="#38bdf8" distance={1.2} />
          {/* Image 3 Violet Atmospheric Rim Light on Hair & Back */}
          <pointLight position={[0, 0.32, -0.28]} intensity={0.9} color="#a855f7" distance={1.5} />
        </group>
      </group>
    </group>
  )
}
