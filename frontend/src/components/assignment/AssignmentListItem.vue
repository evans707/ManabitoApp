<template>
  <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:bg-gray-50 transition-colors">
    <div class="flex-grow font-semibold text-gray-800 self-start md:self-center">
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
        v-if="assignment.url && statusText !== '提出済み'"
        @click="openSubmissionPage"
        class="inline-flex items-center justify-center gap-2 bg-green-500 text-white text-sm font-medium h-9 w-24 rounded-md hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z" /><path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z" /></svg>
        <span>提出</span>
      </button>

      <RouterLink
        :to="`/assignment/${assignment.id}`"
        class="inline-flex items-center justify-center gap-1 bg-transparent text-gray-700 text-sm font-medium h-9 w-24 rounded-md hover:bg-gray-100 transition-colors border border-gray-300"
      >
        <span>詳細</span>
        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.22 5.22a.75.75 0 011.06 0l4.25 4.25a.75.75 0 010 1.06l-4.25 4.25a.75.75 0 01-1.06-1.06L11.94 10 8.22 6.28a.75.75 0 010-1.06z" clip-rule="evenodd" /></svg>
      </RouterLink>
      </div>
  </div>
</template>

<script setup>
// このセクションのコードは変更ありません
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  assignment: {
    type: Object,
    required: true
  }
})

function openSubmissionPage() {
  if (props.assignment.url) {
    window.open(props.assignment.url, '_blank', 'noopener,noreferrer');
  }
}

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

const statusText = computed(() => {
  return props.assignment.is_submitted ? '提出済み' : '未提出'
})

const statusClass = computed(() => {
  return props.assignment.is_submitted ? 'text-green-600' : 'text-red-600'
})
</script>