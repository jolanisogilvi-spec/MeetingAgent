<template>
  <div class="action-items-table">
    <div class="head">
      <span class="muted">该会议自动生成的待办任务（共 {{ tasks.length }} 条）</span>
      <el-button :icon="Refresh" size="small" link @click="$emit('refresh')">刷新</el-button>
    </div>
    <el-table v-loading="loading" :data="tasks" border size="small" empty-text="尚无任务">
      <el-table-column label="责任人" prop="owner_name" min-width="100">
        <template #default="{ row }">
          <span :class="{ muted: !row.owner_name }">{{ row.owner_name || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="任务标题" prop="title" min-width="260">
        <template #default="{ row }">
          <span :class="{ muted: !row.title }">{{ row.title || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="截止时间" prop="due_date" min-width="140">
        <template #default="{ row }">
          <span :class="{ muted: !row.due_date }">{{ row.due_date || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" min-width="160">
        <template #default="{ row }">
          <span>{{ formatTime(row.created_at) }}</span>
        </template>
      </el-table-column>
    </el-table>
    <div class="foot-hint">
      可以在<router-link to="/tasks" class="link">"日程任务"</router-link>页面跨会议查看、筛选并编辑这些任务。
    </div>
  </div>
</template>

<script setup>
import { Refresh } from '@element-plus/icons-vue'

defineProps({
  tasks: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})

defineEmits(['refresh'])

const statusLabelMap = {
  todo: '待办',
  doing: '进行中',
  done: '已完成',
  delayed: '延期'
}

function statusLabel(s) {
  return statusLabelMap[s] || s || '-'
}

function statusTagType(s) {
  switch (s) {
    case 'done':
      return 'success'
    case 'delayed':
      return 'danger'
    case 'doing':
      return 'warning'
    case 'todo':
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
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.muted {
  color: var(--color-text-muted);
}

.foot-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-muted);
}

.link {
  color: var(--color-primary);
}
</style>
