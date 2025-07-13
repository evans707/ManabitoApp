<template>
  <div class="all-assignments-page">
    <div class="flex flex-col md:flex-row justify-between md:items-center mb-6 gap-4">
      <h2 class="text-2xl font-semibold text-gray-700">課題一覧</h2>
      <div class="flex items-center gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="キーワード検索"
          class="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:ring-green-500 focus:border-green-500"
        />
        <label class="flex items-center gap-2 text-sm text-gray-700 select-none">
          <input type="checkbox" v-model="filterUnsubmitted" class="rounded text-green-600 focus:ring-green-500" />
          未提出のみ表示
        </label>
      </div>
    </div>

    <div v-if="isLoading" class="text-center py-12">
      <p class="text-gray-500">課題を読み込んでいます...</p>
    </div>

    <div v-else-if="error" class="text-center py-12 text-red-600 bg-red-50 p-4 rounded-lg">
      <p>{{ error }}</p>
    </div>

    <div v-else>
      <AssignmentList :assignments="filteredAssignments" :courses="courses" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from '@/api/axios'
import AssignmentList from '@/components/assignment/AssignmentList.vue'
import { useScrapingStore } from '@/stores/scrapingStore'

// --- リアクティブな状態管理 ---
const assignments = ref([])
const courses = ref([]) // courses を追加
const isLoading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const filterUnsubmitted = ref(false)
const scrapingStore = useScrapingStore() // ストアのインスタンスを作成

// --- APIからデータを取得する関数 ---
const fetchAssignmentsAndCourses = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [assignmentsResponse, coursesResponse] = await Promise.all([
      apiClient.get('/assignments/'),
      apiClient.get('/courses/')
    ]);
    assignments.value = assignmentsResponse.data
    courses.value = coursesResponse.data
  } catch (err) {
    console.error('データの取得に失敗しました:', err)
    error.value = 'データの取得に失敗しました。ページを再読み込みしてください。'
  } finally {
    isLoading.value = false
  }
}

// --- ライフサイクルフック ---
onMounted(() => {
  fetchAssignmentsAndCourses()
})

// --- scrapingStore の状態を監視 ---
watch(
  () => scrapingStore.completedMessages.length,
  (newLength, oldLength) => {
    if (newLength > oldLength && newLength >= scrapingStore.totalTasks) {
      console.log('全スクレイピングが完了したため、課題データを再取得します。');
      fetchAssignmentsAndCourses();
    }
  }
);

// --- computed プロパティ ---
const filteredAssignments = computed(() => {
  if (!assignments.value) return []

  let assignmentsWithCourseNames = assignments.value.map(assignment => {
    const course = courses.value.find(c => c.id === assignment.course)
    return {
      ...assignment,
      course_name: course ? course.title : '（授業名なし）'
    }
  })

  let filtered = assignmentsWithCourseNames.filter(assignment => {
    const matchesSearch =
      assignment.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      assignment.course_name.toLowerCase().includes(searchQuery.value.toLowerCase())

    const matchesStatus = filterUnsubmitted.value ? !assignment.is_submitted : true
    return matchesSearch && matchesStatus
  })

  // 提出期限でソート
  filtered.sort((a, b) => {
    if (a.is_submitted && !b.is_submitted) return 1
    if (!a.is_submitted && b.is_submitted) return -1
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(b.due_date) - new Date(a.due_date)
  })

  return filtered
})
</script>