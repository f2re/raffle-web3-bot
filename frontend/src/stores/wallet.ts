import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useWalletStore = defineStore('wallet', () => {
  const wallet = ref<any>(null)
  const userFriendlyAddress = ref<string>('')

  const isConnected = computed(() => !!wallet.value)

  const connect = async () => {
    // TON Connect integration placeholder
    console.log('Connecting wallet...')
  }

  const disconnect = async () => {
    wallet.value = null
    userFriendlyAddress.value = ''
  }

  const sendPayment = async (amount: number, memo: string): Promise<string> => {
    if (!wallet.value) {
      throw new Error('Wallet not connected')
    }
    // Payment logic placeholder
    return `tx_hash_${Date.now()}`
  }

  return {
    wallet,
    userFriendlyAddress,
    isConnected,
    connect,
    disconnect,
    sendPayment
  }
})
