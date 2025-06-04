<script setup>
import AssignmentCard from '@/components/assignment/AssignmentCard.vue'
import { ref } from 'vue'

// テストデータ
const assignments = ref([
  { id: 1, title: '情報工学実験A', due_date: '2025年6月10日', status: '未提出' },
  { id: 2, title: '卒業論文テーマ提出', due_date: '2025年6月15日', status: '未提出' },
  { id: 3, title: '線形代数レポート', due_date: '2025年5月28日', status: '提出済み' }
])

</script>

<template>
  <div class="dashboard-page">
    <h2 class="text-2xl font-semibold mb-4">ホーム</h2> 
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <AssignmentCard
        v-for="assignment in assignments"
        :key="assignment.id"
        :id="assignment.id"
        :title="assignment.title"
        :due-date="assignment.due_date"
        :status="assignment.status"
      />
    </div>
  </div>
</template>