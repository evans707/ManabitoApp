<template>
  <div class="p-4 md:p-6">
    <div v-if="assignment">
    <h1 class="text-3xl font-semibold mb-4">{{ assignment.title }}</h1>
      <p class="text-lg text-gray-700 mb-2"><strong>提出期限:</strong> {{ assignment.dueDate }}</p>
      <p class="text-lg mb-4" :class="statusColorClass"><strong>ステータス:</strong> {{ assignment.status }}</p>
      
      <div class="bg-white p-6 rounded-xl shadow-lg">
        <h2 class="text-xl font-semibold text-gray-800 mb-3">課題詳細</h2>
        <p class="text-gray-600">
            ここに課題に関する詳細な説明や、提出用フォーム、関連資料などが表示されます。
            現在は課題ID: {{ assignmentId }} の詳細ページです。
        </p>
        </div>

      <button @click="$router.back()" class="mt-6 bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors">
        戻る
      </button>
    </div>
    <div v-else>
      <p class="text-xl text-gray-500">課題情報を読み込んでいます...</p>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const assignmentId = ref(route.params.id)
const assignment = ref(null)

// ダミーデータ
const allAssignments = {
  '1': { id: 1, title: '情報工学実験A', dueDate: '2025年6月10日', status: '未提出', description: '実験レポートを作成し、指定された形式で提出してください。' },
  '2': { id: 2, title: '卒業論文テーマ提出', dueDate: '2025年6月15日', status: '未提出', description: '卒業論文のテーマと概要を指導教員に提出してください。' },
  '3': { id: 3, title: '線形代数レポート', dueDate: '2025年5月28日', status: '提出済み', description: '教科書の章末問題を解き、解答プロセスと共に提出済みです。' }
}

function fetchAssignmentDetails(id) {
  console.log(`Fetching details for ID: ${id}`)
  const foundAssignment = allAssignments[id]
  if (foundAssignment) {
    assignment.value = { ...foundAssignment }
  } else {
    console.error(`Assignment with ID ${id} not found.`)
    assignment.value = null
  }
}

onMounted(() => {
  fetchAssignmentDetails(assignmentId.value)
})


watch(() => route.params.id, (newId) => {
  if (newId) {
    assignmentId.value = newId
    fetchAssignmentDetails(newId)
  }
})

const statusColorClass = computed(() => {
  if (!assignment.value) return ''
  return assignment.value.status === '提出済み' ? 'text-green-500' : 'text-gray-500'
})
</script>