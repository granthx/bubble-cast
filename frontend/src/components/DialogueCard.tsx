import React from 'react'
import type { DialogueItem } from '../api/types'
import { VolumeX } from 'lucide-react'

interface DialogueCardProps {
  dialogue: DialogueItem
}

export const DialogueCard: React.FC<DialogueCardProps> = ({ dialogue }) => {
  return (
    <article className="balloon-card" style={{ borderLeftColor: dialogue.color }}>
      <header className="balloon-card-header">
        <span
          className="spk-badge"
          style={{
            color: dialogue.color,
            backgroundColor: dialogue.bg,
            border: `1px solid ${dialogue.border}`,
          }}
        >
          <span>{dialogue.icon}</span>
          <span>
            {dialogue.speaker} · {dialogue.speaker_name}
          </span>
        </span>

        <span className="order-badge">#{dialogue.order_index}</span>
      </header>
      <p className="dialogue-text">"{dialogue.text}"</p>
    </article>
  )
}

export const SilentPage: React.FC = () => {
  return (
    <div className="silent-page" role="status">
      <VolumeX className="silent-icon" size={32} />
      <div className="silent-title">Silent Page</div>
      <p className="silent-desc">
        No spoken dialogue or narration panel detected on this page.
      </p>
    </div>
  )
}
