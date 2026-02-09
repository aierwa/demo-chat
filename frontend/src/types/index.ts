export interface AgentStep {
  type: 'thought' | 'tool_call' | 'tool_result'
  content: string
  toolName?: string
  toolInput?: any
  toolOutput?: any
  timestamp: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  agentSteps?: AgentStep[]
}

export interface ChatSession {
  id: string
  messages: Message[]
  createdAt: number
}
