import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { SequenceDetail, SequenceSummary } from '../api/types'
import { CharacterGuide } from './CharacterGuide'
import { DialogueCard, SilentPage } from './DialogueCard'
import { ChevronDown, Image as ImageIcon, MessageCircle, AlertCircle } from 'lucide-react'

export const ReaderWorkspace: React.FC = () => {
  const [source, setSource] = useState<'test' | 'dev'>('test')
  const [sequences, setSequences] = useState<SequenceSummary[]>([])
  const [selectedSeqId, setSelectedSeqId] = useState<string>('')
  const [sequenceDetail, setSequenceDetail] = useState<SequenceDetail | null>(null)
  const [viewMode, setViewMode] = useState<'side-by-side' | 'spread'>('side-by-side')
  const [activePageIndex, setActivePageIndex] = useState<number>(0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // 1. Fetch sequences when source changes
  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)

    api
      .getSequences(source)
      .then((data) => {
        if (!isMounted) return
        setSequences(data)
        if (data.length > 0) {
          // preserve selection if it exists in the new source, otherwise pick first
          const found = data.find((s) => s.sequence_id === selectedSeqId)
          setSelectedSeqId(found ? found.sequence_id : data[0].sequence_id)
        } else {
          setSelectedSeqId('')
          setSequenceDetail(null)
        }
      })
      .catch((err) => {
        if (!isMounted) return
        setError(err.message || 'Failed to fetch sequences')
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [source])

  // 2. Fetch sequence details when selectedSeqId or source changes
  useEffect(() => {
    if (!selectedSeqId) return

    let isMounted = true
    setLoading(true)
    setError(null)

    api
      .getSequenceDetail(selectedSeqId, source)
      .then((detail) => {
        if (!isMounted) return
        setSequenceDetail(detail)
        setActivePageIndex(0)
      })
      .catch((err) => {
        if (!isMounted) return
        setError(err.message || 'Failed to fetch sequence details')
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [selectedSeqId, source])

  return (
    <div className="reader-workspace">
      {/* Reader Toolbar */}
      <div className="reader-toolbar">
        {/* Source Selector */}
        <div className="control-group">
          <label className="control-label">Source Library</label>
          <div className="segmented-control" role="radiogroup" aria-label="Source Library">
            <button
              type="button"
              className={`segmented-btn ${source === 'test' ? 'active' : ''}`}
              onClick={() => setSource('test')}
              role="radio"
              aria-checked={source === 'test'}
            >
              Test Predictions (15)
            </button>
            <button
              type="button"
              className={`segmented-btn ${source === 'dev' ? 'active' : ''}`}
              onClick={() => setSource('dev')}
              role="radio"
              aria-checked={source === 'dev'}
            >
              Development Archive (80)
            </button>
          </div>
        </div>

        {/* Sequence Selector */}
        <div className="control-group">
          <label htmlFor="sequence-select" className="control-label">
            Manga Chapter Sequence
          </label>
          <div className="select-wrapper">
            <select
              id="sequence-select"
              className="custom-select"
              value={selectedSeqId}
              onChange={(e) => setSelectedSeqId(e.target.value)}
              disabled={sequences.length === 0}
            >
              {sequences.map((s) => (
                <option key={s.sequence_id} value={s.sequence_id}>
                  {s.display_label}
                </option>
              ))}
            </select>
            <ChevronDown size={16} className="select-chevron" />
          </div>
        </div>

        {/* Canvas View Switcher */}
        <div className="control-group">
          <label className="control-label">Canvas View Mode</label>
          <div className="segmented-control" role="radiogroup" aria-label="Canvas View Mode">
            <button
              type="button"
              className={`segmented-btn ${viewMode === 'side-by-side' ? 'active' : ''}`}
              onClick={() => setViewMode('side-by-side')}
              role="radio"
              aria-checked={viewMode === 'side-by-side'}
            >
              Side-by-Side (Focused)
            </button>
            <button
              type="button"
              className={`segmented-btn ${viewMode === 'spread' ? 'active' : ''}`}
              onClick={() => setViewMode('spread')}
              role="radio"
              aria-checked={viewMode === 'spread'}
            >
              All 3 Pages Spread
            </button>
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="error-banner" role="alert">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Loading state */}
      {loading && !sequenceDetail && (
        <div className="loading-box" role="status">
          <div className="spinner" />
          <p>Loading sequence artwork and dialogue attribution...</p>
        </div>
      )}

      {/* Sequence Details */}
      {sequenceDetail && (
        <>
          {/* Summary Strip */}
          <div className="summary-strip" aria-label="Sequence Summary">
            <div className="summary-item">
              <span className="summary-label">SEQUENCE ID</span>
              <span className="summary-value monospace">{sequenceDetail.sequence_id}</span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">SERIES & CHAPTER</span>
              <span className="summary-value" style={{ color: '#9182ff' }}>
                {sequenceDetail.title}
              </span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">PAGES</span>
              <span className="summary-value">{sequenceDetail.page_count} Pages</span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">TOTAL DIALOGUE</span>
              <span className="summary-value">{sequenceDetail.total_lines} Lines</span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">ACTIVE CAST</span>
              <span className="summary-value" style={{ color: '#64cce8' }}>
                {sequenceDetail.characters.length} Speakers (
                {sequenceDetail.characters.map((c) => c.name).join(', ') || 'Silent'})
              </span>
            </div>
          </div>

          {/* Character Guide */}
          <CharacterGuide characters={sequenceDetail.characters} />

          {/* Canvas View 1: Side-by-Side Mode */}
          {viewMode === 'side-by-side' && (
            <div>
              {/* Page Subtabs */}
              <div className="page-tabs-bar" role="tablist" aria-label="Page Selection">
                {sequenceDetail.pages.map((p, idx) => (
                  <button
                    key={p.page_number}
                    type="button"
                    className={`page-tab-btn ${activePageIndex === idx ? 'active' : ''}`}
                    onClick={() => setActivePageIndex(idx)}
                    role="tab"
                    aria-selected={activePageIndex === idx}
                  >
                    Page {p.page_number} ({p.dialogues.length} lines)
                  </button>
                ))}
              </div>

              {sequenceDetail.pages[activePageIndex] && (
                <div className="side-by-side-layout">
                  {/* Left Column: Artwork */}
                  <div className="artwork-container">
                    <div className="artwork-header-pill">
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <ImageIcon size={15} /> Page {activePageIndex + 1} of 3 Artwork
                      </span>
                      <span>Aspect Ratio Preserved</span>
                    </div>

                    <div className="manga-image-frame">
                      {sequenceDetail.pages[activePageIndex].image_url ? (
                        <img
                          src={sequenceDetail.pages[activePageIndex].image_url!}
                          alt={`Page ${activePageIndex + 1} Artwork`}
                          className="manga-image"
                          loading="lazy"
                        />
                      ) : (
                        <div style={{ padding: '60px 20px', color: '#a2acc0' }}>
                          Image file not available
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Column: Ordered Dialogue Balloons */}
                  <div className="dialogue-container">
                    <div className="dialogue-header-pill">
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <MessageCircle size={15} /> Extracted Speech Balloons (Reading Order)
                      </span>
                      <span>
                        {sequenceDetail.pages[activePageIndex].dialogues.length} Lines
                      </span>
                    </div>

                    {sequenceDetail.pages[activePageIndex].dialogues.length === 0 ? (
                      <SilentPage />
                    ) : (
                      <div className="balloon-stack">
                        {sequenceDetail.pages[activePageIndex].dialogues.map((item) => (
                          <DialogueCard key={item.order_index} dialogue={item} />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Canvas View 2: All 3 Pages Spread Mode */}
          {viewMode === 'spread' && (
            <div className="spread-grid" aria-label="Three Page Spread Layout">
              {sequenceDetail.pages.map((page) => (
                <div key={page.page_number} className="spread-page-col">
                  {/* Artwork Box */}
                  <div className="artwork-container">
                    <div className="artwork-header-pill">
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <ImageIcon size={14} /> Page {page.page_number}
                      </span>
                      <span>{page.dialogues.length} lines</span>
                    </div>

                    <div className="manga-image-frame">
                      {page.image_url ? (
                        <img
                          src={page.image_url}
                          alt={`Page ${page.page_number} Artwork`}
                          className="manga-image"
                          loading="lazy"
                        />
                      ) : (
                        <div style={{ padding: '40px 10px', color: '#a2acc0' }}>
                          No image
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Dialogue Stack under Page */}
                  {page.dialogues.length === 0 ? (
                    <SilentPage />
                  ) : (
                    <div className="balloon-stack">
                      {page.dialogues.map((item) => (
                        <DialogueCard key={item.order_index} dialogue={item} />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
