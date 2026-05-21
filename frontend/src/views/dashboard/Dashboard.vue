<template>
  <div class="page dashboard-page" v-loading="loading">
    <div class="page-header dashboard-hero">
      <div>
        <h2 class="page-title">数据看板</h2>
        <div class="page-subtitle">运营工作台</div>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" :loading="loading" @click="refreshAll">刷新数据</el-button>
        <el-button type="primary" :icon="Plus" @click="router.push('/meetings')">进入会议</el-button>
      </div>
    </div>

    <div class="kpi-grid">
      <div v-for="item in kpis" :key="item.label" class="kpi-card">
        <div class="kpi-label">{{ item.label }}</div>
        <div class="kpi-value">{{ item.value }}</div>
        <div class="kpi-foot">{{ item.foot }}</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <section class="panel-card">
        <div class="panel-head">
          <div>
            <h3>会议状态</h3>
            <p>按当前生成状态统计</p>
          </div>
        </div>
        <div class="status-list">
          <div v-for="item in meetingStatusRows" :key="item.key" class="status-row">
            <div class="status-meta">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: item.percent + '%', background: item.color }"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="panel-card">
        <div class="panel-head">
          <div>
            <h3>任务健康</h3>
            <p>待办完整度与推进情况</p>
          </div>
        </div>
        <div class="health-grid">
          <div class="health-item">
            <span>待跟进</span>
            <strong>{{ taskStats.pending }}</strong>
          </div>
          <div class="health-item">
            <span>已完成</span>
            <strong>{{ taskStats.done }}</strong>
          </div>
          <div class="health-item warn">
            <span>未明确责任人</span>
            <strong>{{ taskStats.missingOwner }}</strong>
          </div>
          <div class="health-item warn">
            <span>未明确时间</span>
            <strong>{{ taskStats.missingDue }}</strong>
          </div>
        </div>
      </section>
    </div>

    <div class="dashboard-grid lower">
      <section class="panel-card">
        <div class="panel-head">
          <div>
            <h3>部门人员</h3>
            <p>组织资料覆盖情况</p>
          </div>
        </div>
        <div v-if="departmentRows.length" class="dept-list">
          <div v-for="dept in departmentRows" :key="dept.id" class="dept-row">
            <div class="dept-meta">
              <span>{{ dept.name }}</span>
              <strong>{{ dept.count }} 人</strong>
            </div>
            <div class="bar-track">
              <div class="bar-fill teal" :style="{ width: dept.percent + '%' }"></div>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无部门数据" :image-size="72" />
      </section>

      <section class="panel-card recent-card">
        <div class="panel-head">
          <div>
            <h3>最近会议</h3>
            <p>按更新时间排序</p>
          </div>
          <el-button link type="primary" @click="router.push('/meetings')">查看全部</el-button>
        </div>
        <el-table :data="recentMeetings" size="small" border empty-text="暂无会议">
          <el-table-column label="会议名称" min-width="180">
            <template #default="{ row }">
              <a class="meeting-link" @click="router.push(`/meetings/${row.id}`)">{{ row.title }}</a>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="92">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="更新时间" min-width="130">
            <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
          </el-table-column>
        </el-table>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { useDepartmentsStore } from '@/stores/departments'
import { useMeetingsStore } from '@/stores/meetings'
import { usePeopleStore } from '@/stores/people'
import { useTasksStore } from '@/stores/tasks'

const router = useRouter()
const meetingsStore = useMeetingsStore()
const tasksStore = useTasksStore()
const departmentsStore = useDepartmentsStore()
const peopleStore = usePeopleStore()

const loading = computed(
  () =>
    meetingsStore.loading ||
    tasksStore.loading ||
    departmentsStore.loading ||
    peopleStore.loading
)

const meetingStats = computed(() => {
  const list = meetingsStore.list || []
  return {
    total: list.length,
    draft: list.filter((m) => m.status === 'draft').length,
    generating: list.filter((m) => m.status === 'generating').length,
    completed: list.filter((m) => m.status === 'completed' || m.status === 'confirmed').length,
    failed: list.filter((m) => m.status === 'failed').length
  }
})

const taskStats = computed(() => {
  const list = tasksStore.list || []
  return {
    total: list.length,
    pending: list.filter((t) => t.status === 'todo' || t.status === 'doing').length,
    done: list.filter((t) => t.status === 'done').length,
    missingOwner: list.filter((t) => !t.owner_name).length,
    missingDue: list.filter((t) => !t.due_date).length
  }
})

