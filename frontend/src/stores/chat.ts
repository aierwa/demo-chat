import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message, AgentStep, ChatSession } from '../types'

export const useChatStore = defineStore('chat', () => {
  const currentSession = ref<ChatSession>({
    id: generateId(),
    messages: [],
    createdAt: Date.now()
  })

  const isLoading = ref(false)
  const currentInput = ref('')
  const currentAssistantMessageId = ref<string | null>(null)

  const hasMessages = computed(() => currentSession.value.messages.length > 0)

  function addUserMessage(content: string) {
    const message: Message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: Date.now()
    }
    currentSession.value.messages.push(message)
  }

  function createAssistantMessage() {
    const message: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      agentSteps: []
    }
    currentSession.value.messages.push(message)
    currentAssistantMessageId.value = message.id
    return message.id
  }

  function addAgentStep(step: Omit<AgentStep, 'timestamp'>) {
    if (!currentAssistantMessageId.value) return
    
    const message = currentSession.value.messages.find(m => m.id === currentAssistantMessageId.value)
    if (message && message.agentSteps) {
      const agentStep: AgentStep = {
        ...step,
        timestamp: Date.now()
      }
      message.agentSteps.push(agentStep)
    }
  }

  function updateFinalAnswer(content: string) {
    if (!currentAssistantMessageId.value) return
    
    const message = currentSession.value.messages.find(m => m.id === currentAssistantMessageId.value)
    if (message) {
      message.content = content
    }
  }

  function clearSession() {
    currentSession.value = {
      id: generateId(),
      messages: [],
      createdAt: Date.now()
    }
    currentInput.value = ''
    currentAssistantMessageId.value = null
  }

  function generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  return {
    currentSession,
    isLoading,
    currentInput,
    hasMessages,
    addUserMessage,
    createAssistantMessage,
    addAgentStep,
    updateFinalAnswer,
    clearSession
  }
})
