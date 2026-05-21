<template>
  <div class="org-panel">
    <div class="panel-header">
      <div class="panel-title">
        <span>部门</span>
        <span class="count">{{ filteredList.length }}</span>
      </div>
      <div class="panel-actions">
        <el-input
          v-model="keyword"
          placeholder="搜索部门"
          clearable
          size="default"
          style="width: 180px"
          :prefix-icon="Search"
        />
        <el-button type="primary" :icon="Plus" @click="openCreate">新增部门</el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="filteredList"
      stripe
      border
      height="100%"
      empty-text="暂无部门"
    >
      <el-table-column prop="name" label="名称" min-width="140">
        <template #default="{ row }">
          <span class="dept-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span :class="{ muted: !row.description }">{{ row.description || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="人员数" width="90" align="center">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ countOf(row.id) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="480px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" maxlength="128" show-word-limit placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">
          {{ editingId ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { departmentsApi } from '@/api'

const props = defineProps({
  list: { type: Array, required: true },
  people: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['changed'])

const keyword = ref('')

const filteredList = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return props.list
  return props.list.filter(
    (d) =>
      d.name?.toLowerCase().includes(kw) ||
      d.description?.toLowerCase().includes(kw)
  )
})

const peopleCountMap = computed(() => {
  const map = {}
  for (const p of props.people) {
    if (!p.department_id) continue
    map[p.department_id] = (map[p.department_id] || 0) + 1
  }
  return map
})

function countOf(id) {
  return peopleCountMap.value[id] || 0
}

const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)
const form = ref({ name: '', description: '' })
const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

const dialogTitle = computed(() => (editingId.value ? '编辑部门' : '新增部门'))

function resetForm() {
  editingId.value = null
  form.value = { name: '', description: '' }
  formRef.value?.clearValidate()
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.value = { name: row.name, description: row.description || '' }
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (editingId.value) {
      await departmentsApi.update(editingId.value, { ...form.value })
      ElMessage.success('部门已更新')
    } else {
      await departmentsApi.create({ ...form.value })
      ElMessage.success('部门已创建')
    }
    dialogVisible.value = false
    emit('changed')
  } finally {
    submitting.value = false
  }
}

async function onDelete(row) {
  const peopleCount = countOf(row.id)
  const tip = peopleCount > 0
    ? `部门 "${row.name}" 当前有 ${peopleCount} 名人员，删除后这些人员将变为未分配部门。是否继续？`
    : `确认删除部门 "${row.name}"？`
  try {
    await ElMessageBox.confirm(tip, '删除部门', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  await departmentsApi.remove(row.id)
  ElMessage.success('部门已删除')
  emit('changed')
}
</script>

<style scoped>
.org-panel {
  background: #ffffff;
  border: 1px solid rgba(212, 224, 234, 0.95);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
  min-width: 0;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(216, 227, 234, 0.9);
}

.panel-title {
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text);
}

.panel-title .count {
  font-size: 12px;
  background: #eef8fb;
  color: #167b91;
  padding: 2px 8px;
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 999px;
  font-weight: 700;
}

.panel-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  min-width: 0;
}

.dept-name {
  font-weight: 500;
}

.muted {
  color: var(--color-text-muted);
}

:deep(.el-table) {
  flex: 1;
  min-width: 0;
}

@media (max-width: 760px) {
  .panel-header {
    align-items: stretch;
    flex-direction: column;
  }

  .panel-actions {
    justify-content: flex-start;
  }

  .panel-actions :deep(.el-input) {
    width: 100% !important;
  }
}

@media (max-width: 1280px) {
  .org-panel {
    min-height: 360px;
  }
}
</style>
