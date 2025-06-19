<template>
  <Card>
    <h3
      class="text-lg font-semibold mb-2"
      :class="status === '提出済み' ? 'text-gray-600' : 'text-green-600'"
    >
      {{ title }}
    </h3>

    <p class="text-sm text-gray-600 mb-1">
      提出期限: {{ formattedDueDate }}
    </p>
    
    <p class="text-sm mb-1">
      <span class="text-gray-600">ステータス: </span>
      <span :class="statusColorClass">{{ status }}</span>
    </p>

    <div class="mt-4 flex items-center gap-2 justify-end">
      <button
        v-if="url && status !== '提出済み'"
        @click="openSubmissionPage"
        class="inline-block bg-green-500 text-white text-sm font-medium py-2 px-4 rounded-lg hover:bg-green-600 transition-colors"
      >
        提出
      </button>

      <button
        @click="handleDetailsClick"
        class="inline-block bg-green-500 text-white text-sm font-medium py-2 px-4 rounded-lg hover:bg-green-600 transition-colors"
      >
        詳細
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
  // urlプロパティを追加
  url: {
    type: String,
    default: null
  }
})

const router = useRouter()

// --- イベントハンドラ (提出ページを開く) ---
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
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${year}年${month}月${day}日 ${hours}:${minutes}`
  } catch (e) {
    console.error("Invalid date format:", props.dueDate, e)
    return '無効な日付'
  }
})

const statusColorClass = computed(() => {
  return props.status === '提出済み' ? 'text-green-600 font-bold' : 'text-red-600 font-bold'
})

// 関数名をより明確に変更
function handleDetailsClick() {
  router.push({ name: 'AssignmentDetails', params: { id: props.id } })
}
</script>