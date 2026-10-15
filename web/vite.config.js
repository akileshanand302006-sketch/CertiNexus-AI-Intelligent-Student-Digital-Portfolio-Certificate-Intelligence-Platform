import { spawn } from 'node:child_process'
import http from 'node:http'
import path from 'node:path'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

function autoBackendPlugin() {
  let backendProc = null

  return {
    name: 'auto-backend-server',
    configureServer(server) {
      // Check if backend is alive
      const checkBackend = () => {
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

      checkBackend().then((isRunning) => {
        if (isRunning) {
          console.log('\x1b[32m✔ [Vite Auto-Backend]\x1b[0m FastAPI backend is active on http://127.0.0.1:8000')
          return
        }

        console.log('\x1b[36mℹ [Vite Auto-Backend]\x1b[0m Starting FastAPI backend on http://127.0.0.1:8000...')
        const projectRoot = path.resolve(__dirname, '..')
        const candidates = [
          path.join(projectRoot, 'venv', 'Scripts', 'python.exe'),
          path.join(__dirname, 'venv', 'Scripts', 'python.exe'),
          path.join(projectRoot, 'venv', 'bin', 'python'),
          'python',
          'py',
        ]
        const pythonPath = candidates.find((p) => fs.existsSync(p)) || 'python'

        try {
          backendProc = spawn(
            pythonPath,
            ['-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '127.0.0.1', '--port', '8000'],
            {
              cwd: projectRoot,
              stdio: 'inherit',
              shell: process.platform === 'win32',
            }
          )

          backendProc.on('error', (err) => {
            console.error('\x1b[31m✖ [Auto-Backend Error]\x1b[0m Could not start backend:', err.message)
          })

          const cleanup = () => {
            if (backendProc && !backendProc.killed) {
              try {
                if (process.platform === 'win32') {
                  spawn('taskkill', ['/pid', backendProc.pid.toString(), '/f', '/t'])
                } else {
                  backendProc.kill('SIGTERM')
                }
              } catch (_) {}
            }
          }

          process.on('exit', cleanup)
          process.on('SIGINT', cleanup)
          process.on('SIGTERM', cleanup)
        } catch (err) {
          console.error('[Vite Auto-Backend]', err)
        }
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), autoBackendPlugin()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
