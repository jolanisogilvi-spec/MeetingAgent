import { defineStore } from 'pinia'
import { ref } from 'vue'
import { departmentsApi } from '@/api'

export const useDepartmentsStore = defineStore('departments', () => {
  const list = ref([])
  const loading = ref(false)

  async function refresh() {
    loading.value = true
    try {
      const res = await departmentsApi.list()
      list.value = Array.isArray(res) ? res : res?.items || []
    } finally {
      loading.value = false
    }
  }

  return { list, loading, refresh }
})