const kpis = computed(() => [
  { label: '会议总数', value: meetingStats.value.total, foot: '全部会议记录' },
  { label: '已生成纪要', value: meetingStats.value.completed, foot: 'completed + confirmed' },
  { label: '任务总数', value: taskStats.value.total, foot: '会议沉淀待办' },
  { label: '组织人数', value: peopleStore.list.length, foot: `${departmentsStore.list.length} 个部门` }
])

const meetingStatusRows = computed(() => {
  const total = Math.max(meetingStats.value.total, 1)
  return [
    { key: 'draft', label: '草稿', value: meetingStats.value.draft, color: '#94a3b8' },
    { key: 'generating', label: '生成中', value: meetingStats.value.generating, color: '#f59e0b' },
    { key: 'completed', label: '已生成', value: meetingStats.value.completed, color: '#0796bd' },
    { key: 'failed', label: '生成失败', value: meetingStats.value.failed, color: '#f04438' }
  ].map((item) => ({ ...item, percent: Math.round((item.value / total) * 100) }))
})

const departmentRows = computed(() => {
  const counts = Object.fromEntries(departmentsStore.list.map((d) => [d.id, 0]))
  for (const person of peopleStore.list) {
    if (person.department_id && counts[person.department_id] !== undefined) {
      counts[person.department_id] += 1
    }
  }
  const rows = departmentsStore.list.map((dept) => ({
    id: dept.id,
    name: dept.name,
    count: counts[dept.id] || 0
  }))
  const maxCount = Math.max(...rows.map((r) => r.count), 1)
  return rows
    .map((row) => ({ ...row, percent: Math.max(6, Math.round((row.count / maxCount) * 100)) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6)
})

const recentMeetings = computed(() => {
  return [...(meetingsStore.list || [])].slice(0, 6)
})

function statusLabel(s) {
  const map = {
    draft: '草稿',
    generating: '生成中',
    completed: '已生成',
    confirmed: '已确认',
    failed: '失败'
  }
  return map[s] || s || '-'
}

function statusTagType(s) {
  if (s === 'completed' || s === 'confirmed') return 'success'
  if (s === 'generating') return 'warning'
  if (s === 'failed') return 'danger'
  return 'info'
}

function formatTime(raw) {
  if (!raw) return '-'
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return raw
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function refreshAll() {
  await Promise.all([
    meetingsStore.refresh(),
    tasksStore.refresh(),
    departmentsStore.refresh(),
    peopleStore.refresh()
  ])
}

onMounted(refreshAll)
</script>

<style scoped>
.dashboard-page {
  padding-bottom: 40px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.kpi-card,
.panel-card {
  background: #ffffff;
  border: 1px solid #d2e0eb;
  border-radius: var(--radius);
  box-shadow: var(--shadow-soft);
}

.kpi-card {
  min-height: 108px;
  padding: 18px;
}

.kpi-label {
  color: #60758b;
  font-size: 13px;
  font-weight: 700;
}

.kpi-value {
  margin-top: 12px;
  color: #071a33;
  font-size: 30px;
  font-weight: 900;
  line-height: 1;
}

.kpi-foot {
  margin-top: 10px;
  color: var(--color-text-muted);
  font-size: 12px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.dashboard-grid.lower {
  grid-template-columns: minmax(320px, 0.9fr) minmax(0, 1.4fr);
}

.panel-card {
  padding: 16px;
  min-width: 0;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-head h3 {
  margin: 0;
  color: #071a33;
  font-size: 16px;
  font-weight: 900;
}

.panel-head p {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 12px;
}

.status-list,
.dept-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.status-meta,
.dept-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 7px;
  color: #53687e;
  font-weight: 700;
}

.status-meta strong,
.dept-meta strong {
  color: #071a33;
}

.bar-track {
  height: 9px;
  overflow: hidden;
  background: #eef5fa;
  border-radius: 999px;
}

.bar-fill {
  height: 100%;
  min-width: 4px;
  border-radius: 999px;
}

.bar-fill.teal {
  background: linear-gradient(90deg, #0796bd, #12a894);
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.health-item {
  min-height: 92px;
  padding: 16px;
  background: #f8fbfd;
  border: 1px solid #dbe8f1;
  border-radius: var(--radius);
}

.health-item span {
  display: block;
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 700;
}

.health-item strong {
  display: block;
  margin-top: 12px;
  color: #071a33;
  font-size: 26px;
  font-weight: 900;
}

.health-item.warn strong {
  color: #d97706;
}

.meeting-link {
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 700;
}

@media (max-width: 1100px) {
  .kpi-grid,
  .dashboard-grid,
  .dashboard-grid.lower {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .kpi-grid,
  .dashboard-grid,
  .dashboard-grid.lower,
  .health-grid {
    grid-template-columns: 1fr;
  }

  .header-actions {
    flex-wrap: wrap;
  }
}
</style>
