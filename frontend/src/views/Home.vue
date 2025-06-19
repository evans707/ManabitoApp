<script setup>
import AssignmentCard from '@/components/assignment/AssignmentCard.vue'
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

const topThreeAssignments = computed(() => {
  const now = new Date()

  return assignments.value
    .filter(assignment => {
      if (!assignment.due_date) {
        return false
      }
      return new Date(assignment.due_date) > now
    })
    .sort((a, b) => {
      return new Date(a.due_date) - new Date(b.due_date)
    })
    .slice(0, 3)
})
</script>

<template>
  <div class="dashboard-page">
    <h2 class="text-2xl font-semibold mb-4 text-gray-700">ホーム</h2>

    <div v-if="isLoading" class="text-center py-10">
      <p class="text-gray-500">読み込み中...</p>
    </div>

    <div v-else-if="error" class="text-center py-10 text-red-500">
      <p>{{ error }}</p>
    </div>

    <div v-else>
      <div v-if="topThreeAssignments.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AssignmentCard
          v-for="assignment in topThreeAssignments"
          :key="assignment.id"
          :id="assignment.id"
          :title="assignment.title"
          :due-date="assignment.due_date"
          :status="assignment.is_submitted ? '提出済み' : '未提出'"
          :url="assignment.url"
        />
      </div>
      <div v-else class="text-center py-10">
        <p class="text-gray-500">現在、登録されている課題はありません。</p>
      </div>
    </div>

    <div class="mt-8">
      <Card>
        <Calendar :assignments="assignments" /> 
      </Card>
    </div>
  </div>
</template>