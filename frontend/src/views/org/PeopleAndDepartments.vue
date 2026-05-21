<template>
  <div class="page org-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">人员与部门</h2>
        <div class="page-subtitle">维护组织结构和参会人员</div>
      </div>
      <el-button :icon="Refresh" @click="refreshAll">刷新</el-button>
    </div>

    <div class="split">
      <div class="col col-left">
        <DepartmentPanel
          :list="departmentsStore.list"
          :people="peopleStore.list"
          :loading="departmentsStore.loading"
          @changed="onDepartmentChanged"
        />
      </div>
      <div class="col col-right">
        <PeoplePanel
          :list="peopleStore.list"
          :departments="departmentsStore.list"
          :loading="peopleStore.loading"
          @changed="onPeopleChanged"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import DepartmentPanel from './components/DepartmentPanel.vue'
import PeoplePanel from './components/PeoplePanel.vue'
import { useDepartmentsStore } from '@/stores/departments'
import { usePeopleStore } from '@/stores/people'

const departmentsStore = useDepartmentsStore()
const peopleStore = usePeopleStore()

async function refreshAll() {
  await Promise.all([departmentsStore.refresh(), peopleStore.refresh()])
}

async function onDepartmentChanged() {
  // 删除部门会使关联人员的 department_id 变为 null，因此两边都刷新
  await Promise.all([departmentsStore.refresh(), peopleStore.refresh()])
}

async function onPeopleChanged() {
  await peopleStore.refresh()
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.org-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.split {
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(480px, 1.6fr);
  gap: 16px;
  flex: none;
  min-height: 0;
  min-width: 0;
  align-items: stretch;
}

@media (max-width: 1280px) {
  .split {
    grid-template-columns: 1fr;
  }
}

.col {
  min-height: 0;
  min-width: 0;
  display: flex;
}

.col > :deep(*) {
  flex: 1;
}
</style>
