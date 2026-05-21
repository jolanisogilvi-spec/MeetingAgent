<template>
  <div class="section-card">
    <div class="card-head">
      <h3 class="section-title">参会人员</h3>
      <span class="count">{{ items.length }} 人</span>
    </div>
    <div v-if="items.length === 0" class="empty">尚未选择参会人员，可在"编辑"中添加。</div>
    <div v-else class="tags">
      <el-tag
        v-for="p in items"
        :key="p.id"
        size="default"
        class="person-tag"
      >
        <span class="name">{{ p.name }}</span>
        <span v-if="p.role" class="role">· {{ p.role }}</span>
        <span v-if="p.department" class="dept">（{{ p.department }}）</span>
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  participantIds: { type: Array, default: () => [] },
  people: { type: Array, default: () => [] },
  departments: { type: Array, default: () => [] }
})

const deptMap = computed(() =>
  Object.fromEntries(props.departments.map((d) => [d.id, d]))
)

const items = computed(() => {
  return props.participantIds
    .map((id) => {
      const p = props.people.find((x) => x.id === id)
      if (!p) return { id, name: '未知人员', role: '', department: '' }
      return {
        id: p.id,
        name: p.name,
        role: p.role,
        department: deptMap.value[p.department_id]?.name || ''
      }
    })
})
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

.count {
  color: var(--color-text-muted);
  font-size: 12px;
}

.empty {
  color: var(--color-text-muted);
  font-size: 13px;
  padding: 8px 0;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.person-tag {
  font-size: 13px;
}

.name {
  font-weight: 500;
}

.role,
.dept {
  color: var(--color-text-muted);
  margin-left: 2px;
}
</style>
