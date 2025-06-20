<template>
  <div class="p-4 md:p-6">
    <div v-if="isLoading" class="text-center py-10">
      <p class="text-xl text-gray-500">課題情報を読み込んでいます...</p>
    </div>
    
    <div v-else-if="error" class="text-center py-10 text-red-500">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="assignment">
      <h1 class="text-3xl font-semibold mb-4">{{ assignment.title }}</h1>

      <p class="text-lg text-gray-700 mb-2">
        <strong>提出期限:</strong> 
        <span v-if="formattedDueDate">{{ formattedDueDate }}</span>
        <span v-else>なし</span>
      </p>
      
      <p class="text-lg mb-4" :class="statusColorClass">
        <span class="text-gray-600">ステータス:</span> 
        <span>{{ assignmentStatus }}</span>
      </p>
      
      <div class="bg-white p-6 rounded-xl shadow-lg">
        <h2 class="text-xl font-semibold text-gray-800 mb-3">課題詳細</h2>
        <div class="prose max-w-none">
          <p v-if="assignment.content">{{ assignment.content }}</p>
          <p v-else>詳細な説明はありません。</p>
          <p v-if="assignment.url">
            <strong>関連リンク:</strong>
            <a :href="assignment.url" target="_blank" rel="noopener noreferrer" class="text-green-600 hover:underline">
              {{ assignment.url }}
            </a>
          </p>
        </div>
      </div>

      <button @click="$router.back()" class="mt-6 bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors">
        戻る
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'
import apiClient from '@/api/axios'

const route = useRoute()
const assignment = ref(null)
const isLoading = ref(true)
const error = ref(null)

const fetchAssignmentDetails = async (id) => {
  isLoading.value = true
  error.value = null
  assignment.value = null

  try {
    const response = await apiClient.get(`/assignments/${id}/`)
    assignment.value = response.data
  } catch (err) {
    console.error(`課題(ID: ${id})の取得に失敗しました:`, err)
    error.value = '課題情報の取得に失敗しました。URLが正しいか確認してください。'
  } finally {
    isLoading.value = false
  }
}

const formattedDueDate = computed(() => {
  if (!assignment.value || !assignment.value.due_date) {
    return null
  }
  try {
    return format(new Date(assignment.value.due_date), 'yyyy年M月d日 HH:mm', { locale: ja })
  } catch (e) {
    console.error('日付のフォーマットに失敗しました:', e)
    return '無効な日付'
  }
})

// --- ステータスを is_submitted から動的に決定 ---
const assignmentStatus = computed(() => {
  if (!assignment.value) return '不明'
  // is_submitted が true なら「提出済み」、false なら「未提出」
  return assignment.value.is_submitted ? '提出済み' : '未提出'
})

// --- ステータスの色を動的に決定 ---
const statusColorClass = computed(() => {
  if (!assignment.value) return ''
  
  // assignmentStatus の値に応じて色を返す
  switch (assignmentStatus.value) {
    case '提出済み':
      return 'text-green-600 font-bold' // 提出済みは緑色
    case '未提出':
      return 'text-red-600 font-bold' // 未提出は赤色
    default:
      return 'text-gray-600'
  }
})

onMounted(() => {
  fetchAssignmentDetails(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchAssignmentDetails(newId)
  }
})
</script>