<template>
  <Card>
    <h3
      class="text-lg font-semibold mb-2"
      :class="status === '提出済み' ? 'text-gray-600' : 'text-green-600'"
    >
      {{ title }}
    </h3>
    <p class="text-sm text-gray-600 mb-1">提出期限: {{ due_date }}</p>
    <p class="text-sm mb-1" :class="statusColorClass">
      ステータス: {{ status }}
    </p>
    <button
      :class="buttonClass"
      class="mt-4 font-medium py-2 px-4 rounded-lg transition-colors w-full"
      :disabled="status === '提出済み'"
      @click="handleButtonClick"
    >
      {{ buttonText }}
    </button>
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
  due_date: {
    type: String,
    required: true
  },
  status: {
    type: String,
    required: true,
    validator: (value) => ['未提出', '提出済み'].includes(value)
  }
})

const router = useRouter()

const statusColorClass = computed(() => {
  return props.status === '提出済み' ? 'text-green-500' : 'text-gray-500'
})

const buttonText = computed(() => {
  return props.status === '提出済み' ? '提出済み' : '詳細を見る'
})

const buttonClass = computed(() => {
  if (props.status === '提出済み') {
    return 'bg-gray-300 text-gray-700 cursor-not-allowed'
  }
  return 'bg-green-500 hover:bg-green-600 text-white'
})

function handleButtonClick() {
  if (props.status !== '提出済み') {
    router.push({ name: 'AssignmentDetails', params: { id: props.id } })
  }
}
</script>