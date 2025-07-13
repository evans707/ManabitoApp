<template>
  <div>
    <div v-if="assignments.length === 0" class="text-center py-12">
      <p class="text-gray-500">表示する課題はありません。</p>
    </div>
    
    <div v-else class="space-y-3">
      <AssignmentListItem 
        v-for="assignment in assignments" 
        :key="assignment.id"
        :assignment="assignment"
        :course-name="assignment.course_name"
      />
    </div>
  </div>
</template>

<script setup>
import AssignmentListItem from './AssignmentListItem.vue'

defineProps({
  assignments: {
    type: Array,
    required: true
  }
})
</script>