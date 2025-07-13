<template>
  <Card class="flex flex-col">
    <div class="flex-grow">
      <p v-if="courseName" class="text-sm text-gray-600 mb-1">{{ courseName }}</p>
      <h3
        class="text-lg font-semibold mb-2"
        :class="status === '提出済み' ? 'text-gray-500' : 'text-green-700'"
      >
        {{ title }}
      </h3>
      <div class="space-y-1 text-sm text-gray-600">
        <p>
          <strong>提出期限:</strong> {{ formattedDueDate }}
        </p>
        <p>
          <strong>ステータス:</strong>
          <span :class="statusColorClass" class="font-bold">{{ status }}</span>
        </p>
      </div>
    </div>

    <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
      <div>
        <button
          v-if="url && status !== '提出済み'"
          @click="openSubmissionPage"
          class="inline-flex items-center gap-2 bg-green-700 text-white text-sm font-medium py-2 px-4 rounded-lg hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-600"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
          <span>提出</span>
        </button>
      </div>

      <button
        @click="handleDetailsClick"
        class="inline-flex items-center gap-2 bg-transparent text-gray-600 text-sm font-medium py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <span>詳細を見る</span>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3" /></svg>
      </button>
    </div>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from '../common/Card.vue'

const props = defineProps({
  id: {
    type: [String, Number],
    required: true
  },
  title: {
    type: String,
    required: true
  },
  dueDate: {
    type: String,
    default: null 
  },
  status: {
    type: String,
    default: null
  },
  url: {
    type: String,
    default: null
  },
  courseName: {
    type: String,
    default: null
  }
})

const router = useRouter()

function openSubmissionPage() {
  if (props.url) {
    window.open(props.url, '_blank', 'noopener,noreferrer');
  }
}

const formattedDueDate = computed(() => {
  if (!props.dueDate) {
    return '期限なし'
  }
  try {
    const date = new Date(props.dueDate)
    return new Intl.DateTimeFormat('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  } catch (e) {
    console.error("Invalid date format:", props.dueDate, e)
    return '無効な日付'
  }
})

const statusColorClass = computed(() => {
  return props.status === '提出済み' ? 'text-green-600' : 'text-red-600'
})

function handleDetailsClick() {
  router.push({ name: 'AssignmentDetails', params: { id: props.id } })
}
</script>