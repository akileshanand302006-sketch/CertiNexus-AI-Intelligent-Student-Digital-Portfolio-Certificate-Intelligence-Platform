/**
 * CertiNexus AI — Floating Intelligent Certificate & Career Chatbot
 * Answers questions about uploaded certificates, extracts skills, and provides career suggestions.
 */

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare, X, Send, Sparkles, Award, RotateCcw,
  Bot, User, ChevronDown, Minimize2, ExternalLink
} from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import api from '../../lib/api.js'
import { useAuth } from '../../lib/auth.jsx'

export default function AIChatbot() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()



  const [isOpen, setIsOpen] = useState(false)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState([])
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    'What skills have I demonstrated across my certificates?',
    'Suggest certifications I should pursue next',
    'Summarize my certificates by category and issuer',
  ])
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 200)
      if (messages.length === 0) {
        // Fetch initial suggestions
        api.getChatSuggestions()
          .then((res) => {
            if (res?.suggestions) setSuggestedQuestions(res.suggestions)
            setMessages([
              {
                sender: 'bot',
                text: res?.welcome || `Hello ${user?.full_name || user?.username || 'there'}! I am your CertiNexus AI Assistant. Ask me anything about your uploaded certificates or request career recommendations.`,
                referenced: [],
              },
            ])
          })
          .catch(() => {
            setMessages([
              {
                sender: 'bot',
                text: `Hello ${user?.full_name || user?.username || 'there'}! I am your CertiNexus AI Assistant. Ask me anything about your certificates, verified skills, or career next steps.`,
                referenced: [],
              },
            ])
          })
      }
    }
  }, [isOpen])

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
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: "I couldn't process that request right now. Please verify your connection or try rephrasing your question.",
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
        text: 'Chat history cleared. How can I assist you with your certificates and skills today?',
        referenced: [],
      },
    ])
  }

  const renderFormattedText = (text) => {
    // Quick simple markdown renderer for bold, lists, and line breaks
    const lines = text.split('\n')
    return lines.map((line, idx) => {
      if (line.startsWith('### ')) {
        return (
          <h4 key={idx} style={{ fontSize: '0.95rem', fontWeight: 700, margin: '8px 0 4px', color: 'var(--brand-ice)' }}>
            {line.replace('### ', '')}
          </h4>
        )
      }
      if (line.startsWith('• ') || line.startsWith('- ')) {
        const content = line.substring(2)
        return (
          <div key={idx} style={{ display: 'flex', gap: '6px', margin: '3px 0', alignItems: 'flex-start' }}>
            <span style={{ color: 'var(--brand-ice)', lineHeight: 1.4 }}>•</span>
            <span style={{ flex: 1 }} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(content) }} />
          </div>
        )
      }
      if (line.trim() === '---') {
        return <hr key={idx} style={{ border: 'none', borderTop: '1px solid var(--glass-border)', margin: '8px 0' }} />
      }
      if (!line.trim()) {
        return <div key={idx} style={{ height: '6px' }} />
      }
      return (
        <p key={idx} style={{ margin: '3px 0' }} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(line) }} />
      )
    })
  }

  const formatInlineMarkdown = (str) => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
  }

  // Do not render floating widget on dedicated AI Assistant tab
  if (location.pathname === '/assistant') return null

  return (
    <>
      {/* Floating Launcher Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            style={{
              position: 'fixed',
              bottom: 28,
              right: 28,
              zIndex: 9999,
            }}
          >
            <button
              onClick={() => setIsOpen(true)}
              className="btn-liquid btn-liquid-primary"
              style={{
                borderRadius: '50px',
                padding: '12px 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                boxShadow: '0 8px 32px rgba(6, 182, 212, 0.35)',
                border: '1px solid rgba(56, 189, 248, 0.4)',
                cursor: 'pointer',
              }}
              title="Open CertiNexus AI Assistant"
            >
              <div style={{ position: 'relative' }}>
                <Bot size={20} />
                <span className="status-beacon" style={{ position: 'absolute', top: -3, right: -3, width: 8, height: 8 }} />
              </div>
              <span style={{ fontWeight: 700, fontSize: '0.88rem', letterSpacing: '0.02em' }}>
                AI Assistant
              </span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Chatbot Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.92 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.92 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
            className="glass-panel"
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              width: 'min(440px, calc(100vw - 32px))',
              height: 'min(620px, calc(100vh - 48px))',
              zIndex: 99999,
              display: 'flex',
              flexDirection: 'column',
              borderRadius: '28px',
              overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.45), 0 0 40px rgba(56, 189, 248, 0.15)',
              border: '1px solid var(--glass-border-light)',
              background: 'var(--glass-elevated)',
              backdropFilter: 'blur(30px)',
              WebkitBackdropFilter: 'blur(30px)',
            }}
          >
            {/* Header */}
            <div
              style={{
                padding: '16px 20px',
                borderBottom: '1px solid var(--glass-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'rgba(255, 255, 255, 0.03)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, var(--brand-cyan), var(--brand-blue))',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    boxShadow: '0 2px 10px rgba(56, 189, 248, 0.3)',
                  }}
                >
                  <Sparkles size={18} />
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-primary)' }}>
                      CertiNexus AI
                    </span>
                    <span className="nav-brand-badge" style={{ fontSize: '0.62rem', padding: '1px 6px' }}>
                      ASSISTANT
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: 'var(--brand-ice)' }}>
                    Certificate Intelligence & Career Guide
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <button
                  onClick={handleClear}
                  className="icon-action-btn"
                  title="Clear conversation"
                  style={{ width: 30, height: 30 }}
                >
                  <RotateCcw size={14} />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="icon-action-btn"
                  title="Close chat"
                  style={{ width: 30, height: 30 }}
                >
                  <X size={15} />
                </button>
              </div>
            </div>

            {/* Messages Scroll Area */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '18px',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px',
              }}
            >
              {messages.map((m, idx) => {
                const isUser = m.sender === 'user'
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.18 }}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: isUser ? 'flex-end' : 'flex-start',
                      maxWidth: '100%',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '88%',
                        padding: '12px 16px',
                        borderRadius: isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                        background: isUser
                          ? 'linear-gradient(135deg, var(--brand-cyan), var(--brand-blue))'
                          : 'rgba(255, 255, 255, 0.05)',
                        border: isUser ? 'none' : '1px solid var(--glass-border)',
                        color: isUser ? '#ffffff' : 'var(--text-primary)',
                        fontSize: '0.86rem',
                        lineHeight: 1.55,
                        boxShadow: isUser
                          ? '0 4px 16px rgba(6, 182, 212, 0.25)'
                          : '0 2px 10px rgba(0, 0, 0, 0.1)',
                      }}
                    >
                      {isUser ? m.text : renderFormattedText(m.text)}
                    </div>

                    {/* Referenced certificate pills if any */}
                    {!isUser && m.referenced && m.referenced.length > 0 && (
                      <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '6px', maxWidth: '88%' }}>
                        {m.referenced.map((rc) => (
                          <div
                            key={rc.id}
                            onClick={() => {
                              setIsOpen(false)
                              navigate(`/certificates/${rc.id}`)
                            }}
                            className="glass-pill"
                            style={{
                              fontSize: '0.72rem',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '4px 8px',
                            }}
                            title="View certificate details"
                          >
                            <Award size={12} style={{ color: 'var(--brand-ice)' }} />
                            <span style={{ maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {rc.title}
                            </span>
                            <ExternalLink size={10} style={{ color: 'var(--text-muted)' }} />
                          </div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )
              })}

              {/* Bot Typing Indicator */}
              {loading && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{
                    alignSelf: 'flex-start',
                    padding: '10px 16px',
                    borderRadius: '16px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--glass-border)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--brand-ice)', animation: 'pulse 1s infinite' }} />
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--brand-cyan)', animation: 'pulse 1s infinite 0.2s' }} />
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--brand-blue)', animation: 'pulse 1s infinite 0.4s' }} />
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '4px' }}>
                    Consulting your certificate vault...
                  </span>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestion Chips */}
            {suggestedQuestions.length > 0 && (
              <div
                style={{
                  padding: '8px 16px',
                  borderTop: '1px solid var(--glass-border)',
                  background: 'rgba(0, 0, 0, 0.08)',
                  display: 'flex',
                  gap: '6px',
                  overflowX: 'auto',
                  scrollbarWidth: 'none',
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
                      fontSize: '0.74rem',
                      whiteSpace: 'nowrap',
                      padding: '5px 12px',
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
                padding: '12px 16px',
                borderTop: '1px solid var(--glass-border)',
                background: 'rgba(255, 255, 255, 0.02)',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
              }}
            >
              <input
                ref={inputRef}
                type="text"
                placeholder="Ask about your certificates, skills, or career..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
                className="glass-input-spatial"
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  fontSize: '0.84rem',
                  borderRadius: '16px',
                }}
              />

              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="btn-liquid btn-liquid-primary"
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: '14px',
                  padding: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  opacity: !input.trim() || loading ? 0.4 : 1,
                  cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
                }}
                title="Send message"
              >
                <Send size={16} />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
