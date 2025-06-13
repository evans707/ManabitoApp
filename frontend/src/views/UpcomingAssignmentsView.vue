<template>
  <div class="UpcomingAssignments-page">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">直近の課題</h1>

    <div v-for="task in allAssignments" :key="task.id" class="bg-white rounded-md shadow p-4 mb-4">
      <h2 class="text-lg font-semibold text-gray-800">{{ task.title }}</h2>
      <p class="text-sm text-gray-600 mt-1"
        v-if="task.status !== '提出済み'">
        <span :class="{
          'text-red-600 font-bold': getDaysLeft(task.dueDate) <= 0,
          'text-yellow-600 font-semibold': getDaysLeft(task.dueDate) === 0,
          'text-gray-800': getDaysLeft(task.dueDate) > 0
        }">
          {{ getDaysLeft(task.dueDate) < 0 ? '締切過ぎ': getDaysLeft(task.dueDate) === 0 ? '今日締切' : `あと ${getDaysLeft(task.dueDate)} 日`}}
        </span>
      </p>
      <p class="text-sm text-gray-600 mt-1">提出期限：{{ task.dueDate }}</p>
      <p class="text-sm text-gray-600 mt-1">ステータス：{{ task.status }}</p>
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
import { computed } from 'vue'

// ダミーデータ
const allAssignments = {
  '1': { id: 1, title: '情報工学実験A', dueDate: '2025年6月10日', status: '未提出', description: '実験レポートを作成し、指定された形式で提出してください。' },
  '2': { id: 2, title: '卒業論文テーマ提出', dueDate: '2025年6月15日', status: '未提出', description: '卒業論文のテーマと概要を指導教員に提出してください。' },
  '3': { id: 3, title: '線形代数レポート', dueDate: '2025年5月28日', status: '提出済み', description: '教科書の章末問題を解き、解答プロセスと共に提出済みです。' }
}

//日付フォーマット変更
function parseJapaneseDate(japaneseDateStr) {
  const match = japaneseDateStr.match(/(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日/)
  if (!match) return null
  const [_, year, month, day] = match
  return new Date(`${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`)
}

//締め切り早い順に並び替え
const assignments = computed(() =>
  Object.values(allAssignments).sort((a, b) =>
    parseJapaneseDate(a.dueDate) - parseJapaneseDate(b.dueDate)
  )
)

//あと何日か計算
function getDaysLeft(japaneseDateStr) {
  const dueDate = parseJapaneseDate(japaneseDateStr)
  if (!dueDate) return NaN

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  dueDate.setHours(0, 0, 0, 0)

  const diffTime = dueDate - today
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

</script>
