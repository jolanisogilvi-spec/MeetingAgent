<template>
  <div class="page meeting-detail" v-loading="loading && !meeting">
    <div class="page-header">
      <div>
        <div class="title-line">
          <el-button link :icon="ArrowLeft" @click="goBack">返回列表</el-button>
          <h2 class="page-title">{{ meeting?.title || '会议详情' }}</h2>
          <el-tag
            v-if="meeting"
            :type="statusTagType(meeting.status)"
            :effect="meeting.status === 'generating' ? 'dark' : 'light'"
            size="small"
          >
            {{ statusLabel(meeting.status) }}
          </el-tag>
        </div>
        <div class="page-subtitle">会议 ID: {{ meetingId }}</div>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" :loading="loading" @click="refresh">刷新</el-button>
        <el-button
          plain
          :icon="FolderOpened"
          :disabled="!meeting"
          @click="preparationVisible = true"
        >
          会前准备
        </el-button>
        <el-button
          type="success"
          plain
          :icon="CircleCheck"
          :loading="confirming"
          :disabled="!canConfirm"
          @click="onConfirm"
        >
          确认纪要
        </el-button>
        <el-button
          type="primary"
          plain
          :icon="Download"
          :loading="exporting"
          :disabled="!canExport"
          @click="onExport"
        >
          导出 Word
        </el-button>
      </div>
    </div>

    <template v-if="meeting">
      <BasicInfo
        :meeting="meeting"
        :departments="departmentsStore.list"
        @edit="editVisible = true"
      />

      <ParticipantsList
        :participant-ids="meeting.participant_ids"
        :people="peopleStore.list"
        :departments="departmentsStore.list"
      />

      <MaterialsPanel
        ref="materialsRef"
        :meeting-id="meeting.id"
        :raw-text="meeting.raw_text || ''"
        @updated="onMeetingUpdated"
        @files-changed="onFilesChanged"
      />

      <div class="generate-bar section-card">
        <div class="gen-info">
          <h3 class="section-title">生成会议纪要</h3>
          <div class="gen-desc">
            提交后系统会按"原文准备 → 知识库向量化 → 摘要 → 结构化 → 质检"流程生成结果。
            已粘贴文本或上传文件中只要任一就绪即可。
          </div>
        </div>
        <el-button
          type="primary"
          size="large"
          :icon="MagicStick"
          :loading="generating"
          :disabled="generating || meeting.status === 'generating'"
          @click="onGenerate"
        >
          {{ generating || meeting.status === 'generating' ? '生成中…' : '生成会议纪要' }}
        </el-button>
      </div>

      <ResultTabs
        v-model:active-tab="activeTab"
        :meeting="meeting"
        :tasks="meetingTasks"
        :tasks-loading="tasksLoading"
        @updated="onMeetingUpdated"
        @refresh-tasks="refreshTasks"
      />

      <CreateMeetingDialog
        v-model="editVisible"
        :departments="departmentsStore.list"
        :people="peopleStore.list"
        :meeting="meeting"
        @updated="onMeetingUpdated"
      />

      <PreparationDrawer
        v-model="preparationVisible"
        :meeting="meeting"
        :people="peopleStore.list"
      />
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  CircleCheck,
  Download,
  FolderOpened,
  MagicStick,
  Refresh
} from '@element-plus/icons-vue'
import BasicInfo from './components/BasicInfo.vue'
import ParticipantsList from './components/ParticipantsList.vue'
import MaterialsPanel from './components/MaterialsPanel.vue'
import ResultTabs from './components/ResultTabs.vue'
import CreateMeetingDialog from './components/CreateMeetingDialog.vue'
import PreparationDrawer from './components/PreparationDrawer.vue'
import { meetingsApi, tasksApi } from '@/api'
import { useDepartmentsStore } from '@/stores/departments'
import { usePeopleStore } from '@/stores/people'

const route = useRoute()
const router = useRouter()
const departmentsStore = useDepartmentsStore()
const peopleStore = usePeopleStore()

const meetingId = computed(() => route.params.id)
const meeting = ref(null)
const loading = ref(false)
const generating = ref(false)
const exporting = ref(false)
const confirming = ref(false)
const editVisible = ref(false)
const preparationVisible = ref(false)
const activeTab = ref('summary')

const meetingFile = ref(null)
const kbFiles = ref([])
const materialsRef = ref(null)

const meetingTasks = ref([])
const tasksLoading = ref(false)
const pollTimer = ref(null)

const canExport = computed(() => {
  if (!meeting.value) return false
  return meeting.value.status === 'completed' || meeting.value.status === 'confirmed'
})

const canConfirm = computed(() => {
  if (!meeting.value) return false
  return meeting.value.status === 'completed'
})

function goBack() {
  router.push('/meetings')
}

async function refresh() {
  loading.value = true
  try {
    const [m] = await Promise.all([
      meetingsApi.get(meetingId.value),
      departmentsStore.list.length ? Promise.resolve() : departmentsStore.refresh(),
      peopleStore.list.length ? Promise.resolve() : peopleStore.refresh()
    ])
    meeting.value = m
    syncGenerationPolling()
    await refreshTasks()
  } finally {
    loading.value = false
  }
}

async function refreshTasks() {
  tasksLoading.value = true
  try {
    const res = await tasksApi.list({ meeting_id: meetingId.value })
    meetingTasks.value = Array.isArray(res) ? res : []
  } finally {
    tasksLoading.value = false
  }
}

function onMeetingUpdated(updated) {
  if (updated) {
    meeting.value = updated
    syncGenerationPolling()
  }
}

