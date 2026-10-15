import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            width: '100%',
            padding: '24px',
            textAlign: 'center',
          }}
        >
          <div
            className="glass-panel"
            style={{
              maxWidth: 480,
              padding: '32px 24px',
              borderRadius: '24px',
              border: '1px solid var(--glass-border-accent)',
            }}
          >
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                background: 'rgba(244, 63, 94, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
              }}
            >
              <AlertTriangle size={24} style={{ color: 'var(--brand-rose)' }} />
            </div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
              View Temporarily Interrupted
            </h2>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
              CertiNexus AI encountered an interface rendering delay. Click below to instantly re-initialize this view.
            </p>
            <button
              onClick={this.handleReset}
              className="btn-liquid btn-liquid-primary"
              style={{ margin: '0 auto', padding: '8px 20px', fontSize: '0.85rem' }}
            >
              <RefreshCw size={15} />
              <span>Restore View</span>
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
