<template>
  <RouterLink :to="to" class="flex items-center space-x-3 px-4 py-3 hover:bg-green-600 rounded-lg transition-colors">
    <span class="h-6 w-6 shrink-0">
      <slot></slot>
    </span>
    <span class="opacity-0 group-hover:opacity-100 transition-opacity duration-200 ease-in-out whitespace-nowrap">
      {{ label }}
    </span>
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  to: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  }
})
</script>