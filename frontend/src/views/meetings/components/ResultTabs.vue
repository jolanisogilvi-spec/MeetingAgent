<template>
  <div class="section-card">
    <div class="card-head">
      <h3 class="section-title">生成结果</h3>
      <span v-if="meeting.status === 'generating'" class="hint warn">
        <el-icon class="is-loading"><Loading /></el-icon>
        正在生成…
      </span>
    </div>
    <el-tabs v-model="active">
      <el-tab-pane label="摘要" name="summary">
        <SummaryView :summary="meeting.summary" />
      </el-tab-pane>
      <el-tab-pane label="结构化纪要" name="structured">
        <StructuredView :data="meeting.meeting_json || {}" />
      </el-tab-pane>
      <el-tab-pane :label="`待办任务 (${tasks.length})`" name="actions">
        <ActionItemsTable :tasks="tasks" :loading="tasksLoading" @refresh="$emit('refresh-tasks')" />
      </el-tab-pane>
      <el-tab-pane label="JSON 编辑" name="json">
        <JsonEditor
          :meeting-id="meeting.id"
          :meeting-json="meeting.meeting_json || {}"
          @saved="onJsonSaved"
        />
      </el-tab-pane>
      <el-tab-pane label="原文" name="raw">
        <RawTextView :raw-text="meeting.raw_text || ''" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import SummaryView from './SummaryView.vue'
import StructuredView from './StructuredView.vue'
import ActionItemsTable from './ActionItemsTable.vue'
import JsonEditor from './JsonEditor.vue'
import RawTextView from './RawTextView.vue'

const props = defineProps({
  meeting: { type: Object, required: true },
  tasks: { type: Array, default: () => [] },
  tasksLoading: { type: Boolean, default: false },
  activeTab: { type: String, default: 'summary' }
})

const emit = defineEmits(['update:activeTab', 'updated', 'refresh-tasks'])

const active = ref(props.activeTab)

watch(
  () => props.activeTab,
  (v) => {
    if (v && v !== active.value) active.value = v
  }
)

watch(active, (v) => {
  emit('update:activeTab', v)
})

function onJsonSaved(meeting) {
  emit('updated', meeting)
  emit('refresh-tasks')
}
</script>

<style scoped>
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(216, 227, 234, 0.85);
}

.section-title {
  margin: 0;
  font-weight: 800;
}

.hint {
  font-size: 13px;
}

.hint.warn {
  color: var(--color-warning);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: #dbe8ef;
}
</style>
