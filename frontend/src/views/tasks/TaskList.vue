<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">日程任务</h2>
        <div class="page-subtitle">集中跟进所有会议中沉淀出的待办</div>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="refresh">刷新</el-button>
    </div>

    <div class="stats">
      <el-card shadow="never" class="stat-card">
        <div class="stat-label">全部任务</div>
        <div class="stat-value">{{ stats.total }}</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-label">待跟进</div>
        <div class="stat-value warn">{{ stats.pending }}</div>
        <div class="stat-foot">todo + doing</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-label">未明确责任人</div>
        <div class="stat-value danger">{{ stats.missingOwner }}</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-label">未明确时间</div>
        <div class="stat-value danger">{{ stats.missingDue }}</div>
      </el-card>
    </div>

    <div class="toolbar section-card">
      <el-radio-group v-model="quickFilter" @change="onQuickFilterChange">
        <el-radio-button value="all">全部任务</el-radio-button>
        <el-radio-button value="missing_owner">未明确责任人</el-radio-button>
        <el-radio-button value="missing_due">未明确时间</el-radio-button>
      </el-radio-group>
      <el-divider direction="vertical" />
      <el-select
        v-model="filters.department_id"
        placeholder="部门"
        clearable
        filterable
        style="width: 160px"
      >
        <el-option
          v-for="d in departmentsStore.list"
          :key="d.id"
          :label="d.name"
          :value="d.id"
        />
      </el-select>
      <el-select
        v-model="filters.owner_name"
        placeholder="责任人"
        clearable
        filterable
        style="width: 160px"
      >
        <el-option
          v-for="name in ownerOptions"
          :key="name"
          :label="name"
          :value="name"
        />
      </el-select>
      <el-select
        v-model="filters.meeting_id"
        placeholder="所属会议"
        clearable
        filterable
        style="width: 220px"
      >
        <el-option
          v-for="m in meetingsStore.list"
          :key="m.id"
          :label="m.title"
          :value="m.id"
        />
      </el-select>
      <el-select
        v-model="filters.status"
        placeholder="状态"
        clearable
        style="width: 130px"
      >
        <el-option
          v-for="s in statusOptions"
          :key="s.value"
          :label="s.label"
          :value="s.value"
        />
      </el-select>
      <el-button v-if="hasAnyFilter" @click="clearFilters">清空筛选</el-button>
    </div>

    <div class="section-card">
      <el-table
        v-loading="loading"
        :data="filteredTasks"
        stripe
        border
        empty-text="暂无任务"
      >
        <el-table-column label="所属会议" min-width="180">
          <template #default="{ row }">
            <a v-if="row.meeting_id" class="link" @click="goMeeting(row.meeting_id)">
              {{ meetingName(row.meeting_id) }}
            </a>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="所属部门" min-width="120">
          <template #default="{ row }">
            <el-tag v-if="deptName(row.department_id)" size="small">{{ deptName(row.department_id) }}</el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="责任人" min-width="140">
          <template #default="{ row }">
            <el-input
              :model-value="row.owner_name"
              size="small"
              placeholder="请输入"
              @change="(val) => onFieldChange(row, 'owner_name', val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="任务标题" min-width="260">
          <template #default="{ row }">
            <el-input
              :model-value="row.title"
              size="small"
              placeholder="请输入任务"
              @change="(val) => onFieldChange(row, 'title', val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="截止时间" min-width="160">
          <template #default="{ row }">
            <el-input
              :model-value="row.due_date"
              size="small"
              placeholder="例如：下周五"
              @change="(val) => onFieldChange(row, 'due_date', val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="130">
          <template #default="{ row }">
            <el-select
              :model-value="row.status"
              size="small"
              @change="(val) => onFieldChange(row, 'status', val)"
            >
              <el-option
                v-for="s in statusOptions"
                :key="s.value"
                :label="s.label"
                :value="s.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="160">
          <template #default="{ row }">
            <span>{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useTasksStore } from '@/stores/tasks'
