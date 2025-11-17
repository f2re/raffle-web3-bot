import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const fetchStats = async () => {
    loading.value = true
    try {
      const response = await api.get('/user/stats')
      user.value = response.data.user
    } catch (e) {
      console.error('Failed to fetch stats:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    loading,
    fetchStats
  }
})
