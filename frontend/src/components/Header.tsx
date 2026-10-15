import React from 'react'
import { BookOpen, Sparkles, Layers, Compass, Globe, Zap } from 'lucide-react'

export const Header: React.FC = () => {
  return (
    <header className="studio-header">
      <div className="studio-brand">
        <div className="studio-logo" aria-label="Manga Speaker Logo">
          <BookOpen size={24} />
        </div>
        <div>
          <div className="studio-title-row">
            <h1 className="studio-title">Manga Speaker</h1>
            <span className="studio-badge">STUDIO</span>
          </div>
          <p className="studio-subtitle">
            Multimodal manga reading & dialogue intelligence engine
          </p>
        </div>
      </div>

      <div className="capability-chips" role="list" aria-label="Studio Capabilities">
        <span className="chip" role="listitem">
          <Layers size={14} color="#9182ff" /> 3-Page Narrative Memory
        </span>
        <span className="chip" role="listitem">
          <Sparkles size={14} color="#64cce8" /> Cross-Page Character Consistency
        </span>
        <span className="chip" role="listitem">
          <Compass size={14} color="#ff8b7d" /> Right-to-Left Panel Flow
        </span>
        <span className="chip" role="listitem">
          <Globe size={14} color="#66d7a5" /> Multilingual (EN · JA · KO · ZH)
        </span>
        <span className="chip" role="listitem">
          <Zap size={14} color="#f4c56b" /> Fine-Tuned 7B Vision Model
        </span>
      </div>
    </header>
  )
}