import { useMeetingsStore } from '@/stores/meetings'
import { useDepartmentsStore } from '@/stores/departments'
import { tasksApi } from '@/api'

const router = useRouter()
const tasksStore = useTasksStore()
const meetingsStore = useMeetingsStore()
const departmentsStore = useDepartmentsStore()

const loading = computed(() => tasksStore.loading)

const quickFilter = ref('all')

const filters = reactive({
  department_id: '',
  owner_name: '',
  meeting_id: '',
  status: ''
})

const statusOptions = [
  { value: 'todo', label: '待办' },
  { value: 'doing', label: '进行中' },
  { value: 'done', label: '已完成' },
  { value: 'delayed', label: '延期' }
]

const meetingMap = computed(() =>
  Object.fromEntries(meetingsStore.list.map((m) => [m.id, m]))
)
const deptMap = computed(() =>
  Object.fromEntries(departmentsStore.list.map((d) => [d.id, d]))
)

function meetingName(id) {
  if (!id) return ''
  return meetingMap.value[id]?.title || '未知会议'
}

function deptName(id) {
  if (!id) return ''
  return deptMap.value[id]?.name || ''
}

const ownerOptions = computed(() => {
  const set = new Set()
  for (const t of tasksStore.list) {
    if (t.owner_name) set.add(t.owner_name)
  }
  return [...set].sort()
})

const stats = computed(() => {
  const list = tasksStore.list
  return {
    total: list.length,
    pending: list.filter((t) => t.status === 'todo' || t.status === 'doing').length,
    missingOwner: list.filter((t) => !t.owner_name).length,
    missingDue: list.filter((t) => !t.due_date).length
  }
})

const filteredTasks = computed(() => {
  return tasksStore.list.filter((t) => {
    if (quickFilter.value === 'missing_owner' && t.owner_name) return false
    if (quickFilter.value === 'missing_due' && t.due_date) return false
    if (filters.department_id && t.department_id !== filters.department_id) return false
    if (filters.owner_name && t.owner_name !== filters.owner_name) return false
    if (filters.meeting_id && t.meeting_id !== filters.meeting_id) return false
    if (filters.status && t.status !== filters.status) return false
    return true
  })
})

const hasAnyFilter = computed(
  () =>
    quickFilter.value !== 'all' ||
    filters.department_id ||
    filters.owner_name ||
    filters.meeting_id ||
    filters.status
)

function onQuickFilterChange() {
  // 切换 quickFilter 不需要额外动作，filteredTasks 已经响应
}

function clearFilters() {
  quickFilter.value = 'all'
  filters.department_id = ''
  filters.owner_name = ''
  filters.meeting_id = ''
  filters.status = ''
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

function goMeeting(id) {
  router.push(`/meetings/${id}`)
}

async function onFieldChange(row, field, value) {
  if (value === undefined || value === null) value = ''
  if (row[field] === value) return
  try {
    const updated = await tasksApi.update(row.id, { [field]: value })
    Object.assign(row, updated)
    ElMessage.success('已保存')
  } catch (e) {
    // axios 拦截器已 ElMessage.error；本地仍然刷新原值以保持一致
    refresh()
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除任务 "${row.title || '(无标题)'}"？`, '删除任务', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  await tasksApi.remove(row.id)
  ElMessage.success('任务已删除')
  refresh()
}

async function refresh() {
  await Promise.all([
    tasksStore.refresh(),
    meetingsStore.refresh(),
    departmentsStore.refresh()
  ])
}

onMounted(refresh)
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 1100px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  min-height: 96px;
  border: 1px solid #d2e0eb;
  background: #ffffff;
  color: var(--color-text);
  box-shadow: var(--shadow-soft);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  display: none;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-muted);
  font-weight: 700;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  margin-top: 12px;
  color: var(--color-text);
}

.stat-value.warn {
  color: var(--color-warning);
}

.stat-value.danger {
  color: var(--color-danger);
}

.stat-foot {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px 16px;
}

.link {
  color: var(--color-primary);
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.muted {
  color: var(--color-text-muted);
}
</style>
