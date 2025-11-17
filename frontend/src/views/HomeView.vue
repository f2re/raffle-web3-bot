<script setup lang="ts">
import { onMounted } from 'vue'
import { useRaffleStore } from '@/stores/raffle'
import RaffleCard from '@/components/RaffleCard.vue'

const raffleStore = useRaffleStore()

onMounted(async () => {
  await raffleStore.fetchActiveRaffles()
})
</script>

<template>
  <div class="home-view p-4 pb-20">
    <header class="header mb-6">
      <h1 class="text-2xl font-bold">🎯 Активные розыгрыши</h1>
    </header>

    <div v-if="raffleStore.loading" class="loading flex flex-col items-center justify-center py-12">
      <div class="spinner w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <p class="mt-4">Загрузка розыгрышей...</p>
    </div>

    <div v-else-if="raffleStore.error" class="error text-center py-12">
      <p class="text-red-500">{{ raffleStore.error }}</p>
      <button @click="raffleStore.fetchActiveRaffles()" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded">
        Повторить
      </button>
    </div>

    <div v-else class="raffles-list space-y-4">
      <RaffleCard
        v-for="raffle in raffleStore.activeRaffles"
        :key="raffle.id"
        :raffle="raffle"
      />
    </div>
  </div>
</template>

<style scoped>
.home-view {
  min-height: 100vh;
}
</style>
