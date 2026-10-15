import { Suspense, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import Workstation from './Workstation.jsx'
import OfficeChair from './OfficeChair.jsx'
import StudentCharacter from './StudentCharacter.jsx'
import FloatingCertificate from './FloatingCertificate.jsx'
import NeuralNetworkScene from './NeuralNetworkScene.jsx'
import GlassEnvironment from './GlassEnvironment.jsx'
import SceneLighting from './SceneLighting.jsx'

function CameraRig({ progress = 0 }) {
  const targetLook = useRef(new THREE.Vector3(0, 0.82, 0.05))

  useFrame((state) => {
    // Smooth cursor parallax
    const mouseX = state.pointer.x * 0.3
    const mouseY = state.pointer.y * 0.15

    // Cinematic 3/4 camera orbit framing both student face, workstation, and monitor
    const baseAngle = 0.68 + progress * 0.32
    const camX = Math.sin(baseAngle) * 2.85 + mouseX
    const camZ = Math.cos(baseAngle) * 2.85
    const camY = 1.42 + mouseY - progress * 0.2

    state.camera.position.lerp(new THREE.Vector3(camX, camY, camZ), 0.05)
    state.camera.lookAt(targetLook.current)
  })

  return null
}

export default function StudentExperience({
  progress = 0,
  scene = 5,
  showCertificate = true,
}) {
  // Always seated facing the workstation desk as in the reference art
  const isSeated = true
  const chairCompression = 1
  const chairPos = [0, 0, 0.64]
  const chairRot = [0, Math.PI * 0.94, 0]

  return (
    <div className="spatial-canvas-container" aria-hidden="true">
      <Canvas
        camera={{ position: [1.8, 1.42, 2.3], fov: 42 }}
        dpr={[1, 1.5]}
        gl={{
          antialias: true,
          powerPreference: 'high-performance',
          alpha: true,
        }}
        shadows
      >
        <Suspense fallback={null}>
          <CameraRig progress={progress} />
          <SceneLighting />
          <GlassEnvironment />
          <NeuralNetworkScene />

          <group position={[0, -0.4, 0]}>
            <Workstation />
            <OfficeChair
              position={chairPos}
              rotation={chairRot}
              compression={chairCompression}
            />
            <StudentCharacter
              progress={progress}
              scene={scene}
            />
            <FloatingCertificate visible={showCertificate} />
          </group>
        </Suspense>
      </Canvas>
    </div>
  )
}
