import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { School, ChevronDown, Check, Search, X } from 'lucide-react'
import { INDIAN_INSTITUTIONS, searchInstitutions } from '../../data/indianUniversities.js'

export default function InstitutionSelect({ value, onChange, placeholder = 'Select your Indian College / University' }) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const containerRef = useRef(null)

  // Filtered options
  const filtered = searchInstitutions(searchTerm, 40)

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (inst) => {
    onChange(inst)
    setIsOpen(false)
    setSearchTerm('')
  }

  const handleClear = (e) => {
    e.stopPropagation()
    onChange('')
    setSearchTerm('')
  }

  return (
    <div ref={containerRef} style={{ position: 'relative', width: '100%' }}>
      {/* Selector Trigger Input */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="glass-input-spatial"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          padding: '10px 14px',
          userSelect: 'none',
          minHeight: '42px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', flex: 1 }}>
          <School size={15} style={{ color: value ? 'var(--brand-ice)' : 'var(--text-tertiary)', flexShrink: 0 }} />
          <span style={{
            fontSize: '0.84rem',
            color: value ? 'var(--text-primary)' : 'var(--text-muted)',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {value || placeholder}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
          {value && (
            <button
              type="button"
              onClick={handleClear}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '2px',
                display: 'flex',
                alignItems: 'center',
              }}
              title="Clear selection"
            >
              <X size={13} />
            </button>
          )}
          <ChevronDown
            size={14}
            style={{
              color: 'var(--text-muted)',
              transition: 'transform 0.2s',
              transform: isOpen ? 'rotate(180deg)' : 'none',
            }}
          />
        </div>
      </div>

      {/* Floating Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.98 }}
            transition={{ duration: 0.16 }}
            className="glass-panel"
            style={{
              position: 'absolute',
              top: 'calc(100% + 6px)',
              left: 0,
              right: 0,
              zIndex: 100,
              maxHeight: '280px',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: 'var(--glass-shadow-lg)',
              border: '1px solid var(--glass-border-light)',
              borderRadius: '16px',
              overflow: 'hidden',
              background: 'var(--glass-elevated)',
              backdropFilter: 'blur(24px)',
            }}
          >
            {/* Search filter input inside dropdown */}
            <div style={{ padding: '8px 10px', borderBottom: '1px solid var(--glass-border)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Search size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
              <input
                type="text"
                autoFocus
                placeholder="Search colleges across India (e.g. IIT, Anna, PSG, BITS)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--text-primary)',
                  fontSize: '0.82rem',
                }}
              />
            </div>

            {/* List options */}
            <div style={{ overflowY: 'auto', flex: 1, padding: '4px' }}>
              {filtered.length > 0 ? (
                filtered.map((inst) => {
                  const isSelected = value === inst
                  return (
                    <div
                      key={inst}
                      onClick={() => handleSelect(inst)}
                      style={{
                        padding: '8px 12px',
                        borderRadius: '10px',
                        cursor: 'pointer',
                        fontSize: '0.82rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '8px',
                        background: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                        color: isSelected ? 'var(--brand-ice)' : 'var(--text-primary)',
                        transition: 'background 0.15s',
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) e.currentTarget.style.background = 'var(--glass-hover)'
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) e.currentTarget.style.background = 'transparent'
                      }}
                    >
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {inst}
                      </span>
                      {isSelected && <Check size={14} style={{ color: 'var(--brand-ice)', flexShrink: 0 }} />}
                    </div>
                  )
                })
              ) : (
                <div style={{ padding: '12px', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
                  <div>No matching institutions found</div>
                  {searchTerm && (
                    <button
                      type="button"
                      onClick={() => handleSelect(searchTerm)}
                      style={{
                        marginTop: '6px',
                        background: 'rgba(56, 189, 248, 0.15)',
                        border: '1px solid var(--brand-ice)',
                        color: 'var(--brand-ice)',
                        borderRadius: '8px',
                        padding: '4px 10px',
                        fontSize: '0.78rem',
                        cursor: 'pointer',
                      }}
                    >
                      Use "{searchTerm}" as custom institution
                    </button>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
