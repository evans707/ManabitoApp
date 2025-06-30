<template>
  <div class="settings-page">
    <h2 class="text-2xl font-semibold mb-4 text-gray-700">設定</h2>

    <Card>
      <div class="space-y-6">
        <div>
          <h3 class="text-lg font-medium leading-6 text-gray-900">カレンダー設定</h3>
          <p class="mt-1 text-sm text-gray-500">カレンダーの週の始まりを月曜日または日曜日に設定します。</p>

          <div class="mt-4">
            <p class="mb-2 font-semibold text-gray-700">週の開始曜日:</p>
            <div class="flex space-x-2">
              <button
                :class="[
                  'px-4 py-2 rounded-lg font-medium transition-colors text-sm',
                  weekStartsOn === 1
                    ? 'bg-green-600 text-white shadow-sm'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                ]"
                @click="weekStartsOn = 1"
              >
                月曜日
              </button>

              <button
                :class="[
                  'px-4 py-2 rounded-lg font-medium transition-colors text-sm',
                  weekStartsOn === 0
                    ? 'bg-green-600 text-white shadow-sm'
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                ]"
                @click="weekStartsOn = 0"
              >
                日曜日
              </button>
            </div>
          </div>
        </div>

        </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useCalendarSettingsStore } from '@/stores/settings'
import Card from '@/components/common/Card.vue' // Cardコンポーネントをインポート

const settingsStore = useCalendarSettingsStore()
const weekStartsOn = ref(settingsStore.weekStartsOn)

watch(weekStartsOn, (newVal) => {
  settingsStore.setWeekStart(newVal)
})
</script>