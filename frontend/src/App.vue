<template>
  <div class="app">
    <div class="app-content">
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎使用 AI 助手</h1>
        <p class="welcome-subtitle">智能对话，实时展示 Agent 思考过程</p>
      </div>
    </div>

    <el-button
      class="chat-toggle-btn"
      type="primary"
      :icon="chatVisible ? Close : ChatDotRound"
      circle
      size="large"
      @click="toggleChat"
    />

    <el-dialog
      v-model="chatVisible"
      title=""
      :show-close="false"
      width="900px"
      class="chat-dialog"
      :close-on-click-modal="false"
    >
      <ChatWindow />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Close, ChatDotRound } from '@element-plus/icons-vue'
import ChatWindow from './components/ChatWindow.vue'

const chatVisible = ref(false)

function toggleChat() {
  chatVisible.value = !chatVisible.value
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
</style>

<style scoped>
.app {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 20px;
}

.welcome-section {
  text-align: center;
  color: white;
}

.welcome-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.welcome-subtitle {
  font-size: 20px;
  opacity: 0.9;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.chat-toggle-btn {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 60px;
  height: 60px;
  font-size: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  transition: all 0.3s ease;
}

.chat-toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.4);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  gap: 16px;
}
</style>

<style>
.chat-dialog .el-dialog__header {
  padding: 0;
}

.chat-dialog .el-dialog__body {
  padding: 0;
}

.chat-dialog .el-dialog {
  border-radius: 12px;
  overflow: hidden;
}
</style>
