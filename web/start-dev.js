/**
 * CertiNexus AI — Unified Development Server
 * Automatically starts FastAPI backend (port 8000) and Vite frontend (port 5173).
 */

import { spawn } from 'node:child_process'
import http from 'node:http'
import path from 'node:path'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.resolve(__dirname, '..')

// Find python executable in venv
function getPythonPath() {
  const candidates = [
    path.join(projectRoot, 'venv', 'Scripts', 'python.exe'),
    path.join(__dirname, 'venv', 'Scripts', 'python.exe'),
    path.join(projectRoot, 'venv', 'bin', 'python'),
    'python',
    'py',
  ]
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate
    }
  }
  return 'python'
}

// Check if backend is alive
function checkBackendAlive() {
  return new Promise((resolve) => {
    const req = http.get('http://127.0.0.1:8000/api/health', (res) => {
      resolve(res.statusCode === 200 || res.statusCode === 204)
    })
    req.on('error', () => resolve(false))
    req.setTimeout(800, () => {
      req.destroy()
      resolve(false)
    })
  })
}

// Wait for backend to be ready
async function waitForBackend(maxAttempts = 20) {
  for (let i = 0; i < maxAttempts; i++) {
    const isAlive = await checkBackendAlive()
    if (isAlive) return true
    await new Promise((r) => setTimeout(r, 400))
  }
  return false
}

let backendProcess = null
let frontendProcess = null

function cleanup() {
  console.log('\n\x1b[33m[CertiNexus AI]\x1b[0m Shutting down development services...')
  if (backendProcess) {
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', backendProcess.pid.toString(), '/f', '/t'])
      } else {
        backendProcess.kill('SIGTERM')
      }
    } catch (_) {}
  }
  if (frontendProcess) {
    try {
      if (process.platform === 'win32') {
        spawn('taskkill', ['/pid', frontendProcess.pid.toString(), '/f', '/t'])
      } else {
        frontendProcess.kill('SIGTERM')
      }
    } catch (_) {}
  }
  process.exit(0)
}

process.on('SIGINT', cleanup)
process.on('SIGTERM', cleanup)
process.on('exit', cleanup)

async function main() {
  console.log('\x1b[36m╔════════════════════════════════════════════════════════════════╗\x1b[0m')
  console.log('\x1b[36m║   CertiNexus AI — Unified Development Environment              ║\x1b[0m')
  console.log('\x1b[36m╚════════════════════════════════════════════════════════════════╝\x1b[0m\n')

  const isAlreadyRunning = await checkBackendAlive()

  if (isAlreadyRunning) {
    console.log('\x1b[32m✔ [FastAPI]\x1b[0m Backend already active on http://127.0.0.1:8000')
  } else {
    const pythonExe = getPythonPath()
    console.log(`\x1b[34mℹ [FastAPI]\x1b[0m Starting backend server via ${pythonExe}...`)

    backendProcess = spawn(
      pythonExe,
      ['-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '127.0.0.1', '--port', '8000'],
      {
        cwd: projectRoot,
        stdio: 'inherit',
        shell: process.platform === 'win32',
      }
    )

    backendProcess.on('error', (err) => {
      console.error('\x1b[31m✖ [FastAPI Error]\x1b[0m', err.message)
    })

    const ready = await waitForBackend()
    if (ready) {
      console.log('\x1b[32m✔ [FastAPI]\x1b[0m Backend is ready on http://127.0.0.1:8000\n')
    } else {
      console.log('\x1b[33m⚠ [FastAPI]\x1b[0m Backend starting up in background...\n')
    }
  }

  // Start Vite frontend
  console.log('\x1b[35mℹ [Vite]\x1b[0m Starting React frontend...\n')
  const viteCmd = process.platform === 'win32' ? 'npx.cmd' : 'npx'
  frontendProcess = spawn(viteCmd, ['vite'], {
    cwd: __dirname,
    stdio: 'inherit',
    shell: process.platform === 'win32',
  })

  frontendProcess.on('exit', (code) => {
    cleanup()
  })
}

main().catch((err) => {
  console.error('[Fatal Error]', err)
  cleanup()
})
