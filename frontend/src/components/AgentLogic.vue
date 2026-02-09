<template>
  <div class="agent-logic">
    <div class="agent-logic-content">
      <div
        v-for="(step, index) in agentSteps"
        :key="index"
        :class="['agent-step', `step-${step.type}`]"
      >
        <div v-if="step.type === 'thought'" class="thought-content">
          <div v-if="step.content" class="thought-text">{{ step.content }}</div>
        </div>
        
        <div v-else-if="step.type === 'tool_call'" class="tool-section">
          <div 
            class="tool-header" 
            @click="toggleTool(index)"
          >
            <div class="tool-info">
              <span class="tool-icon">{{ getToolIcon(index) }}</span>
              <span class="tool-name">{{ step.toolName }}</span>
            </div>
            <span class="expand-icon">{{ expandedTools[index] ? '▼' : '▶' }}</span>
          </div>
          <div v-if="expandedTools[index]" class="tool-details">
            <div v-if="step.toolInput" class="step-input">
              <strong>入参:</strong> <pre>{{ formatJson(step.toolInput) }}</pre>
            </div>
            <div v-if="getToolResult(index)" class="step-output">
              <strong>返回:</strong> <pre>{{ formatJson(getToolResult(index)) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { AgentStep } from '../types'

const props = defineProps<{
  agentSteps: AgentStep[]
}>()

const expandedTools = ref<Record<number, boolean>>({})

function toggleTool(index: number) {
  expandedTools.value[index] = !expandedTools.value[index]
}

function getToolIcon(index: number): string {
  if (hasToolResult(index)) {
    return '✅'
  }
  return '⏳'
}

function hasToolResult(index: number): boolean {
  return getToolResult(index) !== undefined
}

function getToolResult(index: number): any {
  const currentStep = props.agentSteps[index]
  if (currentStep.type !== 'tool_call') return undefined
  
  for (let i = index + 1; i < props.agentSteps.length; i++) {
    const nextStep = props.agentSteps[i]
    if (nextStep.type === 'tool_call') {
      break
    }
    if (nextStep.type === 'tool_result') {
      return nextStep.toolOutput
    }
  }
  return undefined
}

function formatJson(data: any): string {
  if (typeof data === 'string') {
    return data
  }
  return JSON.stringify(data, null, 2)
}
</script>

<style scoped>
.agent-logic {
  background: #fafafa;
  padding: 8px 12px;
}

.agent-logic-content {
  max-height: 400px;
  overflow-y: auto;
}

.agent-step {
  margin-bottom: 6px;
}

.agent-step:last-child {
  margin-bottom: 0;
}

.thought-content {
  padding: 8px 10px;
  background: white;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.thought-text {
  color: #303133;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.tool-section {
  background: white;
  border-radius: 4px;
  overflow: hidden;
  border-left: 3px solid #e6a23c;
}

.tool-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.tool-header:hover {
  background-color: #f5f7fa;
}

.tool-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tool-icon {
  font-size: 13px;
}

.tool-name {
  font-weight: 600;
  color: #303133;
  font-size: 12px;
}

.expand-icon {
  color: #909399;
  font-size: 11px;
  transition: transform 0.2s;
}

.tool-details {
  padding: 0 8px 8px 8px;
  border-top: 1px solid #e4e7ed;
}

.step-input,
.step-output {
  padding: 6px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 10px;
  margin-bottom: 6px;
}

.step-output {
  margin-bottom: 0;
}

.step-input strong {
  display: block;
  margin-bottom: 4px;
  color: #606266;
}

.step-input pre,
.step-output pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #303133;
}
</style>
