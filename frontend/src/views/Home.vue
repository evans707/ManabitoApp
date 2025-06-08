<script setup>
import AssignmentCard from '@/components/assignment/AssignmentCard.vue'
import Calendar from '@/components/Calendar.vue'
import Card from '@/components/common/Card.vue'
import { ref } from 'vue'
import axios from 'axios'

const assignments = ref([])
const fetchAssignments = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/assignments/')
    assignments.value = response.data
  } catch (error) {
    console.error('課題の取得に失敗しました:', error)
  }
}

</script>

<template>
  <div class="dashboard-page">
    <h2 class="text-2xl font-semibold mb-4 text-gray-700">ホーム</h2> 
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
    <div class="mt-8">
      <Card>
        <Calendar />
      </Card>
    </div>
  </div>
</template>