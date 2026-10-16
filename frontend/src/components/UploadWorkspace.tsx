import React, { useState, useRef } from 'react'
import { api } from '../api/client'
import type { AnalysisResult } from '../api/types'
import { UploadCloud, FileImage, Trash2, Zap, CheckCircle, AlertCircle } from 'lucide-react'

export const UploadWorkspace: React.FC = () => {
  const [readingFlow, setReadingFlow] = useState<string>('Japanese Manga (Right-to-Left, Top-to-Bottom)')
  const [languageMode, setLanguageMode] = useState<string>('Auto-Detect')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [previewUrls, setPreviewUrls] = useState<string[]>([])
  const [isDragActive, setIsDragActive] = useState<boolean>(false)
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false)
  const [progressStage, setProgressStage] = useState<string>('')
  const [progressPercent, setProgressPercent] = useState<number>(0)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFiles = (files: FileList | null) => {
    if (!files) return
    const validFiles: File[] = []
    const validUrls: string[] = []

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
      if (['.png', '.jpg', '.jpeg', '.webp'].includes(ext)) {
        if (validFiles.length + selectedFiles.length < 3) {
          validFiles.push(file)
          validUrls.push(URL.createObjectURL(file))
        }
      }
    }

    if (validFiles.length === 0 && files.length > 0) {
      setError('Please upload valid manga image files (.png, .jpg, .webp).')
      return
    }

    setError(null)
    setSelectedFiles((prev) => [...prev, ...validFiles].slice(0, 3))
    setPreviewUrls((prev) => [...prev, ...validUrls].slice(0, 3))
  }

  const removeFile = (index: number) => {
    URL.revokeObjectURL(previewUrls[index])
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
    setPreviewUrls((prev) => prev.filter((_, i) => i !== index))
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragActive(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleAnalyze = async () => {
    if (selectedFiles.length === 0) return

    setIsAnalyzing(true)
    setError(null)
    setResult(null)
    setProgressPercent(15)
    setProgressStage('Uploading pages to multimodal vision pipeline...')

    try {
      setTimeout(() => {
        setProgressPercent(45)
        setProgressStage('Detecting panel boundaries & speech bubble polygons...')
      }, 300)

      setTimeout(() => {
        setProgressPercent(75)
        setProgressStage('Transcribing text & clustering cross-page character identities...')
      }, 700)

      const res = await api.analyzeUpload(selectedFiles, readingFlow, languageMode)

      setProgressPercent(100)
      setProgressStage('Analysis complete!')
      setResult(res)
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please check backend server status.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="upload-container">
      <div className="multilingual-intro">
        <h2 className="section-title">Upload Custom Manga Pages</h2>
        <p className="section-desc">
          Upload 1 to 3 sequential manga pages (.png, .jpg, .webp) to run dialogue bubble extraction
          and track consistent character identities in reading order:
        </p>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Settings */}
      <div className="upload-options-row">
        <div className="control-group">
          <label htmlFor="flow-select" className="control-label">Reading Order Flow</label>
          <select
            id="flow-select"
            className="custom-select"
            value={readingFlow}
            onChange={(e) => setReadingFlow(e.target.value)}
          >
            <option value="Japanese Manga (Right-to-Left, Top-to-Bottom)">
              Japanese Manga (Right-to-Left, Top-to-Bottom)
            </option>
            <option value="Webtoon / Manhwa (Top-to-Bottom Vertical Scroll)">
              Webtoon / Manhwa (Top-to-Bottom Vertical Scroll)
            </option>
            <option value="Western Comic (Left-to-Right, Top-to-Bottom)">
              Western Comic (Left-to-Right, Top-to-Bottom)
            </option>
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="lang-select" className="control-label">Language Transcription Mode</label>
          <select
            id="lang-select"
            className="custom-select"
            value={languageMode}
            onChange={(e) => setLanguageMode(e.target.value)}
          >
            <option value="Auto-Detect">Auto-Detect</option>
            <option value="Japanese (日本語)">Japanese (日本語)</option>
            <option value="English">English</option>
            <option value="Korean (한국어)">Korean (한국어)</option>
            <option value="Chinese (中文)">Chinese (中文)</option>
          </select>
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <div
        className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragActive(true)
        }}
        onDragLeave={() => setIsDragActive(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".png,.jpg,.jpeg,.webp"
          multiple
          style={{ display: 'none' }}
          onChange={(e) => handleFiles(e.target.files)}
        />
        <UploadCloud className="dropzone-icon" size={44} />
        <div className="dropzone-title">
          Drag & drop up to 3 sequential manga pages here, or click to browse
        </div>
        <p className="dropzone-hint">
          Supported formats: PNG, JPG, JPEG, WEBP (Max 3 pages per sequence)
        </p>
      </div>

      {/* Thumbnail Previews */}
      {selectedFiles.length > 0 && (
        <div>
          <div className="artwork-header-pill" style={{ marginBottom: '12px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileImage size={15} /> Uploaded Pages Queue ({selectedFiles.length} of 3)
            </span>
            <span style={{ color: '#66d7a5' }}>Ready for Analysis</span>
          </div>

          <div className="preview-grid">
            {selectedFiles.map((file, idx) => (
              <div key={idx} className="preview-card">
                <img src={previewUrls[idx]} alt={file.name} className="preview-img" />
                <div className="preview-meta">
                  <span>Page {idx + 1}: {file.name.slice(0, 16)}</span>
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() => removeFile(idx)}
                    aria-label={`Remove Page ${idx + 1}`}
                  >
                    <Trash2 size={12} /> Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '18px' }}>
            <button
              type="button"
              className="btn-primary"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              <Zap size={16} />
              <span>{isAnalyzing ? 'Analyzing Sequence...' : 'Analyze Pages & Transcribe Dialogue'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Progress feedback */}
      {isAnalyzing && (
        <div className="progress-strip" role="status">
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', fontWeight: 600 }}>
            <span>{progressStage}</span>
            <span>{progressPercent}%</span>
          </div>
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }} />
          </div>
        </div>
      )}

      {/* Analysis Result */}
      {result && (
        <div style={{ marginTop: '20px' }}>
          <div className="summary-strip" style={{ borderColor: 'rgba(102, 215, 165, 0.4)' }}>
            <div className="summary-item">
              <span className="summary-label">RESULT STATUS</span>
              <span className="summary-value" style={{ color: '#66d7a5', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle size={15} /> Transcribed & Attributed
              </span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">TOTAL EXTRACTED LINES</span>
              <span className="summary-value">{result.total_lines} Lines</span>
            </div>

            <div className="summary-divider" />

            <div className="summary-item">
              <span className="summary-label">ACTIVE CAST</span>
              <span className="summary-value" style={{ color: '#64cce8' }}>
                {result.speakers.join(', ') || 'Silent'}
              </span>
            </div>
          </div>

          <div className="spread-grid" style={{ marginTop: '16px' }}>
            {result.pages.map((p, pIdx) => (
              <div key={pIdx} className="spread-page-col">
                <div className="artwork-header-pill">
                  <span>Page {pIdx + 1} Transcribed Dialogue</span>
                  <span>{p.length} lines</span>
                </div>

                <div className="balloon-stack">
                  {p.length === 0 ? (
                    <div className="silent-page">
                      <div className="silent-title">Silent Page</div>
                      <p className="silent-desc">No speech bubbles detected on Page {pIdx + 1}.</p>
                    </div>
                  ) : (
                    p.map((line, lIdx) => (
                      <article key={lIdx} className="balloon-card" style={{ borderLeftColor: '#60a5fa' }}>
                        <header className="balloon-card-header">
                          <span className="spk-badge" style={{ color: '#60a5fa', background: 'rgba(96,165,250,0.1)' }}>
                            {line.speaker}
                          </span>
                          <span className="order-badge">#{lIdx + 1}</span>
                        </header>
                        <p className="dialogue-text">"{line.text}"</p>
                      </article>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
