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
      <AssignmentList :assignments="filteredAssignments" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from '@/api/axios' 
import AssignmentList from '@/components/assignment/AssignmentList.vue'

const assignments = ref([])
const isLoading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const filterUnsubmitted = ref(false)

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

watch(
  () => scrapingStore.completedMessages.length,
  (newLength) => {
    // 全てのタスクが完了したらデータを再取得
    if (newLength >= scrapingStore.totalTasks) {
      console.log('全スクレイピングが完了したため、課題データを再取得します。');
      fetchAssignments();
    }
  }
);

const filteredAssignments = computed(() => {
  if (!assignments.value) return []

  let filtered = assignments.value.filter(assignment => {
    const matchesSearch = assignment.title.toLowerCase().includes(searchQuery.value.toLowerCase())
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