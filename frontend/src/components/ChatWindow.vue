<template>
  <div class="chat-window">
    <div class="chat-header">
      <span class="chat-title">AI 助手</span>
      <el-button
        type="danger"
        size="small"
        :icon="Delete"
        circle
        @click="handleClear"
      />
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div v-if="!hasMessages" class="empty-state">
        <div class="empty-icon">💬</div>
        <div class="empty-text">开始与 AI 助手对话</div>
      </div>

      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', `message-${message.role}`]"
      >
        <div class="message-avatar">
          <span v-if="message.role === 'user'">👤</span>
          <span v-else>🤖</span>
        </div>
        <div class="message-content">
          <div v-if="message.role === 'user'" class="message-text">{{ message.content }}</div>
          <div v-else class="assistant-message">
            <AgentLogic :agent-steps="message.agentSteps || []" />
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>

      <div v-if="isLoading" class="message message-assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="message-text typing">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input">
      <el-input
        v-model="inputValue"
        type="textarea"
        :rows="3"
        placeholder="输入您的问题..."
        :disabled="isLoading"
        @keydown.enter.ctrl="handleSend"
      />
      <div class="chat-actions">
        <span class="hint">Ctrl + Enter 发送</span>
        <el-button
          type="primary"
          :loading="isLoading"
          :disabled="!inputValue.trim()"
          @click="handleSend"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useChatStore } from '../stores/chat'
import { streamChat } from '../api/chat'
import AgentLogic from './AgentLogic.vue'

const chatStore = useChatStore()
const messagesContainer = ref<HTMLElement>()

const inputValue = computed({
  get: () => chatStore.currentInput,
  set: (value) => {
    chatStore.currentInput = value
  }
})

const messages = computed(() => chatStore.currentSession.messages)
const hasMessages = computed(() => chatStore.hasMessages)
const isLoading = computed(() => chatStore.isLoading)

async function handleSend() {
  const message = inputValue.value.trim()
  if (!message || isLoading.value) return

  chatStore.addUserMessage(message)
  inputValue.value = ''

  chatStore.isLoading = true
  chatStore.createAssistantMessage()

  try {
    const history = messages.value
      .slice(0, -2)
      .filter((m) => {
        if (m.role === 'user') return true
        if (m.role === 'assistant' && m.content) return true
        if (m.role === 'assistant' && m.agentSteps && m.agentSteps.length > 0) {
          return m.agentSteps.some(s => s.type === 'thought' && s.content)
        }
        return false
      })
      .map((m) => {
        if (m.role === 'user') {
          return { role: m.role, content: m.content }
        }
        if (m.content) {
          return { role: m.role, content: m.content }
        }
        const thoughts = m.agentSteps
          ?.filter(s => s.type === 'thought' && s.content)
          .map(s => s.content)
          .join('\n')
        return { role: m.role, content: thoughts || '' }
      })

    let finalAnswer = ''

    for await (const chunk of streamChat(message, history)) {
      if (chunk.type === 'thought') {
        chatStore.addAgentStep({
          type: 'thought',
          content: chunk.content || ''
        })
      } else if (chunk.type === 'tool_call') {
        chatStore.addAgentStep({
          type: 'tool_call',
          content: '',
          toolName: chunk.tool_name,
          toolInput: chunk.tool_input
        })
      } else if (chunk.type === 'tool_result') {
        chatStore.addAgentStep({
          type: 'tool_result',
          content: '',
          toolOutput: chunk.tool_output
        })
      } else if (chunk.type === 'final_answer') {
        if (chunk.content) {
          finalAnswer += chunk.content
          chatStore.updateFinalAnswer(finalAnswer)
        }
      } else if (chunk.type === 'done') {
        await scrollToBottom()
      }
    }
  } catch (error) {
    console.error('Chat error:', error)
    ElMessage.error('发送失败，请重试')
  } finally {
    chatStore.isLoading = false
    await scrollToBottom()
  }
}

function handleClear() {
  chatStore.clearSession()
}

function formatTime(timestamp: number): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(messages, () => {
  scrollToBottom()
}, { deep: true })
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-content {
  max-width: 70%;
}

.message-user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-user .message-text {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant-message {
  background: white;
  border-radius: 12px;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.assistant-message .message-text {
  padding: 12px 16px;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  color: #303133;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.assistant-message .agent-logic {
  border-top: 1px solid #e4e7ed;
  border-radius: 0;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  background: white;
}

.chat-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.hint {
  font-size: 12px;
  color: #909399;
}
</style>
