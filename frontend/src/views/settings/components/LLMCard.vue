<template>
  <ModelCard
    title="大模型"
    desc="用于生成摘要、抽取结构化纪要和质检补全"
    :saving="saving"
    :testing="testing"
    :feedback="feedback"
    @save="onSave"
    @test="onTest"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" label-position="right">
      <el-form-item label="API Key" prop="api_key">
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
      <el-form-item label="Base URL" prop="base_url">
        <el-input v-model="form.base_url" placeholder="例如：https://api.deepseek.com/v1" />
      </el-form-item>
      <el-form-item label="模型 ID" prop="model_name">
        <el-input v-model="form.model_name" placeholder="例如：deepseek-chat" />
      </el-form-item>
      <el-form-item label="Temperature" prop="temperature">
        <el-input-number
          v-model="form.temperature"
          :min="0"
          :max="2"
          :step="0.1"
          :precision="2"
          style="width: 180px"
        />
      </el-form-item>
      <el-form-item label="Max Tokens" prop="max_tokens">
        <el-input-number
          v-model="form.max_tokens"
          :min="1"
          :max="32768"
          :step="128"
          style="width: 180px"
        />
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

const formRef = ref(null)
const saving = ref(false)
const testing = ref(false)
const feedback = ref(null)

const form = reactive({
  api_key: '',
  base_url: '',
  model_name: '',
  temperature: 0.3,
  max_tokens: 1024
})

const masked = reactive({
  api_key: ''
})

const rules = {
  base_url: [{ required: false }],
  model_name: [{ required: false }]
}

watch(
  () => props.settings,
  (s) => {
    if (!s) return
    masked.api_key = s.llm_api_key || ''
    form.api_key = ''
    form.base_url = s.llm_base_url || ''
    form.model_name = s.llm_model_name || ''
    form.temperature = typeof s.temperature === 'number' ? s.temperature : 0.3
    form.max_tokens = typeof s.max_tokens === 'number' ? s.max_tokens : 1024
  },
  { immediate: true }
)

function setFeedback(type, title, description = '') {
  feedback.value = { type, title, description, closable: false }
}

function buildPayload(includeKeyIfEmpty = false) {
  const payload = {
    llm_base_url: form.base_url,
    llm_model_name: form.model_name,
    temperature: form.temperature,
    max_tokens: form.max_tokens
  }
  if (form.api_key) {
    payload.llm_api_key = form.api_key
  } else if (includeKeyIfEmpty) {
    // 不传，使用后端已保存的
  }
  return payload
}

async function onSave() {
  saving.value = true
  setFeedback('info', '保存中…')
  try {
    const res = await settingsApi.updateLlm(buildPayload())
    setFeedback('success', '保存成功', '大模型配置已更新')
    emit('saved', res)
  } catch (e) {
    setFeedback('error', '保存失败', extractErr(e))
  } finally {
    saving.value = false
  }
}

async function onTest() {
  testing.value = true
  setFeedback('info', '测试中…', '正在向大模型发送测试请求')
  try {
    const res = await settingsApi.testLlm(buildPayload(true))
    if (res?.ok) {
      const extra = res.extra || {}
      const lines = []
      if (extra.model) lines.push(`模型：${extra.model}`)
      if (extra.reply) lines.push(`回复：${extra.reply}`)
      setFeedback('success', `测试成功：${res.message || '模型可用'}`, lines.join('\n'))
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
