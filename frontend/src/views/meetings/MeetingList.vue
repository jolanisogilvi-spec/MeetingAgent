<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">会议</h2>
        <div class="page-subtitle">运营工作台</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="createVisible = true">新建会议</el-button>
      </div>
    </div>

    <div class="meeting-stats">
      <div class="metric-card">
        <div class="metric-label">会议总数</div>
        <div class="metric-value">{{ meetingStats.total }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">草稿会议</div>
        <div class="metric-value">{{ meetingStats.draft }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">生成中</div>
        <div class="metric-value">{{ meetingStats.generating }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">已生成</div>
        <div class="metric-value">{{ meetingStats.completed }}</div>
      </div>
    </div>

    <div class="toolbar section-card">
      <el-input
        v-model="filters.keyword"
        placeholder="按名称/目标/备注搜索"
        clearable
        style="width: 240px"
        :prefix-icon="Search"
        @keyup.enter="refresh"
        @clear="refresh"
      />
      <el-select
        v-model="filters.status"
        placeholder="状态"
        clearable
        style="width: 140px"
        @change="refresh"
      >
        <el-option
          v-for="s in statusOptions"
          :key="s.value"
          :label="s.label"
          :value="s.value"
        />
      </el-select>
      <el-select
        v-model="filters.department_id"
        placeholder="部门"
        clearable
        filterable
        style="width: 180px"
        @change="refresh"
      >
        <el-option
          v-for="d in departmentsStore.list"
          :key="d.id"
          :label="d.name"
          :value="d.id"
        />
      </el-select>
      <el-button :icon="Search" @click="refresh">搜索</el-button>
      <el-button :icon="Refresh" :loading="meetingsStore.loading" @click="refresh">刷新</el-button>
    </div>

    <div class="section-card">
      <el-table
        v-loading="meetingsStore.loading"
        :data="meetingsStore.list"
        stripe
        border
        empty-text="暂无会议"
        @row-click="onRowClick"
      >
        <el-table-column label="会议名称" min-width="190">
          <template #default="{ row }">
            <a class="title-link" @click.stop="goDetail(row.id)">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column label="会议时间" min-width="135">
          <template #default="{ row }">
            <span :class="{ muted: !row.meeting_time }">
              {{ row.meeting_time ? formatTime(row.meeting_time) : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="所属部门" min-width="105">
          <template #default="{ row }">
            <el-tag v-if="deptName(row.department_id)" size="small">
              {{ deptName(row.department_id) }}
            </el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="参会人员" min-width="140">
          <template #default="{ row }">
            <template v-if="row.participant_ids?.length">
              <el-tag
                v-for="pid in row.participant_ids.slice(0, 3)"
                :key="pid"
                size="small"
                type="info"
                class="participant-tag"
              >
                {{ personName(pid) }}
              </el-tag>
              <span v-if="row.participant_ids.length > 3" class="more">
                +{{ row.participant_ids.length - 3 }}
              </span>
            </template>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="92">
          <template #default="{ row }">
            <el-tag
              :type="statusTagType(row.status)"
              :effect="row.status === 'generating' ? 'dark' : 'light'"
              size="small"
            >
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最近更新" min-width="130">
          <template #default="{ row }">
            <span>{{ formatTime(row.updated_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="goDetail(row.id)">详情</el-button>
            <el-button link type="danger" @click.stop="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <CreateMeetingDialog
      v-model="createVisible"
      :departments="departmentsStore.list"
      :people="peopleStore.list"
      @created="onCreated"
    />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import CreateMeetingDialog from './components/CreateMeetingDialog.vue'
import { useMeetingsStore } from '@/stores/meetings'
import { useDepartmentsStore } from '@/stores/departments'
import { usePeopleStore } from '@/stores/people'
import { meetingsApi } from '@/api'

const router = useRouter()
const meetingsStore = useMeetingsStore()
const departmentsStore = useDepartmentsStore()
const peopleStore = usePeopleStore()

const createVisible = ref(false)

const filters = reactive({
  keyword: '',
  status: '',
  department_id: ''
})

const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'generating', label: '生成中' },
  { value: 'completed', label: '已生成' },
  { value: 'confirmed', label: '已确认' },
  { value: 'failed', label: '生成失败' }
]
const statusLabelMap = Object.fromEntries(statusOptions.map((s) => [s.value, s.label]))

const meetingStats = computed(() => {
  const list = meetingsStore.list || []
  return {
    total: list.length,
    draft: list.filter((m) => m.status === 'draft').length,
    generating: list.filter((m) => m.status === 'generating').length,
    completed: list.filter((m) => m.status === 'completed' || m.status === 'confirmed').length
  }
})

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
    case 'draft':
    default:
      return 'info'
  }
}

const deptMap = computed(() => Object.fromEntries(departmentsStore.list.map((d) => [d.id, d])))
const personMap = computed(() => Object.fromEntries(peopleStore.list.map((p) => [p.id, p])))

function deptName(id) {
  if (!id) return ''
  return deptMap.value[id]?.name || ''
}

function personName(id) {
  return personMap.value[id]?.name || id
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

function goDetail(id) {
  router.push(`/meetings/${id}`)
}

function onRowClick(row) {
  goDetail(row.id)
}

function onCreated(meeting) {
  goDetail(meeting.id)
}

async function refresh() {
  const params = {}
  if (filters.keyword.trim()) params.keyword = filters.keyword.trim()
  if (filters.status) params.status = filters.status
  if (filters.department_id) params.department_id = filters.department_id
  await meetingsStore.refresh(params)
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除会议 "${row.title}" 及其相关任务？`, '删除会议', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  await meetingsApi.remove(row.id)
  ElMessage.success('会议已删除')
  refresh()
}

onMounted(async () => {
  await Promise.all([
    departmentsStore.refresh(),
    peopleStore.refresh(),
    refresh()
  ])
})
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 8px;
}

.meeting-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.metric-card {
  min-height: 96px;
  padding: 18px;
  background: #ffffff;
  border: 1px solid #d2e0eb;
  border-radius: var(--radius);
  box-shadow: var(--shadow-soft);
}

.metric-label {
  color: #60758b;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 12px;
}

.metric-value {
  color: #071a33;
  font-size: 28px;
  font-weight: 900;
  line-height: 1;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 0;
  margin-bottom: 16px;
}

.title-link {
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 500;
}

.title-link:hover {
  text-decoration: underline;
}

.participant-tag {
  margin-right: 4px;
}

.more {
  color: var(--color-text-muted);
  font-size: 12px;
  margin-left: 4px;
}

.muted {
  color: var(--color-text-muted);
}

:deep(.el-table__row) {
  cursor: pointer;
}

@media (max-width: 900px) {
  .meeting-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .meeting-stats {
    grid-template-columns: 1fr;
  }
}
</style>
