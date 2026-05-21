import { defineStore } from 'pinia'
import { ref } from 'vue'
import { peopleApi } from '@/api'

export const usePeopleStore = defineStore('people', () => {
  const list = ref([])
  const loading = ref(false)

  async function refresh(params) {
    loading.value = true
    try {
      const res = await peopleApi.list(params)
      list.value = Array.isArray(res) ? res : res?.items || []
    } finally {
      loading.value = false
    }
  }

  return { list, loading, refresh }
})