function onFilesChanged(payload) {
  meetingFile.value = payload?.meetingFile || null
  kbFiles.value = Array.isArray(payload?.kbFiles) ? payload.kbFiles.slice() : []
  if (typeof payload?.text === 'string' && meeting.value) {
    // 不直接覆盖 meeting.raw_text（避免与服务端 raw_text 状态混淆），
    // 用单独的 pendingText 缓存
    pendingText.value = payload.text
  }
}

const pendingText = ref('')

async function onGenerate() {
  if (!meeting.value) return
  const payload = materialsRef.value?.getPayload() || {
    text: pendingText.value || meeting.value.raw_text || '',
    meetingFile: meetingFile.value,
    kbFiles: kbFiles.value
  }
  const text = (payload.text || '').trim()
  if (!text && !payload.meetingFile) {
    ElMessage.warning('请先粘贴会议文本或上传会议文件')
    return
  }
  const formData = new FormData()
  if (text) formData.append('meeting_text', payload.text)
  if (payload.meetingFile) {
    formData.append('meeting_file', payload.meetingFile)
  }
  if (Array.isArray(payload.kbFiles)) {
    for (const f of payload.kbFiles) {
      if (f) formData.append('kb_files', f)
    }
  }

  generating.value = true
  try {
    const updated = await meetingsApi.generate(meetingId.value, formData)
    meeting.value = updated
    syncGenerationPolling()
    if (updated?.status === 'generating') {
      ElMessage.info('会议纪要已开始生成，可先浏览其他页面')
      materialsRef.value?.reset?.()
    } else if (updated?.status === 'failed') {
      ElMessage.error(updated.error_message || '生成失败')
    } else {
      ElMessage.success('会议纪要已生成')
      activeTab.value = 'summary'
      materialsRef.value?.reset?.()
      await refreshTasks()
    }
  } catch (e) {
    await refresh().catch(() => {})
  } finally {
    generating.value = false
  }
}

async function onExport() {
  exporting.value = true
  try {
    const response = await meetingsApi.exportWord(meetingId.value)
    const blob = response.data
    const filename = parseFilename(response.headers, meeting.value?.title)
    triggerDownload(blob, filename)
    ElMessage.success('已开始下载 Word 文档')
  } finally {
    exporting.value = false
  }
}

async function onConfirm() {
  if (!meeting.value || !canConfirm.value) return
  confirming.value = true
  try {
    const updated = await meetingsApi.update(meetingId.value, { status: 'confirmed' })
    meeting.value = updated
    ElMessage.success('纪要已确认')
  } finally {
    confirming.value = false
  }
}

function parseFilename(headers, fallbackTitle) {
  const cd =
    headers?.['content-disposition'] ||
    headers?.['Content-Disposition'] ||
    ''
  let m = cd.match(/filename\*=([^']*)'[^']*'([^;]+)/i)
  if (m && m[2]) {
    try {
      return decodeURIComponent(m[2].trim())
    } catch (e) {
      return m[2].trim()
    }
  }
  m = cd.match(/filename="?([^";]+)"?/i)
  if (m && m[1]) {
    try {
      return decodeURIComponent(m[1].trim())
    } catch (e) {
      return m[1].trim()
    }
  }
  const base = (fallbackTitle || '会议纪要').replace(/[\\/:*?"<>|]+/g, '_')
  return `${base}.docx`
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

const statusLabelMap = {
  draft: '草稿',
  generating: '生成中',
  completed: '已生成',
  confirmed: '已确认',
  failed: '生成失败'
}

function statusLabel(s) {
  return statusLabelMap[s] || s || '-'
}

function statusTagType(s) {
  switch (s) {
    case 'completed':
      return 'success'
    case 'confirmed':
      return 'primary'
    case 'failed':
      return 'danger'
    case 'generating':
      return 'warning'
    default:
      return 'info'
  }
}

function syncGenerationPolling() {
  if (meeting.value?.status === 'generating') {
    startGenerationPolling()
  } else {
    stopGenerationPolling()
  }
}

function startGenerationPolling() {
  if (pollTimer.value) return
  pollTimer.value = window.setInterval(async () => {
    try {
      const latest = await meetingsApi.get(meetingId.value)
      meeting.value = latest
      if (latest?.status && latest.status !== 'generating') {
        stopGenerationPolling()
        await refreshTasks()
        if (latest.status === 'completed') {
          activeTab.value = 'summary'
          ElMessage.success('会议纪要已生成')
        } else if (latest.status === 'failed') {
          ElMessage.error(latest.error_message || '生成失败')
        }
      }
    } catch (e) {
      // 轮询失败不打断页面使用，下一轮继续尝试。
    }
  }, 4000)
}

function stopGenerationPolling() {
  if (!pollTimer.value) return
  window.clearInterval(pollTimer.value)
  pollTimer.value = null
}

watch(meetingId, (v) => {
  if (v) {
    stopGenerationPolling()
    meeting.value = null
    meetingFile.value = null
    kbFiles.value = []
    refresh()
  }
})

onMounted(refresh)
onUnmounted(stopGenerationPolling)
</script>

<style scoped>
.meeting-detail :deep(.section-card) {
  margin-bottom: 16px;
}

.title-line {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-line .page-title {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.generate-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  background: linear-gradient(135deg, #ffffff, #f3fbfd);
  border-color: rgba(185, 219, 232, 0.95);
  color: var(--color-text);
  box-shadow: var(--shadow-soft);
}

.section-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 800;
  color: inherit;
}

.gen-desc {
  font-size: 12px;
  color: var(--color-text-muted);
  max-width: 720px;
}
</style>
