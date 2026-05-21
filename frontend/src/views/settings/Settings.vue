<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">设置</h2>
        <div class="page-subtitle">分别配置大模型、Embedding、语音模型；每张卡片独立保存与测试</div>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="refresh">刷新</el-button>
    </div>

    <div v-loading="loading && !settingsStore.data" class="cards">
      <LLMCard :settings="settingsStore.data" @saved="onSaved" />
      <EmbeddingCard :settings="settingsStore.data" @saved="onSaved" />
      <SpeechCard :settings="settingsStore.data" @saved="onSaved" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import LLMCard from './components/LLMCard.vue'
import EmbeddingCard from './components/EmbeddingCard.vue'
import SpeechCard from './components/SpeechCard.vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const loading = computed(() => settingsStore.loading)

async function refresh() {
  await settingsStore.refresh()
}

function onSaved(updated) {
  // 后端返回的就是 mask 之后的最新数据，直接更新 store
  if (updated) settingsStore.data = updated
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1040px;
}
</style>
