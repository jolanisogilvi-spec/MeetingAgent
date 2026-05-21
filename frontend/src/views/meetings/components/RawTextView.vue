<template>
  <div class="raw-text-view">
    <div class="head">
      <span class="muted">{{ rawText.length }} 字符</span>
    </div>
    <div v-if="!rawText" class="empty">
      <el-empty description="尚无原文内容；可以在上方『会议材料』中粘贴或上传后生成。" />
    </div>
    <pre v-else class="raw-text">{{ rawText }}</pre>
  </div>
</template>

<script setup>
defineProps({
  rawText: { type: String, default: '' }
})
</script>

<style scoped>
.head {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.muted {
  color: var(--color-text-muted);
  font-size: 12px;
}

.raw-text {
  white-space: pre-wrap;
  word-break: break-word;
  background: #fafbfc;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 12px 14px;
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, "Menlo", "Consolas", monospace;
  font-size: 13px;
  line-height: 1.7;
  max-height: 540px;
  overflow: auto;
}

.empty {
  padding: 16px 0;
}
</style>
