/**
 * CertiNexus AI — Dedicated AI Assistant & Career Intelligence Page
 * Answers questions about uploaded certificates, tracks skills, and provides career suggestions.
 */

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bot, Send, Sparkles, Award, RotateCcw, ExternalLink,
  ChevronRight, Brain, Lightbulb, Compass, Zap
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'

export default function AIAssistant() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState([])
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    'What skills have I demonstrated across my certificates?',
    'Suggest certifications I should pursue next',
    'Summarize all my certificates by category and issuer',
    'What skill gaps should I address for a tech interview?',
  ])
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  useEffect(() => {
    // Load initial suggestions and welcome message
    api.getChatSuggestions()
      .then((res) => {
        if (res?.suggestions) setSuggestedQuestions(res.suggestions)
        setMessages([
          {
            sender: 'bot',
            text: res?.welcome || `Hello **${user?.full_name || user?.username || 'there'}**! I am your **CertiNexus AI Academic & Career Assistant**.\n\nI have indexed your uploaded certificates, validated skills, and credentials. Ask me any question about your achievements or request tailored career suggestions!`,
            referenced: [],
          },
        ])
      })
      .catch(() => {
        setMessages([
          {
            sender: 'bot',
            text: `Hello **${user?.full_name || user?.username || 'there'}**! I am your **CertiNexus AI Assistant**.\n\nAsk me anything about your uploaded certificates, verified skills, or career next steps.`,
            referenced: [],
          },
        ])
      })
    setTimeout(() => inputRef.current?.focus(), 150)
  }, [])

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim()
    if (!query || loading) return

    const newMessages = [...messages, { sender: 'user', text: query }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const history = newMessages.slice(-6).map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }))

      const res = await api.sendChatMessage(query, history)
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: res.reply,
          referenced: res.referenced_certificates || [],
        },
      ])
      if (res.suggested_questions && res.suggested_questions.length > 0) {
        setSuggestedQuestions(res.suggested_questions)
      }
    } catch (err) {
      console.error('AI chat error:', err)
      const detail = err?.message || 'Server communication error'
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `I couldn't process that query right now (${detail}). Please try again or ask another question about your certificates.`,
          referenced: [],
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setMessages([
      {
        sender: 'bot',
        text: 'Conversation history reset. How can I assist you with your certificates and skills today?',
        referenced: [],
      },
    ])
  }

  const renderFormattedText = (text) => {
    const lines = text.split('\n')
    return lines.map((line, idx) => {
      if (line.startsWith('### ')) {
        return (
          <h3 key={idx} style={{ fontSize: '1.05rem', fontWeight: 700, margin: '10px 0 6px', color: 'var(--brand-ice)' }}>
            {line.replace('### ', '')}
          </h3>
        )
      }
      if (line.startsWith('• ') || line.startsWith('- ')) {
        const content = line.substring(2)
        return (
          <div key={idx} style={{ display: 'flex', gap: '8px', margin: '4px 0', alignItems: 'flex-start' }}>
            <span style={{ color: 'var(--brand-ice)', lineHeight: 1.4 }}>•</span>
            <span style={{ flex: 1 }} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(content) }} />
          </div>
        )
      }
      if (line.trim() === '---') {
        return <hr key={idx} style={{ border: 'none', borderTop: '1px solid var(--glass-border)', margin: '10px 0' }} />
      }
      if (!line.trim()) {
        return <div key={idx} style={{ height: '8px' }} />
      }
      return (
        <p key={idx} style={{ margin: '4px 0' }} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(line) }} />
      )
    })
  }

  const formatInlineMarkdown = (str) => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code style="background: rgba(56,189,248,0.15); padding: 2px 6px; border-radius: 4px; font-size: 0.85em; color: var(--brand-ice);">$1</code>')
  }

  return (
    <div className="assistant-page-wrapper" style={{ maxWidth: 1100, width: '100%', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px', flexShrink: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
            <span className="status-beacon green" />
            <span style={{ fontSize: '0.74rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--brand-ice)' }}>
              Certificate Intelligence Assistant
            </span>
          </div>
          <h1 className="spatial-hero-title" style={{ fontSize: '1.45rem', margin: 0 }}>
            AI Academic & Career Advisor
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => navigate('/portfolio')}
            className="btn-liquid btn-liquid-ghost"
            style={{ padding: '8px 16px', fontSize: '0.84rem' }}
          >
            <Award size={15} />
            <span>View Portfolio</span>
          </button>
          <button
            onClick={handleClear}
            className="btn-liquid btn-liquid-ghost"
            style={{ padding: '8px 16px', fontSize: '0.84rem' }}
            title="Reset conversation"
          >
            <RotateCcw size={14} />
            <span>Clear Chat</span>
          </button>
        </div>
      </div>

      {/* Main Chat Panel */}
      <div
        className="glass-panel"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          borderRadius: '28px',
          overflow: 'hidden',
          minHeight: 0,
          background: 'var(--glass-elevated)',
        }}
      >
        {/* Messages Stream */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          {messages.map((m, idx) => {
            const isUser = m.sender === 'user'
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '100%',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-tertiary)', fontWeight: 600 }}>
                    {isUser ? (user?.full_name || user?.username || 'You') : 'CertiNexus AI'}
                  </span>
                </div>

                <div
                  style={{
                    maxWidth: '82%',
                    padding: '14px 20px',
                    borderRadius: isUser ? '24px 24px 4px 24px' : '24px 24px 24px 4px',
                    background: isUser
                      ? 'linear-gradient(135deg, var(--brand-cyan), var(--brand-blue))'
                      : 'rgba(255, 255, 255, 0.05)',
                    border: isUser ? 'none' : '1px solid var(--glass-border)',
                    color: isUser ? '#ffffff' : 'var(--text-primary)',
                    fontSize: '0.9rem',
                    lineHeight: 1.6,
                    boxShadow: isUser
                      ? '0 6px 20px rgba(6, 182, 212, 0.25)'
                      : '0 4px 16px rgba(0, 0, 0, 0.1)',
                  }}
                >
                  {isUser ? m.text : renderFormattedText(m.text)}
                </div>

                {/* Referenced Certificates Cards */}
                {!isUser && m.referenced && m.referenced.length > 0 && (
                  <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '8px', maxWidth: '82%' }}>
                    {m.referenced.map((rc) => (
                      <div
                        key={rc.id}
                        onClick={() => navigate(`/portfolio?certId=${rc.id}`)}
                        className="glass-pill"
                        style={{
                          fontSize: '0.76rem',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '6px 12px',
                          background: 'rgba(56, 189, 248, 0.1)',
                          borderColor: 'rgba(56, 189, 248, 0.3)',
                        }}
                        title="View certificate document in Portfolio"
                      >
                        <Award size={13} style={{ color: 'var(--brand-ice)' }} />
                        <span style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {rc.title}
                        </span>
                        <ExternalLink size={11} style={{ color: 'var(--text-muted)' }} />
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            )
          })}

          {/* Typing state */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                alignSelf: 'flex-start',
                padding: '12px 18px',
                borderRadius: '20px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--glass-border)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--brand-ice)', animation: 'pulse 1s infinite' }} />
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--brand-cyan)', animation: 'pulse 1s infinite 0.2s' }} />
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--brand-blue)', animation: 'pulse 1s infinite 0.4s' }} />
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginLeft: '6px' }}>
                Analyzing verified certificates & formulating career advice...
              </span>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Dynamic Suggested Inquiries */}
        {suggestedQuestions.length > 0 && (
          <div
            style={{
              padding: '6px 16px',
              borderTop: '1px solid var(--glass-border)',
              background: 'rgba(0, 0, 0, 0.1)',
              display: 'flex',
              gap: '8px',
              overflowX: 'auto',
              scrollbarWidth: 'none',
              flexShrink: 0,
            }}
          >
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(q)}
                disabled={loading}
                className="glass-pill"
                style={{
                  fontSize: '0.76rem',
                  whiteSpace: 'nowrap',
                  padding: '4px 12px',
                  cursor: 'pointer',
                  border: '1px solid var(--glass-border-light)',
                  color: 'var(--text-secondary)',
                  background: 'rgba(255, 255, 255, 0.04)',
                  transition: 'all 0.15s ease',
                  flexShrink: 0,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = 'var(--brand-ice)'
                  e.currentTarget.style.borderColor = 'var(--brand-ice)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = 'var(--text-secondary)'
                  e.currentTarget.style.borderColor = 'var(--glass-border-light)'
                }}
              >
                💡 {q}
              </button>
            ))}
          </div>
        )}

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          style={{
            padding: '8px 16px',
            borderTop: '1px solid var(--glass-border)',
            background: 'rgba(255, 255, 255, 0.02)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            flexShrink: 0,
          }}
        >
          <input
            ref={inputRef}
            type="text"
            placeholder="Ask about your certificates, demonstrated skills, or career suggestions..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="glass-input-spatial"
            style={{
              flex: 1,
              padding: '9px 16px',
              fontSize: '0.86rem',
              borderRadius: '16px',
            }}
          />

          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-liquid btn-liquid-primary"
            style={{
              padding: '9px 18px',
              borderRadius: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              flexShrink: 0,
              fontSize: '0.84rem',
              opacity: !input.trim() || loading ? 0.45 : 1,
              cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
            }}
          >
            <span>Ask AI</span>
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  )
}
