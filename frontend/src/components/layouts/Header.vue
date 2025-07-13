<template>
  <header class="bg-white border-b border-gray-200 p-4 flex justify-between items-center h-16">
    <div class="flex items-center space-x-3">
      <div class="md:hidden">
        <HamburgerMenu />
      </div>
      <img :src="logoUrl" alt="マナビト ロゴ" class="h-10 w-10">
      <h1 class="text-2xl font-semibold text-green-700 hidden sm:block">マナビト</h1>
    </div>

    <div v-if="scrapingStore.isScraping" class="flex items-center space-x-2 text-gray-600">
      <span>{{ scrapingStore.headerMessage }}</span>
      <div v-if="scrapingStore.completedMessages.length < scrapingStore.totalTasks"
           class="animate-spin rounded-full h-5 w-5 border-b-2 border-green-700">
      </div>
    </div>
  </header>
</template>

<script setup>
import logoUrl from '@/assets/manabito.svg';
import { useScrapingStore } from '@/stores/scrapingStore';
import HamburgerMenu from './HamburgerMenu.vue';

const scrapingStore = useScrapingStore();
</script>