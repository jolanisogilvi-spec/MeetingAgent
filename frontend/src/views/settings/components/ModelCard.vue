<template>
  <div class="model-card">
    <div class="card-header">
      <div>
        <h3 class="card-title">{{ title }}</h3>
        <div class="card-desc">{{ desc }}</div>
      </div>
      <slot name="header-extra" />
    </div>

    <div class="card-body">
      <slot />
    </div>

    <el-alert
      v-if="feedback"
      class="card-feedback"
      :type="feedback.type"
      :title="feedback.title"
      :description="feedback.description"
      :closable="feedback.closable"
      show-icon
    >
      <template v-if="feedback.extraSlot" #default>
        <slot name="feedback-extra" />
      </template>
    </el-alert>

    <div class="card-actions">
      <el-button
        type="primary"
        :icon="Check"
        :loading="saving"
        :disabled="testing"
        @click="$emit('save')"
      >
        保存
      </el-button>
      <el-button
        :icon="Connection"
        :loading="testing"
        :disabled="saving"
        @click="$emit('test')"
      >
        测试连接
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { Check, Connection } from '@element-plus/icons-vue'

defineProps({
  title: { type: String, required: true },
  desc: { type: String, default: '' },
  saving: { type: Boolean, default: false },
  testing: { type: Boolean, default: false },
  feedback: { type: Object, default: null }
})
defineEmits(['save', 'test'])
</script>

<style scoped>
.model-card {
  background: #ffffff;
  border: 1px solid rgba(212, 224, 234, 0.95);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: var(--shadow-soft);
  position: relative;
  overflow: hidden;
}

.model-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-teal));
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid rgba(216, 227, 234, 0.9);
  padding-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 800;
  margin: 0 0 4px;
  color: var(--color-text);
}

.card-desc {
  font-size: 12px;
  color: var(--color-text-muted);
}

.card-body {
  display: flex;
  flex-direction: column;
}

.card-feedback {
  margin-top: -8px;
  border-radius: 8px;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 2px;
}
</style>
