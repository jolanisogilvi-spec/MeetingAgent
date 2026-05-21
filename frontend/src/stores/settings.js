import { defineStore } from 'pinia'
import { ref } from 'vue'
import { settingsApi } from '@/api'

export const useSettingsStore = defineStore('settings', () => {
  const data = ref(null)
  const loading = ref(false)

  async function refresh() {
    loading.value = true
    try {
      data.value = await settingsApi.get()
    } finally {
      loading.value = false
    }
  }

  return { data, loading, refresh }
})
