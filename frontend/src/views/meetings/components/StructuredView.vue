<template>
  <div class="structured-view">
    <div v-if="isEmpty" class="empty">
      <el-empty description="尚未生成结构化纪要" />
    </div>
    <template v-else>
      <el-card shadow="never" class="block">
        <template #header>
          <span class="block-title">会议主题</span>
        </template>
        <div :class="{ muted: !data.Topic }">{{ data.Topic || '-' }}</div>
      </el-card>

      <el-card shadow="never" class="block">
        <template #header>
          <span class="block-title">关键讨论点</span>
        </template>
        <ol v-if="keyPoints.length" class="list">
          <li v-for="(item, i) in keyPoints" :key="i">{{ item }}</li>
        </ol>
        <div v-else class="muted">-</div>
      </el-card>

      <el-card shadow="never" class="block">
        <template #header>
          <span class="block-title">决策结论</span>
        </template>
        <ol v-if="decisions.length" class="list">
          <li v-for="(item, i) in decisions" :key="i">{{ item }}</li>
        </ol>
        <div v-else class="muted">-</div>
      </el-card>

      <el-card shadow="never" class="block">
        <template #header>
          <span class="block-title">待办事项</span>
        </template>
        <el-table v-if="actionItems.length" :data="actionItems" size="small" border>
          <el-table-column label="责任人" prop="Who" min-width="100">
            <template #default="{ row }">
              <span :class="{ muted: !row.Who }">{{ row.Who || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="任务内容" prop="What" min-width="260">
            <template #default="{ row }">
              <span :class="{ muted: !row.What }">{{ row.What || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="截止时间" prop="When" min-width="140">
            <template #default="{ row }">
              <span :class="{ muted: !row.When }">{{ row.When || '-' }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div v-else class="muted">-</div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({}) }
})

const keyPoints = computed(() => normalizeArray(props.data?.KeyPoints))
const decisions = computed(() => normalizeArray(props.data?.Decisions))
const actionItems = computed(() => {
  const arr = props.data?.ActionItems
  if (!Array.isArray(arr)) return []
  return arr.map((x) => ({
    Who: x?.Who || '',
    What: x?.What || '',
    When: x?.When || ''
  }))
})

const isEmpty = computed(() => {
  if (!props.data) return true
  if (typeof props.data !== 'object') return true
  const hasContent =
    props.data.Topic ||
    keyPoints.value.length ||
    decisions.value.length ||
    actionItems.value.length
  return !hasContent
})

function normalizeArray(v) {
  if (!Array.isArray(v)) return []
  return v.filter((x) => x !== null && x !== undefined && String(x).length > 0)
}
</script>

<style scoped>
.structured-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.block-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text);
}

.list {
  margin: 0;
  padding-left: 20px;
  line-height: 1.8;
}

.muted {
  color: var(--color-text-muted);
}

.empty {
  padding: 16px 0;
}

:deep(.el-card) {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 251, 253, 0.96));
  border-color: rgba(194, 213, 225, 0.9);
  box-shadow: 0 10px 24px rgba(15, 40, 65, 0.06);
}

:deep(.el-card__header) {
  padding: 12px 16px;
  background: rgba(237, 248, 252, 0.7);
}
</style>
