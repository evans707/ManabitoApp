<template>
  <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:bg-gray-50 transition-colors">
    <div class="flex-grow font-semibold text-gray-800">
      {{ assignment.title }}
    </div>

    <div class="flex items-center gap-2 md:gap-4 flex-shrink-0 w-full md:w-auto justify-end">
      <div class="text-sm text-gray-600 text-right hidden lg:block">
        {{ formatDate(assignment.due_date) }}
      </div>
      <div class="w-20 text-center">
        <span :class="statusClass" class="text-sm font-bold">
          {{ statusText }}
        </span>
      </div>

      <button 
        v-if="assignment.url"
        @click="openSubmissionPage"
        class="inline-block bg-green-500 text-white text-sm px-4 py-2 rounded-md hover:bg-green-600 transition-colors"
      >
        提出
      </button>

      <RouterLink
        :to="`/assignment/${assignment.id}`"
        class="inline-block bg-green-500 text-white text-sm px-4 py-2 rounded-md hover:bg-green-600 transition-colors"
      >
        詳細
      </RouterLink>
      </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

// --- Props定義 ---
const props = defineProps({
  assignment: {
    type: Object,
    required: true
  }
})

// --- イベントハンドラ (提出ページを開く) ---
function openSubmissionPage() {
  if (props.assignment.url) {
    window.open(props.assignment.url, '_blank', 'noopener,noreferrer');
  }
}

// --- ヘルパー関数 ---
function formatDate(dateString) {
  if (!dateString) return '期限なし'
  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ja-JP', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
    }).format(date)
  } catch (e) {
    return '無効な日付'
  }
}

// --- Computedプロパティ ---
const statusText = computed(() => {
  return props.assignment.is_submitted ? '提出済み' : '未提出'
})

const statusClass = computed(() => {
  return props.assignment.is_submitted ? 'text-green-600' : 'text-red-600'
})
</script>