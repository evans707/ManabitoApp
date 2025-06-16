<template>
  <div class="AllAssignments-page">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold text-gray-800">課題一覧</h1>
      <div class="flex items-center gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="キーワード検索"
          class="border rounded px-2 py-1 text-sm"
        />
        <label class="flex items-center gap-1 text-sm text-gray-700">
          <input type="checkbox" v-model="filterUnsubmitted" />
          未提出のみ表示
        </label>
      </div>
    </div>

    <div v-for="task in filteredAssignments" :key="task.id" class="bg-white rounded-md shadow p-4 border border-gray-200 mb-4">
      <h2 class="text-lg font-semibold text-gray-800">{{ task.title }}</h2>
      <p class="text-sm text-gray-600 mt-1">提出期限：{{ task.dueDate }}</p>
      <p class="text-sm mt-1">
        ステータス：
        <span :class="task.status === '提出済み' ? 'text-green-600 font-bold' : 'text-red-600 font-bold'">
          {{ task.status }}
        </span>
      </p>
      <p class="text-sm text-gray-600 mt-1">内容：{{ task.description }}</p>

      <div class="mt-3">
        <RouterLink
          :to="`/assignment/${task.id}`"
          class="inline-block bg-green-700 text-white text-sm px-4 py-1.5 rounded hover:bg-green-800"
        >
          詳細を見る
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const filterUnsubmitted = ref(false)

const allAssignments = {
  '1': { id: 1, title: '情報工学実験A', dueDate: '2025年6月10日', status: '未提出', description: 'レポートを提出してください。' },
  '2': { id: 2, title: '卒業論文テーマ提出', dueDate: '2025年6月15日', status: '未提出', description: '概要を提出してください。' },
  '3': { id: 3, title: '線形代数レポート', dueDate: '2025年5月28日', status: '提出済み', description: '問題を解いて提出済みです。' }
}

function parseJapaneseDate(str) {
  const match = str.match(/(\d{4})年?(\d{1,2})月(\d{1,2})日?/)
  if (!match) return new Date(NaN)
  const [, y, m, d] = match
  return new Date(`${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`)
}

const sortedAssignments = computed(() =>
  Object.values(allAssignments).sort((a, b) =>
    parseJapaneseDate(a.dueDate) - parseJapaneseDate(b.dueDate)
  )
)

const filteredAssignments = computed(() => {
  return sortedAssignments.value.filter(task => {
    const matchesSearch =
      task.title.includes(searchQuery.value) ||
      task.description.includes(searchQuery.value)
    const matchesStatus = filterUnsubmitted.value ? task.status === '未提出' : true
    return matchesSearch && matchesStatus
  })
})
</script>
