<template>
  <ModelCard
    title="语音模型"
    desc="用于音频文件转写为会议原文"
    :saving="saving"
    :testing="testing"
    :feedback="feedback"
    @save="onSave"
    @test="onTest"
  >
    <el-form :model="form" label-width="110px" label-position="right">
      <el-form-item label="模式">
        <el-radio-group v-model="form.provider" @change="onProviderChange">
          <el-radio-button value="local">本地</el-radio-button>
          <el-radio-button value="online">线上</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="语音模型类型">
        <el-input v-model="form.model_type" placeholder="例如：whisper" />
      </el-form-item>
      <el-form-item label="模型名称">
        <el-input
          v-model="form.model_name"
          :placeholder="form.provider === 'local' ? '例如：base、small、medium' : '线上模型名称'"
        />
      </el-form-item>
      <template v-if="form.provider === 'online'">
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
          <el-input v-model="form.base_url" placeholder="线上语音接口地址" />
        </el-form-item>
      </template>
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
  provider: 'local',
  model_type: 'whisper',
  model_name: '',
  api_key: '',
  base_url: ''
})

const masked = reactive({
  api_key: ''
})

watch(
  () => props.settings,
  (s) => {
    if (!s) return
    masked.api_key = s.speech_api_key || ''
    form.provider = s.speech_provider || 'local'
    form.model_type = s.speech_model_type || 'whisper'
    form.model_name = s.speech_model_name || ''
    form.api_key = ''
    form.base_url = s.speech_base_url || ''
  },
  { immediate: true }
)

function onProviderChange(val) {
  if (val === 'local') {
    form.api_key = ''
    form.base_url = ''
  }
}

function setFeedback(type, title, description = '') {
  feedback.value = { type, title, description, closable: false }
}

function buildPayload() {
  const payload = {
    speech_provider: form.provider,
    speech_model_type: form.model_type,
    speech_model_name: form.model_name
  }
  if (form.provider === 'online') {
    payload.speech_base_url = form.base_url
    if (form.api_key) payload.speech_api_key = form.api_key
  } else {
    payload.speech_api_key = ''
    payload.speech_base_url = ''
  }
  return payload
}

async function onSave() {
  saving.value = true
  setFeedback('info', '保存中…')
  try {
    const res = await settingsApi.updateSpeech(buildPayload())
    setFeedback('success', '保存成功', '语音模型配置已更新')
    emit('saved', res)
  } catch (e) {
    setFeedback('error', '保存失败', extractErr(e))
  } finally {
    saving.value = false
  }
}

async function onTest() {
  testing.value = true
  const tip =
    form.provider === 'local'
      ? '正在生成内置测试音频，并调用本地模型转写'
      : '正在生成内置测试音频，并上传到线上转写接口'
  setFeedback('info', '测试中…', tip)
  try {
    const res = await settingsApi.testSpeech(buildPayload())
    if (res?.ok) {
      const extra = res.extra || {}
      const lines = []
      if (extra.model) lines.push(`模型：${extra.model}`)
      if (extra.provider) lines.push(`模式：${extra.provider === 'local' ? '本地' : '线上'}`)
      if (extra.endpoint) lines.push(`接口：${extra.endpoint}`)
      if (typeof extra.stream === 'boolean') lines.push(`stream：${extra.stream ? 'true' : 'false'}`)
      lines.push(`转写结果：${extra.transcript || '接口已返回，测试音频未识别出明确文本'}`)
      setFeedback('success', `测试成功：${res.message || '语音模型可用'}`, lines.join('\n'))
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
