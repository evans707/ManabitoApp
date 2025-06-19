<template>
  <Card class="flex flex-col">
    <div class="flex-grow">
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
          class="inline-flex items-center gap-2 bg-green-500 text-white text-sm font-medium py-2 px-4 rounded-lg hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-600"
        >
          <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M13.44 12.37a.75.75 0 10-1.06-1.06l-2.56 2.56V6.75a.75.75 0 00-1.5 0v7.12L5.62 9.69a.75.75 0 00-1.06 1.06l4.25 4.25a.75.75 0 001.06 0l4.25-4.25z" /><path d="M6.75 18a.75.75 0 000-1.5H13.25a.75.75 0 000 1.5H6.75z" /></svg>
          <span>提出</span>
        </button>
      </div>

      <button
        @click="handleDetailsClick"
        class="inline-flex items-center gap-2 bg-transparent text-gray-600 text-sm font-medium py-2 px-4 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <span>詳細を見る</span>
        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clip-rule="evenodd" /></svg>
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