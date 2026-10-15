export interface SourceOption {
  id: 'test' | 'dev'
  label: string
  count: number
  description: string
}

export interface SequenceSummary {
  sequence_id: string
  title: string
  display_label: string
  page_count: number
  total_lines: number
  speaker_count: number
  speakers: string[]
  has_images: boolean
}

export interface CharacterProfile {
  id: string
  normalized_id: string
  name: string
  description: string
  lines_count: number
  dialogue_share_pct: number
  color: string
  bg: string
  border: string
  icon: string
}

export interface DialogueItem {
  order_index: number
  speaker: string
  speaker_name: string
  color: string
  bg: string
  border: string
  icon: string
  text: string
}

export interface PageDetail {
  page_number: number
  image_url: string | null
  image_rel: string | null
  dialogues: DialogueItem[]
  is_silent: boolean
}

export interface SequenceDetail {
  sequence_id: string
  title: string
  source: 'test' | 'dev'
  total_lines: number
  speaker_count: number
  page_count: number
  characters: CharacterProfile[]
  pages: PageDetail[]
}

export interface TraditionDialogue {
  speaker: string
  speaker_name: string
  text: string
  trans?: string | null
}

export interface TraditionPage {
  page_number: number
  dialogues: TraditionDialogue[]
}

export interface ComicTradition {
  id: string
  title: string
  flag: string
  reading_flow: string
  language: string
  font_family: string
  description: string
  pages: TraditionPage[]
}

export interface AnalysisResult {
  sequence_id: string
  reading_flow: string
  language_mode: string
  page_count: number
  total_lines: number
  speakers: string[]
  pages: { speaker: string; text: string }[][]
  log: string[]
}

export interface HealthStatus {
  status: string
  service: string
  model: string
  test_sequences: number
  dev_sequences: number
  total_metadata: number
}
