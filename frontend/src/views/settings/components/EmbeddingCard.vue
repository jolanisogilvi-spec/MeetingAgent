<template>
  <ModelCard
    title="Embedding"
    desc="用于知识库片段向量化与检索"
    :saving="saving"
    :testing="testing"
    :feedback="feedback"
    @save="onSave"
    @test="onTest"
  >
    <el-form :model="form" label-width="110px" label-position="right">
      <el-form-item label="API Key">
        <el-input
          v-model="form.api_key"
          type="password"
          show-password
          :placeholder="masked.api_key || '请输入 API Key'"
          autocomplete="new-password"
        />
        <div v-if="masked.api_key && !form.api_key" class="hint">
          已保存：{{ masked.api_key }}（留空则保持不变）
        </div>
      </el-form-item>
      <el-form-item label="Base URL">
        <el-input v-model="form.base_url" placeholder="例如：https://api.openai.com/v1" />
        <div class="hint">支持以 /v1 或 /v1/embeddings 结尾，后端会自动规范化</div>
      </el-form-item>
      <el-form-item label="模型 ID">
        <el-input v-model="form.model_name" placeholder="例如：text-embedding-3-small" />
      </el-form-item>
    </el-form>
  </ModelCard>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { settingsApi } from '@/api'
import ModelCard from './ModelCard.vue'

const props = defineProps({
  settings: { type: Object, default: null }
})
const emit = defineEmits(['saved'])

const saving = ref(false)
const testing = ref(false)
const feedback = ref(null)

const form = reactive({
  api_key: '',
  base_url: '',
  model_name: ''
})

const masked = reactive({
  api_key: ''
})

watch(
  () => props.settings,
  (s) => {
    if (!s) return
    masked.api_key = s.embedding_api_key || ''
    form.api_key = ''
    form.base_url = s.embedding_base_url || ''
    form.model_name = s.embedding_model_name || ''
  },
  { immediate: true }
)

function setFeedback(type, title, description = '') {
  feedback.value = { type, title, description, closable: false }
}

function buildPayload() {
  const payload = {
    embedding_base_url: form.base_url,
    embedding_model_name: form.model_name
  }
  if (form.api_key) payload.embedding_api_key = form.api_key
  return payload
}

async function onSave() {
  saving.value = true
  setFeedback('info', '保存中…')
  try {
    const res = await settingsApi.updateEmbedding(buildPayload())
    setFeedback('success', '保存成功', 'Embedding 配置已更新')
    emit('saved', res)
  } catch (e) {
    setFeedback('error', '保存失败', extractErr(e))
  } finally {
    saving.value = false
  }
}

async function onTest() {
  testing.value = true
  setFeedback('info', '测试中…', '正在调用 embedding 接口')
  try {
    const res = await settingsApi.testEmbedding(buildPayload())
    if (res?.ok) {
      const extra = res.extra || {}
      const lines = []
      if (extra.dim) lines.push(`向量维度：${extra.dim}`)
      if (extra.model) lines.push(`模型：${extra.model}`)
      setFeedback('success', `测试成功：${res.message || 'Embedding 可用'}`, lines.join('\n'))
    } else {
      setFeedback('error', '测试失败', res?.message || '未知错误')
    }
  } catch (e) {
    setFeedback('error', '测试失败', extractErr(e))
  } finally {
    testing.value = false
  }
}

function extractErr(e) {
  return e?.response?.data?.detail || e?.message || '请求失败'
}
</script>

<style scoped>
.hint {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
}
</style>
