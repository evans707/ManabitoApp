<template>
    <div class="calendar-page">
        <h1 class="text-2xl font-semibold mb-4 text-gray-700">カレンダー</h1>
        <Card>
        <Calendar :assignments="assignments" />
        </Card>
    </div>
</template>
<script setup>
import Calendar from '@/components/Calendar.vue'
import Card from '@/components/common/Card.vue'
import { ref, onMounted, computed } from 'vue'
import apiClient from '@/api/axios'

const assignments = ref([])
const isLoading = ref(true)
const error = ref(null)

const fetchAssignments = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await apiClient.get('/assignments/')
    assignments.value = response.data
  } catch (err) {
    console.error('課題の取得に失敗しました:', err)
    error.value = '課題の取得に失敗しました。ページを再読み込みしてください。'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAssignments()
})
</script>