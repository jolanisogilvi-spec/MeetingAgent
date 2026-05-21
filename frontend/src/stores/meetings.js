import { defineStore } from 'pinia'
import { ref } from 'vue'
import { meetingsApi } from '@/api'

export const useMeetingsStore = defineStore('meetings', () => {
  const list = ref([])
  const loading = ref(false)

  async function refresh(params) {
    loading.value = true
    try {
      const res = await meetingsApi.list(params)
      list.value = Array.isArray(res) ? res : res?.items || []
    } finally {
      loading.value = false
    }
  }

  return { list, loading, refresh }
})
