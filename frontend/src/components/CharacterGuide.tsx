import React, { useState } from 'react'
import type { CharacterProfile } from '../api/types'
import { ChevronDown, ChevronUp, Users, MessageSquare } from 'lucide-react'

interface CharacterGuideProps {
  characters: CharacterProfile[]
}

export const CharacterGuide: React.FC<CharacterGuideProps> = ({ characters }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false)

  if (!characters || characters.length === 0) {
    return null
  }

  return (
    <section className="character-guide" aria-label="Character Identification Guide">
      <button
        type="button"
        className="guide-toggle-btn"
        onClick={() => setIsExpanded((prev) => !prev)}
        aria-expanded={isExpanded}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Users size={18} color="#9182ff" />
          <span>Character Identification Guide (Editorial Cast & Visual Frame Mapping)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a2acc0' }}>
          <span style={{ fontSize: '0.78rem' }}>{characters.length} Active Speakers</span>
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {isExpanded && (
        <div className="cast-grid">
          {characters.map((char) => (
            <article key={char.id} className="cast-card">
              <div>
                <div className="cast-header">
                  <span
                    className="spk-badge"
                    style={{
                      color: char.color,
                      backgroundColor: char.bg,
                      border: `1px solid ${char.border}`,
                    }}
                  >
                    <span>{char.icon}</span>
                    <span>{char.id}</span>
                  </span>
                  <span style={{ fontSize: '0.72rem', color: '#a2acc0', fontWeight: 600 }}>
                    {char.dialogue_share_pct}% share
                  </span>
                </div>
                <h4 className="cast-name">{char.name}</h4>
                <p className="cast-desc">{char.description}</p>
              </div>

              <div className="cast-meta">
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <MessageSquare size={12} /> {char.lines_count} lines in chapter
                </span>
                <span style={{ color: char.color, fontWeight: 700 }}>Continuous ID</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
