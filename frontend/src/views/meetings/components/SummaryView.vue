<template>
  <div class="summary-view">
    <div v-if="!summary" class="empty">
      <el-empty description="尚未生成摘要，请先点击上方的『生成会议纪要』按钮" />
    </div>
    <pre v-else class="summary-text">{{ summary }}</pre>
  </div>
</template>

<script setup>
defineProps({
  summary: { type: String, default: '' }
})
</script>

<style scoped>
.summary-text {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.8;
  color: var(--color-text);
  margin: 0;
  padding: 8px 4px;
}

.empty {
  padding: 16px 0;
}
</style>
