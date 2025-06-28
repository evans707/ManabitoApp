<template>
  <div class="settings-page p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">設定</h1>

    <div>
      <p class="mb-2 font-semibold text-gray-700">週の開始曜日:</p>

      <div class="flex space-x-2">
        <!-- 月曜始まり -->
        <button
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-colors',
            weekStartsOn === 1 ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'
          ]"
          @click="weekStartsOn = 1"
        >
          月曜日
        </button>

        <!-- 日曜始まり -->
        <button
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-colors',
            weekStartsOn === 0 ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'
          ]"
          @click="weekStartsOn = 0"
        >
          日曜日
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useCalendarSettingsStore } from '@/stores/settings'

const settingsStore = useCalendarSettingsStore()
const weekStartsOn = ref(settingsStore.weekStartsOn)

watch(weekStartsOn, (newVal) => {
  settingsStore.setWeekStart(newVal)
})
</script>
