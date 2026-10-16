import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { ComicTradition } from '../api/types'
import { Globe, ChevronDown, CheckCircle, AlertCircle } from 'lucide-react'

export const MultilingualStudio: React.FC = () => {
  const [traditions, setTraditions] = useState<ComicTradition[]>([])
  const [selectedId, setSelectedId] = useState<string>('japanese_manga')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    api
      .getMultilingualTraditions()
      .then((data) => {
        if (!isMounted) return
        setTraditions(data)
        if (data.length > 0) {
          setSelectedId(data[0].id)
        }
      })
      .catch((err) => {
        if (!isMounted) return
        setError(err.message || 'Failed to load comic traditions')
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  const current = traditions.find((t) => t.id === selectedId) || traditions[0]

  return (
    <div className="multilingual-studio">
      <div className="multilingual-intro">
        <h2 className="section-title">Multilingual Comic Studio</h2>
        <p className="section-desc">
          Dialogue extraction and cross-page character identification adapted across four global comic traditions:
          <strong> Japanese Manga (日本語)</strong>, <strong>Korean Manhwa & Webtoons (한국어)</strong>, 
          <strong> Chinese Manhua (中文)</strong>, and <strong>English Comics</strong>.
        </p>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {loading && !current && (
        <div className="loading-box" role="status">
          <div className="spinner" />
          <p>Loading multilingual traditions...</p>
        </div>
      )}

      {current && (
        <>
          {/* Tradition Dropdown */}
          <div className="control-group" style={{ maxWidth: '520px', marginBottom: '20px' }}>
            <label htmlFor="tradition-select" className="control-label">
              Select Comic Tradition & Flow Architecture
            </label>
            <div className="select-wrapper">
              <select
                id="tradition-select"
                className="custom-select"
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
              >
                {traditions.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.flag} {t.title} — {t.reading_flow.split('·')[0]}
                  </option>
                ))}
              </select>
              <ChevronDown size={16} className="select-chevron" />
            </div>
          </div>

          {/* Architecture Summary Strip */}
          <div className="summary-strip" aria-label="Tradition Architecture Details">
            <div className="summary-item">
              <span className="summary-label">READING FLOW</span>
              <span className="summary-value" style={{ color: '#9182ff' }}>
                {current.reading_flow}
              </span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">TARGET LANGUAGE</span>
              <span className="summary-value">{current.language}</span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">NARRATIVE MEMORY</span>
              <span className="summary-value" style={{ color: '#66d7a5', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle size={14} /> Active Across All 3 Pages
              </span>
            </div>
          </div>

          {/* 3 Pages Grid */}
          <div className="multilingual-grid">
            {current.pages.map((p) => (
              <div key={p.page_number} className="spread-page-col">
                <div className="artwork-header-pill">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Globe size={14} /> Page {p.page_number} Dialogue
                  </span>
                  <span>{p.dialogues.length} speech lines</span>
                </div>

                <div className="balloon-stack">
                  {p.dialogues.map((d, dIdx) => (
                    <article
                      key={dIdx}
                      className="balloon-card"
                      style={{
                        borderLeftColor:
                          d.speaker === 'NARRATION' ? '#f4c56b' : d.speaker === 'char1' ? '#60a5fa' : '#f472b6',
                      }}
                    >
                      <header className="balloon-card-header">
                        <span
                          className="spk-badge"
                          style={{
                            color: d.speaker === 'NARRATION' ? '#f4c56b' : '#60a5fa',
                            backgroundColor: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid var(--border)',
                          }}
                        >
                          {d.speaker_name} ({d.speaker})
                        </span>
                        <span className="order-badge">#{dIdx + 1}</span>
                      </header>

                      {/* Native text with specific font */}
                      <p
                        className="dialogue-text"
                        style={{ fontFamily: current.font_family, fontSize: '1.02rem' }}
                      >
                        "{d.text}"
                      </p>

                      {/* English translation if available */}
                      {d.trans && (
                        <div className="dialogue-trans">
                          🇬🇧 "{d.trans}"
                        </div>
                      )}
                    </article>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
