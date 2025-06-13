<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-4">課題一覧</h1>
    <ul class="space-y-4">
      <li v-for="task in allAssignments" :key="task.id" class="pl-4 list-disc">
        <div class="font-semibold text-gray-800">{{ task.title }}</div>
        <div class="ml-4 text-sm text-gray-600">
          <p>提出期限：{{ task.dueDate }}</p>
          <p>ステータス：{{ task.status }}</p>
          <p>内容：{{ task.description }}</p>
          <RouterLink
            :to="`/assignment/${task.id}`"
            class="text-blue-600 hover:underline inline-block mt-1"
          >
            詳細
          </RouterLink>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

// ダミーデータ
const allAssignments = {
  '1': { id: 1, title: '情報工学実験A', dueDate: '2025年6月10日', status: '未提出', description: '実験レポートを作成し、指定された形式で提出してください。' },
  '2': { id: 2, title: '卒業論文テーマ提出', dueDate: '2025年6月15日', status: '未提出', description: '卒業論文のテーマと概要を指導教員に提出してください。' },
  '3': { id: 3, title: '線形代数レポート', dueDate: '2025年5月28日', status: '提出済み', description: '教科書の章末問題を解き、解答プロセスと共に提出済みです。' }
}
</script>
