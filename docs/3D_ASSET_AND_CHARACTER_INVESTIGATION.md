# CertiNexus AI — 3D Asset, Character & Kinematic Rig Investigation Report

## 1. Sketchfab Asset Investigation (`https://skfb.ly/oHBOn`)

### URL Resolution & Identity
- **Supplied Link**: `https://skfb.ly/oHBOn`
- **Resolved URL**: `https://sketchfab.com/3d-models/pc-workstation-057fbc5a0e9641e49e0f3408093ae1a4`
- **Model Name**: **PC workstation**
- **Authors / Creators**: Frida, Dina, and Jorkop
- **Production Pipeline**: Autodesk Maya (modeling), Substance Painter (texturing), Unreal Engine (lighting/staging)
- **License**: Creative Commons Attribution 4.0 International (**CC-BY 4.0**)

### Content, Geometry & Rig Analysis
- **Geometry**: Hard-surface computer workstation setup consisting of a modern computer chassis, ultrawide curved monitor, mechanical keyboard, ergonomic mouse, and desk frame.
- **Humanoid Character Check**: **NOT PRESENT**. The model contains zero human characters.
- **Skeletal Rig & Armatures**: **NONE**. The model is an unrigged static environment prop.
- **Animation Clips**: **ZERO**. There are no walking, sitting, turning, typing, or gestural animation tracks.
- **Download / API Status**: Model is available on Sketchfab under CC-BY with manual download requiring authenticated user session/tokens.
- **Determined Role**: **Supporting Environmental Reference Asset**. The model provides the industrial and desktop aesthetic for the workstation environment, but **cannot serve as the student character**.

---

## 2. Stylized 3D Student Character Design & Reference Fidelity

To fulfill the primary art reference (`media_1791781079196.jpg`) without violating licensing or making false claims about static props:

- **Art Direction**: Stylized, high-fidelity college student at a high-tech AI credential workstation.
- **Facial Features & Modern Glasses**:
  - Thin dark round wireframe glasses perched on the nose bridge.
  - Refractive physical glass lenses with subtle cyan screen reflections (`transmission: 0.92`, `ior: 1.5`).
  - Expressive head rotation responding dynamically to scroll position and screen interaction.
- **Volumetric Styled Hair**:
  - Multi-tufted tousled/wavy auburn/dark espresso hairstyle with front crest and lateral volume.
- **Clothing & Textures**:
  - Modern hoodie with deep pocket pouch and white drawstrings.
  - Inner neck collar and ribbed sleeve cuffs in deep burgundy/crimson (`#881337`), perfectly matching the reference art.
  - Dual backpack shoulder straps crossing the chest with metallic cyan buckles.
  - High-top streetwear sneakers with cyan active sole stripes (`#38bdf8`).
- **Screen & Atmospheric Lighting**:
  - Dedicated front cyan light casting monitor reflections onto the student's face, hands, and chest.
  - Blue-violet backlight creating soft cinematic hair highlights.

---

## 3. Coordinated 7-Phase Cinematic Kinematic Timeline

The 3D student scene coordinates real kinematic transformations driven by scroll progress ($p \in [0, 1]$):

| Phase | Scene Title | Kinematic Actions & Physics Coordination |
| :--- | :--- | :--- |
| **A** | **Arrival** ($p < 0.15$) | Student enters environment from right ($X: 2.4 \to 0.9$). Natural gait with striding thighs/calves, swinging arms, bouncing spine, and forward eye tracking. |
| **B** | **Approach** ($0.15 \le p < 0.30$) | Student decelerates near workstation ($X: 0.4, Z: 0.95$), turning body $-36^\circ$ toward desk and chair. |
| **C** | **Chair Interaction** ($0.30 \le p < 0.45$) | Right arm reaches backward to grip the ergonomic office chair. Chair rolls backward on 5-star casters ($Z: 0.72 \to 0.95$). |
| **D** | **Sitting** ($0.45 \le p < 0.58$) | Torso and hips lower smoothly ($Y: 0.88 \to 0.52$). Hips and knees bend to $90^\circ$. Hydraulic gas-lift cylinder compresses downwards by $4\text{cm}$, and chair rolls inward to desk. |
| **E** | **Working & Typing** ($0.58 \le p < 0.75$) | Student rests hands on keyboard and mouse. Fast dual-arm typing motion on keys with periodic mouse steering. Chest expands and contracts with subtle natural breathing rhythm ($f = 1.8\text{ Hz}$). |
| **F** | **AI Activation** ($0.75 \le p < 0.90$) | Monitor activates with live CRAFT OCR bounding boxes and neural classification waveforms. Floating holographic certificate materializes with cyan laser scanning beam. Head tilts towards floating certificate. |
| **G** | **Continued Orbit** ($p \ge 0.90$) | Camera orbits smoothly around workstation while student continues typing and monitoring real-time skill extraction chips. |

---

## 4. Workstation Procedural Screen Texture
- Utilizes an active HTML5 Canvas rendered as a live Three.js canvas texture (`CanvasTexture`).
- Features real CRAFT bounding boxes, CRNN text extraction pulses, a real-time sinusoidal neural classification waveform, and extracted skill chips (Python, FastAPI, OCR, Three.js).

---

## 5. Licensing & Attribution
- **Environment Reference**: "PC workstation" by Frida, Dina, and Jorkop licensed under CC-BY 4.0.
- **CertiNexus AI System**: Procedural 3D WebGL / React Three Fiber architecture developed natively for CertiNexus AI.
