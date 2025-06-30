<template>
  <header class="bg-white border-b border-gray-200 p-4">
    <div class="flex items-center space-x-3">
      <img :src="logoUrl" alt="マナビト ロゴ" class="h-12 w-12">
      <h1 class="text-2xl font-semibold text-green-700">マナビト</h1>
    </div>
  </header>
</template>

<script setup>
import logoUrl from '@/assets/manabito.svg'
</script>