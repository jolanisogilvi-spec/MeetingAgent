<template>
  <div class="org-panel">
    <div class="panel-header">
      <div class="panel-title">
        <span>人员</span>
        <span class="count">{{ filteredList.length }}</span>
      </div>
      <div class="panel-actions">
        <el-input
          v-model="keyword"
          placeholder="搜索姓名/角色/邮箱"
          clearable
          size="default"
          style="width: 200px"
          :prefix-icon="Search"
        />
        <el-select
          v-model="filterDept"
          placeholder="按部门筛选"
          clearable
          style="width: 160px"
        >
          <el-option label="未分配部门" value="__none__" />
          <el-option
            v-for="d in departments"
            :key="d.id"
            :label="d.name"
            :value="d.id"
          />
        </el-select>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增人员</el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="filteredList"
      stripe
      border
      height="100%"
      empty-text="暂无人员"
    >
      <el-table-column prop="name" label="姓名" min-width="100" />
      <el-table-column label="所属部门" min-width="120">
        <template #default="{ row }">
          <el-tag v-if="deptNameOf(row.department_id)" size="small">
            {{ deptNameOf(row.department_id) }}
          </el-tag>
          <span v-else class="muted">未分配</span>
        </template>
      </el-table-column>
      <el-table-column prop="role" label="职位/角色" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">
          <span :class="{ muted: !row.role }">{{ row.role || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span :class="{ muted: !row.email }">{{ row.email || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="电话" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <span :class="{ muted: !row.phone }">{{ row.phone || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="520px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="90px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" maxlength="128" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="所属部门" prop="department_id">
          <el-select v-model="form.department_id" placeholder="请选择部门" clearable style="width: 100%">
            <el-option
              v-for="d in departments"
              :key="d.id"
              :label="d.name"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位/角色" prop="role">
          <el-input v-model="form.role" placeholder="例如：产品经理" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="可选" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="可选" />
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
import { peopleApi } from '@/api'

const props = defineProps({
  list: { type: Array, required: true },
  departments: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['changed'])

const keyword = ref('')
const filterDept = ref('')

const deptMap = computed(() => {
  const m = {}
  for (const d of props.departments) m[d.id] = d
  return m
})

function deptNameOf(id) {
  if (!id) return ''
  return deptMap.value[id]?.name || ''
}

const filteredList = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return props.list.filter((p) => {
    if (filterDept.value === '__none__') {
      if (p.department_id) return false
    } else if (filterDept.value) {
      if (p.department_id !== filterDept.value) return false
    }
    if (!kw) return true
    return (
      p.name?.toLowerCase().includes(kw) ||
      p.role?.toLowerCase().includes(kw) ||
      p.email?.toLowerCase().includes(kw) ||
      p.phone?.toLowerCase().includes(kw)
    )
  })
})

const dialogVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)
const form = ref({ name: '', department_id: null, role: '', email: '', phone: '' })

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    {
      validator: (rule, value, callback) => {
        if (!value) return callback()
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!re.test(value)) return callback(new Error('邮箱格式不正确'))
        callback()
      },
      trigger: 'blur'
    }
  ]
}

const dialogTitle = computed(() => (editingId.value ? '编辑人员' : '新增人员'))

function resetForm() {
  editingId.value = null
  form.value = { name: '', department_id: null, role: '', email: '', phone: '' }
  formRef.value?.clearValidate()
}

function openCreate() {
  resetForm()
  if (filterDept.value && filterDept.value !== '__none__') {
    form.value.department_id = filterDept.value
  }
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.value = {
    name: row.name,
    department_id: row.department_id || null,
    role: row.role || '',
    email: row.email || '',
    phone: row.phone || ''
  }
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = { ...form.value }
    if (editingId.value) {
      await peopleApi.update(editingId.value, payload)
      ElMessage.success('人员已更新')
    } else {
      await peopleApi.create(payload)
      ElMessage.success('人员已创建')
    }
    dialogVisible.value = false
    emit('changed')
  } finally {
    submitting.value = false
  }
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(`确认删除人员 "${row.name}"？`, '删除人员', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  await peopleApi.remove(row.id)
  ElMessage.success('人员已删除')
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
  flex-wrap: wrap;
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
  background: #edf9f6;
  color: #168072;
  padding: 2px 8px;
  border: 1px solid rgba(20, 184, 166, 0.22);
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

  .panel-actions :deep(.el-input),
  .panel-actions :deep(.el-select) {
    width: 100% !important;
  }
}

@media (max-width: 1280px) {
  .org-panel {
    min-height: 360px;
  }
}
</style>
