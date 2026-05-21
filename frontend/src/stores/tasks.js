import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tasksApi } from '@/api'

export const useTasksStore = defineStore('tasks', () => {
  const list = ref([])
  const loading = ref(false)

  async function refresh(params) {
    loading.value = true
    try {
      const res = await tasksApi.list(params)
      list.value = Array.isArray(res) ? res : res?.items || []
    } finally {
      loading.value = false
    }
  }

  return { list, loading, refresh }
})
