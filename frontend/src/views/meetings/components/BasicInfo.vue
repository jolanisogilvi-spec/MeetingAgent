<template>
  <div class="section-card">
    <div class="card-head">
      <h3 class="section-title">基础信息</h3>
      <el-button link type="primary" :icon="Edit" @click="$emit('edit')">编辑</el-button>
    </div>
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="会议名称">
        <span class="strong">{{ meeting.title }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag
          :type="statusTagType(meeting.status)"
          :effect="meeting.status === 'generating' ? 'dark' : 'light'"
          size="small"
        >
          {{ statusLabel(meeting.status) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="会议时间">
        <span :class="{ muted: !meeting.meeting_time }">
          {{ meeting.meeting_time ? formatTime(meeting.meeting_time) : '-' }}
        </span>
      </el-descriptions-item>
      <el-descriptions-item label="所属部门">
        <span :class="{ muted: !deptName }">{{ deptName || '-' }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="会议类型">
        <span :class="{ muted: !meeting.meeting_type }">{{ meeting.meeting_type || '-' }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="最近更新">
        {{ formatTime(meeting.updated_at) }}
      </el-descriptions-item>
      <el-descriptions-item label="会议目标" :span="2">
        <span :class="{ muted: !meeting.objective }">{{ meeting.objective || '-' }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">
        <span :class="{ muted: !meeting.notes }">{{ meeting.notes || '-' }}</span>
      </el-descriptions-item>
    </el-descriptions>
    <el-alert
      v-if="meeting.status === 'failed' && meeting.error_message"
      class="err-alert"
      type="error"
      :title="`生成失败：${meeting.error_message}`"
      show-icon
      :closable="false"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Edit } from '@element-plus/icons-vue'

const props = defineProps({
  meeting: { type: Object, required: true },
  departments: { type: Array, default: () => [] }
})

defineEmits(['edit'])

const deptName = computed(() => {
  if (!props.meeting.department_id) return ''
  const d = props.departments.find((x) => x.id === props.meeting.department_id)
  return d?.name || ''
})

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

function formatTime(raw) {
  if (!raw) return '-'
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return raw
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`
}
</script>

<style scoped>
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  margin: 0;
}

.strong {
  font-weight: 600;
}

.muted {
  color: var(--color-text-muted);
}

.err-alert {
  margin-top: 12px;
}
</style>
