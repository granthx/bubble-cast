import React, { useState } from 'react'
import { Header } from './components/Header'
import { Navigation } from './components/Navigation'
import type { TabKey } from './components/Navigation'
import { ReaderWorkspace } from './components/ReaderWorkspace'
import { MultilingualStudio } from './components/MultilingualStudio'
import { UploadWorkspace } from './components/UploadWorkspace'
import { ExportCenter } from './components/ExportCenter'
import './styles/global.css'
import './styles/app.css'

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('reader')

  return (
    <div className="app-shell">
      <main className="container">
        <Header />
        <Navigation activeTab={activeTab} onSelectTab={setActiveTab} />

        {activeTab === 'reader' && <ReaderWorkspace />}
        {activeTab === 'multilingual' && <MultilingualStudio />}
        {activeTab === 'upload' && <UploadWorkspace />}
        {activeTab === 'export' && <ExportCenter />}
      </main>
    </div>
  )
}

export default App
