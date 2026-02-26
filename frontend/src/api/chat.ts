import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface ChatRequest {
  message: string
  history: Array<{ role: string; content: string }>
}

export interface ChatStreamChunk {
  type: 'thought' | 'tool_call' | 'tool_result' | 'final_answer' | 'done'
  content?: string
  tool_name?: string
  tool_input?: any
  tool_output?: any
}

export async function* streamChat(message: string, history: Array<{ role: string; content: string }>) {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message, history })
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  if (!reader) {
    throw new Error('Response body is not readable')
  }

  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.trim() === '') continue
      if (line.startsWith('data: ')) {
        const data = line.slice(6)
        try {
          const chunk: ChatStreamChunk = JSON.parse(data)
          yield chunk
        } catch (e) {
          console.error('Failed to parse chunk:', data, e)
        }
      }
    }
  }
}

export default api
