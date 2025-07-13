<template>
  <nav class="fixed bottom-0 left-0 right-0 h-12 bg-green-700 border-t border-gray-200 shadow-t-md flex justify-around items-center z-40">
    <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="flex flex-col items-center justify-center text-white hover:bg-green-600 transition-colors w-full h-full" active-class="bg-green-600">
      <component :is="item.icon" class="h-6 w-6 mb-1"/>
      <span class="text-xs font-medium">{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup>
import { shallowRef } from 'vue'
import { RouterLink } from 'vue-router'
import IconHome from '@/components/icons/IconHome.vue'
import IconCalendar from '@/components/icons/IconCalendar.vue'
import IconAssignment from '@/components/icons/IconAssignment.vue'

const navItems = shallowRef([
  { to: '/calendar', label: 'カレンダー', icon: IconCalendar },
  { to: '/', label: 'ホーム', icon: IconHome },
  { to: '/all-assignments', label: '課題一覧', icon: IconAssignment }
])
</script>