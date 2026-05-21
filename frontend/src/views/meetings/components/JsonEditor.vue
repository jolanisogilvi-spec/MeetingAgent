<template>
  <div class="json-editor">
    <div class="toolbar">
      <span class="hint">编辑结构化纪要 JSON；保存时会校验语法并刷新摘要与待办视图。</span>
      <div>
        <el-button size="small" @click="onFormat">格式化</el-button>
        <el-button size="small" type="primary" :loading="saving" @click="onSave">保存 JSON</el-button>
      </div>
    </div>
    <el-input
      v-model="text"
      type="textarea"
      :rows="18"
      spellcheck="false"
      class="json-textarea"
      placeholder="结构化纪要 JSON"
    />
    <el-alert
      v-if="errorMsg"
      :title="errorMsg"
      type="error"
      :closable="false"
      show-icon
      style="margin-top: 8px"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { meetingsApi } from '@/api'

const props = defineProps({
  meetingId: { type: String, required: true },
  meetingJson: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['saved'])

const text = ref('')
const saving = ref(false)
const errorMsg = ref('')

function stringify(obj) {
  try {
    return JSON.stringify(obj || {}, null, 2)
  } catch (e) {
    return ''
  }
}

watch(
  () => props.meetingJson,
  (v) => {
    text.value = stringify(v)
    errorMsg.value = ''
  },
  { immediate: true, deep: true }
)

function onFormat() {
  errorMsg.value = ''
  try {
    const obj = JSON.parse(text.value || '{}')
    text.value = JSON.stringify(obj, null, 2)
  } catch (e) {
    errorMsg.value = `JSON 格式错误：${e.message}`
  }
}

async function onSave() {
  errorMsg.value = ''
  let parsed
  try {
    parsed = JSON.parse(text.value || '{}')
  } catch (e) {
    errorMsg.value = `JSON 格式错误：${e.message}`
    return
  }
  if (typeof parsed !== 'object' || Array.isArray(parsed) || parsed === null) {
    errorMsg.value = 'JSON 顶层必须是对象'
    return
  }
  saving.value = true
  try {
    const meeting = await meetingsApi.update(props.meetingId, { meeting_json: parsed })
    ElMessage.success('JSON 已保存')
    emit('saved', meeting)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.json-editor {
  width: 100%;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 12px;
}
.hint {
  color: var(--color-text-muted);
  font-size: 12px;
}
.json-textarea :deep(textarea) {
  font-family: ui-monospace, "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
  font-size: 12.5px;
  line-height: 1.5;
}
</style>
