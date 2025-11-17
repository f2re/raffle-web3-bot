import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'
import type { Raffle } from '@/types'

export const useRaffleStore = defineStore('raffle', () => {
  const activeRaffles = ref<Raffle[]>([])
  const currentRaffle = ref<Raffle | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const rafflesByType = computed(() => {
    return {
      express: activeRaffles.value.find(r => r.type === 'express'),
      standard: activeRaffles.value.find(r => r.type === 'standard'),
      premium: activeRaffles.value.find(r => r.type === 'premium')
    }
  })

  const fetchActiveRaffles = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/raffles/active')
      activeRaffles.value = response.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  const joinRaffle = async (raffleId: number, txHash: string) => {
    try {
      const response = await api.post(`/raffles/${raffleId}/join`, {
        tx_hash: txHash
      })
      await fetchActiveRaffles()
      return response.data
    } catch (e: any) {
      throw new Error(e.response?.data?.detail || 'Ошибка участия в розыгрыше')
    }
  }

  return {
    activeRaffles,
    currentRaffle,
    loading,
    error,
    rafflesByType,
    fetchActiveRaffles,
    joinRaffle
  }
})
