import type {
  AnalysisResult,
  ComicTradition,
  HealthStatus,
  SequenceDetail,
  SequenceSummary,
  SourceOption,
} from './types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`
  const response = await fetch(url, options)

  if (!response.ok) {
    let errorDetail = response.statusText
    try {
      const errJson = await response.json()
      if (errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail)
      }
    } catch {
      // ignore
    }
    throw new Error(`API Error (${response.status}): ${errorDetail}`)
  }

  return response.json() as Promise<T>
}

export const api = {
  getHealth: () => request<HealthStatus>('/api/health'),

  getSources: () => request<SourceOption[]>('/api/sources'),

  getSequences: (source: 'test' | 'dev' = 'test') =>
    request<SequenceSummary[]>(`/api/sequences?source=${source}`),

  getSequenceDetail: (sequenceId: string, source: 'test' | 'dev' = 'test') =>
    request<SequenceDetail>(`/api/sequences/${encodeURIComponent(sequenceId)}?source=${source}`),

  getMultilingualTraditions: () =>
    request<ComicTradition[]>('/api/multilingual'),

  analyzeUpload: async (
    files: File[],
    readingFlow: string,
    languageMode: string
  ): Promise<AnalysisResult> => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    formData.append('reading_flow', readingFlow)
    formData.append('language_mode', languageMode)

    return request<AnalysisResult>('/api/analyze', {
      method: 'POST',
      body: formData,
    })
  },

  getDownloadPredictionsUrl: () => `${BASE_URL}/api/exports/predictions`,
  getDownloadReadmeUrl: () => `${BASE_URL}/api/exports/readme`,
  getDownloadSequenceJsonUrl: (sequenceId: string, source: 'test' | 'dev' = 'test') =>
    `${BASE_URL}/api/exports/sequence/${encodeURIComponent(sequenceId)}/json?source=${source}`,
  getDownloadSequenceScriptUrl: (sequenceId: string, source: 'test' | 'dev' = 'test') =>
    `${BASE_URL}/api/exports/sequence/${encodeURIComponent(sequenceId)}/script?source=${source}`,
}
