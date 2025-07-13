<template>
  <div class="assignment-details-page">
    <h2 class="text-2xl font-semibold mb-4 text-gray-700">課題詳細</h2>

    <div v-if="isLoading" class="text-center py-20">
      <p class="text-gray-500">読み込んでいます...</p>
    </div>

    <div v-else-if="error" class="text-center py-12 text-red-600 bg-red-50 p-4 rounded-lg">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="assignment">
      <Card>
        <div class="p-2">
          <div class="mb-4">
            <p v-if="courseName" class="text-sm text-gray-500 font-medium">{{ courseName }}</p>
            <h1 class="text-2xl font-bold text-gray-800 mt-1">{{ assignment.title }}</h1>
          </div>

          <div class="space-y-2 text-md text-gray-700 mb-6">
            <div class="flex items-center gap-3">
              <strong class="w-24 text-gray-500">提出期限</strong>
              <span>:</span>
              <span v-if="formattedDueDate">{{ formattedDueDate }}</span>
              <span v-else>なし</span>
            </div>
            <div class="flex items-center gap-3">
              <strong class="w-24 text-gray-500">ステータス</strong>
              <span>:</span>
              <span :class="statusColorClass">{{ assignmentStatus }}</span>
            </div>
          </div>

          <div v-if="assignment.content || assignment.url" class="mt-6 pt-6 border-t border-gray-200">
            <div class="prose max-w-none text-gray-600">
              <p v-if="assignment.content">{{ assignment.content }}</p>
            </div>
          </div>
        </div>
      </Card>

      <div class="mt-6 flex items-center justify-end gap-3">
        <button @click="$router.back()" class="bg-white border border-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors">
          戻る
        </button>
        <button
          v-if="assignment.url && assignmentStatus !== '提出済み'"
          @click="openSubmissionPage"
          class="inline-flex items-center gap-2 bg-green-600 text-white font-medium py-2 px-4 rounded-lg hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
          <span>提出</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'
import apiClient from '@/api/axios'
import Card from '@/components/common/Card.vue'

const route = useRoute()
const assignment = ref(null)
const courses = ref([])
const isLoading = ref(true)
const error = ref(null)

const fetchData = async (id) => {
  isLoading.value = true
  error.value = null
  assignment.value = null

  try {
    const [assignmentResponse, coursesResponse] = await Promise.all([
      apiClient.get(`/assignments/${id}/`),
      apiClient.get('/courses/')
    ]);
    assignment.value = assignmentResponse.data;
    courses.value = coursesResponse.data;
  } catch (err) {
    console.error(`データ(ID: ${id})の取得に失敗しました:`, err)
    error.value = '情報の取得に失敗しました。URLが正しいか確認してください。'
  } finally {
    isLoading.value = false
  }
}

const courseName = computed(() => {
  if (!assignment.value || !assignment.value.course || !courses.value.length) {
    return null
  }
  const course = courses.value.find(c => c.id === assignment.value.course)
  return course ? course.title : '不明な授業'
})

const formattedDueDate = computed(() => {
  if (!assignment.value || !assignment.value.due_date) {
    return null
  }
  try {
    return format(new Date(assignment.value.due_date), 'yyyy年M月d日 HH:mm', { locale: ja })
  } catch (e) {
    return '無効な日付'
  }
})

const assignmentStatus = computed(() => {
  if (!assignment.value) return '不明'
  return assignment.value.is_submitted ? '提出済み' : '未提出'
})

const statusColorClass = computed(() => {
  switch (assignmentStatus.value) {
    case '提出済み': return 'text-green-600 font-bold'
    case '未提出': return 'text-red-600 font-bold'
    default: return 'text-gray-600'
  }
})

function openSubmissionPage() {
  if (assignment.value && assignment.value.url) {
    window.open(assignment.value.url, '_blank', 'noopener,noreferrer');
  }
}

onMounted(() => {
  fetchData(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchData(newId)
  }
})
</script>