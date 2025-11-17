<script setup lang="ts">
import { computed, ref } from 'vue'
import { useWalletStore } from '@/stores/wallet'
import { useRaffleStore } from '@/stores/raffle'
import type { Raffle } from '@/types'

interface Props {
  raffle: Raffle
}

const props = defineProps<Props>()
const walletStore = useWalletStore()
const raffleStore = useRaffleStore()

const isJoining = ref(false)

const progress = computed(() =>
  (props.raffle.current_participants / props.raffle.min_participants) * 100
)

const typeEmoji = computed(() => {
  const emojis = { express: '🚀', standard: '⭐', premium: '💎' }
  return emojis[props.raffle.type]
})

const handleJoin = async () => {
  if (!walletStore.isConnected) {
    await walletStore.connect()
    return
  }

  isJoining.value = true

  try {
    const txHash = await walletStore.sendPayment(
      props.raffle.entry_fee_ton,
      `raffle_${props.raffle.id}`
    )

    await raffleStore.joinRaffle(props.raffle.id, txHash)

    alert('Вы успешно участвуете в розыгрыше! 🎉')
  } catch (error: any) {
    console.error('Join error:', error)
    alert(error.message || 'Ошибка участия в розыгрыше')
  } finally {
    isJoining.value = false
  }
}
</script>

<template>
  <div class="raffle-card bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-4 mb-4 border-2 border-blue-500">
    <div class="raffle-header flex justify-between items-center mb-3">
      <span class="raffle-badge text-lg font-bold">
        {{ typeEmoji }} {{ raffle.type.toUpperCase() }}
      </span>
      <span :class="[
        'raffle-status text-xs px-2 py-1 rounded-full',
        raffle.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
      ]">
        {{ raffle.status }}
      </span>
    </div>

    <div class="raffle-body space-y-3">
      <div class="participants-info flex justify-between items-center">
        <span class="text-gray-600 dark:text-gray-400">Участников:</span>
        <span class="font-semibold">
          {{ raffle.current_participants }}/{{ raffle.min_participants }}
        </span>
      </div>

      <div class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          class="h-full bg-blue-500 transition-all duration-500 ease-out"
          :style="{ width: `${progress}%` }"
        />
      </div>

      <div class="raffle-details space-y-2">
        <div class="detail-item flex justify-between items-center">
          <span class="text-gray-600 dark:text-gray-400">Взнос:</span>
          <span class="font-semibold">{{ raffle.entry_fee_ton }} TON</span>
        </div>
        <div class="detail-item flex justify-between items-center">
          <span class="text-gray-600 dark:text-gray-400">Приз:</span>
          <span class="font-semibold text-green-600 dark:text-green-400 text-lg">
            💰 {{ raffle.prize_pool_ton }} TON
          </span>
        </div>
      </div>
    </div>

    <div class="raffle-actions flex gap-2 mt-4">
      <button
        v-if="raffle.status === 'active'"
        @click="handleJoin"
        :disabled="isJoining"
        class="flex-1 py-3 rounded-xl font-medium transition-all bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50"
      >
        <span v-if="isJoining">Обработка...</span>
        <span v-else>Участвовать</span>
      </button>
    </div>
  </div>
</template>
