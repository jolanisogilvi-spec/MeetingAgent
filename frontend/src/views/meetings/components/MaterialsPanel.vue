<template>
  <div class="section-card materials-panel">
    <div class="card-head">
      <h3 class="section-title">会议材料</h3>
      <span class="hint">支持粘贴文本或上传音频/文档；可附加多份知识库参考资料</span>
    </div>
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="粘贴文本" name="text">
        <el-input
          v-model="text"
          type="textarea"
          :rows="10"
          placeholder="将会议原文粘贴到此处，可与上传文件二选一"
          maxlength="200000"
          show-word-limit
        />
        <div class="row-actions">
          <span class="hint">文本会作为会议原文，与 mp3/wav/txt/docx 文件二选一；若两者都填，文本优先。</span>
          <el-button :loading="savingText" :disabled="!text" type="primary" plain @click="onSaveText">
            保存为原文
          </el-button>
        </div>
      </el-tab-pane>

      <el-tab-pane label="会议文件" name="meeting_file">
        <el-upload
          drag
          :auto-upload="false"
          :multiple="false"
          :limit="1"
          :accept="meetingAccept"
          :file-list="meetingFileList"
          :on-change="onMeetingChange"
          :on-remove="onMeetingRemove"
          :on-exceed="onMeetingExceed"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖入或<em>点击选择</em>会议文件
          </div>
          <template #tip>
            <div class="upload-tip">支持 .mp3 / .wav（语音转写） / .txt / .docx，单文件 ≤ 50MB</div>
          </template>
        </el-upload>
      </el-tab-pane>

      <el-tab-pane label="知识库参考" name="kb_files">
        <el-upload
          drag
          :auto-upload="false"
          :multiple="true"
          :accept="kbAccept"
          :file-list="kbFileList"
          :on-change="onKbChange"
          :on-remove="onKbRemove"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖入或<em>点击选择</em>参考资料（可多选）
          </div>
          <template #tip>
            <div class="upload-tip">支持 .txt / .docx，参与 RAG 检索辅助生成</div>
          </template>
        </el-upload>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { meetingsApi } from '@/api'

const props = defineProps({
  meetingId: { type: String, required: true },
  rawText: { type: String, default: '' }
})
const emit = defineEmits(['updated', 'files-changed'])

const activeTab = ref('text')
const text = ref(props.rawText || '')
const savingText = ref(false)

const meetingFileList = ref([])
const kbFileList = ref([])
const meetingRawFile = ref(null)
const kbRawFiles = ref([])

const meetingAccept = '.mp3,.wav,.txt,.docx'
const kbAccept = '.txt,.docx'

watch(
  () => props.rawText,
  (v) => {
    text.value = v || ''
  }
)

function emitFiles() {
  emit('files-changed', {
    text: text.value || '',
    meetingFile: meetingRawFile.value,
    kbFiles: kbRawFiles.value.slice()
  })
}

watch(text, emitFiles)

function onMeetingChange(file) {
  meetingRawFile.value = file.raw || null
  meetingFileList.value = file.raw ? [file] : []
  emitFiles()
}
function onMeetingRemove() {
  meetingRawFile.value = null
  meetingFileList.value = []
  emitFiles()
}
function onMeetingExceed() {
  ElMessage.warning('会议文件仅支持单个，已自动替换')
}
function onKbChange(file, list) {
  kbFileList.value = list.slice()
  kbRawFiles.value = list.map((f) => f.raw).filter(Boolean)
  emitFiles()
}
function onKbRemove(file, list) {
  kbFileList.value = list.slice()
  kbRawFiles.value = list.map((f) => f.raw).filter(Boolean)
  emitFiles()
}

async function onSaveText() {
  savingText.value = true
  try {
    const meeting = await meetingsApi.update(props.meetingId, { raw_text: text.value })
    ElMessage.success('原文已保存')
    emit('updated', meeting)
  } finally {
    savingText.value = false
  }
}

defineExpose({
  reset() {
    meetingRawFile.value = null
    meetingFileList.value = []
    kbRawFiles.value = []
    kbFileList.value = []
  },
  getPayload() {
    return {
      text: text.value || '',
      meetingFile: meetingRawFile.value,
      kbFiles: kbRawFiles.value.slice()
    }
  }
})
</script>

<style scoped>
.materials-panel {
  width: 100%;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(216, 227, 234, 0.85);
}
.section-title {
  margin: 0;
  font-weight: 800;
}
.row-actions {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.hint {
  color: var(--color-text-muted);
  font-size: 12px;
}
.upload-tip {
  color: var(--color-text-muted);
  font-size: 12px;
  margin-top: 4px;
}

:deep(.el-upload-dragger) {
  border-color: #b9dbe8;
  background: linear-gradient(135deg, rgba(240, 249, 252, 0.78), rgba(255, 255, 255, 0.96));
  border-radius: var(--radius);
}

:deep(.el-upload-dragger:hover) {
  border-color: var(--color-cyan);
  background: rgba(237, 248, 252, 0.9);
}
</style>
