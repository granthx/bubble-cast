import React from 'react'
import { BookOpen, Globe, UploadCloud, Download } from 'lucide-react'

export type TabKey = 'reader' | 'multilingual' | 'upload' | 'export'

interface NavigationProps {
  activeTab: TabKey
  onSelectTab: (tab: TabKey) => void
}

export const Navigation: React.FC<NavigationProps> = ({ activeTab, onSelectTab }) => {
  return (
    <nav className="nav-tabs" aria-label="Application Workspaces">
      <button
        type="button"
        className={`nav-tab ${activeTab === 'reader' ? 'active' : ''}`}
        onClick={() => onSelectTab('reader')}
        aria-selected={activeTab === 'reader'}
        role="tab"
      >
        <BookOpen size={16} />
        <span>Manga Reader & Dialogue Inspector</span>
      </button>

      <button
        type="button"
        className={`nav-tab ${activeTab === 'multilingual' ? 'active' : ''}`}
        onClick={() => onSelectTab('multilingual')}
        aria-selected={activeTab === 'multilingual'}
        role="tab"
      >
        <Globe size={16} />
        <span>Multilingual Comic Studio</span>
      </button>

      <button
        type="button"
        className={`nav-tab ${activeTab === 'upload' ? 'active' : ''}`}
        onClick={() => onSelectTab('upload')}
        aria-selected={activeTab === 'upload'}
        role="tab"
      >
        <UploadCloud size={16} />
        <span>Upload Any Manga</span>
      </button>

      <button
        type="button"
        className={`nav-tab ${activeTab === 'export' ? 'active' : ''}`}
        onClick={() => onSelectTab('export')}
        aria-selected={activeTab === 'export'}
        role="tab"
      >
        <Download size={16} />
        <span>Export Deliverables</span>
      </button>
    </nav>
  )
}
