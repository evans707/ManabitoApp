<script setup>
import AssignmentCard from '@/components/assignment/AssignmentCard.vue'
import Calendar from '@/components/Calendar.vue'
import Card from '@/components/common/Card.vue'
import { ref, onMounted, watch, computed } from 'vue'
import apiClient from '@/api/axios'
import { useScrapingStore } from '@/stores/scrapingStore'

const assignments = ref([])
const courses = ref([])
const isLoading = ref(true)
const error = ref(null)
const scrapingStore = useScrapingStore()

// --- APIからデータを取得する関数 ---
const fetchAssignments = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const [assignmentsResponse, coursesResponse] = await Promise.all([
      apiClient.get('/assignments/'),
      apiClient.get('/courses/')
    ]);
    assignments.value = assignmentsResponse.data;
    courses.value = coursesResponse.data;

  } catch (err) {
    error.value = 'データの取得に失敗しました。ページを再読み込みしてください。';
  } finally {
    isLoading.value = false;
  }
}

// --- ライフサイクルフック ---
onMounted(() => {
  fetchAssignments();
})

// --- scrapingStore の状態を監視 ---
watch(
  () => scrapingStore.completedMessages.length,
  (newLength, oldLength) => {
    if (newLength > oldLength && newLength >= scrapingStore.totalTasks) {
      fetchAssignments();
    }
  }
);


// --- ヘルパー関数 ---
function getCourseName(courseId) {
  if (courseId === null || !courses.value.length) {
    return '（授業名なし）';
  }
  const course = courses.value.find(c => c.id === courseId);
  return course ? course.title : '（不明な授業）';
}


// --- topThreeAssignments の computed プロパティ ---
const topThreeAssignments = computed(() => {
  if (!assignments.value) return [];
  const now = new Date();
  const upcomingUnsubmitted = assignments.value
    .filter(a => !a.is_submitted && a.due_date && new Date(a.due_date) >= now)
    .sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
  if (upcomingUnsubmitted.length >= 3) {
    return upcomingUnsubmitted.slice(0, 3);
  }
  const needed = 3 - upcomingUnsubmitted.length;
  const submitted = assignments.value
    .filter(a => a.is_submitted)
    .sort((a, b) => {
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return new Date(b.due_date) - new Date(a.due_date)
    });
  const finalAssignments = [
    ...upcomingUnsubmitted,
    ...submitted.slice(0, needed)
  ];
  return finalAssignments;
})
</script>

<template>
  <div class="dashboard-page">
    <h2 class="text-2xl font-semibold mb-4 text-gray-700">ホーム</h2>

    <div v-if="isLoading" class="text-center py-10">
      <p class="text-gray-500">読み込み中...</p>
    </div>

    <div v-else-if="error" class="text-center py-10 text-red-500">
      <p>{{ error }}</p>
    </div>

    <div v-else>
      <div v-if="topThreeAssignments.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AssignmentCard
          v-for="assignment in topThreeAssignments"
          :key="assignment.id"
          :id="assignment.id"
          :title="assignment.title"
          :due-date="assignment.due_date"
          :status="assignment.is_submitted ? '提出済み' : '未提出'"
          :url="assignment.url"
          :course-name="getCourseName(assignment.course)"
        />
      </div>
    </div>

    <div class="mt-8">
      <Card>
        <Calendar :assignments="assignments" />
      </Card>
    </div>
  </div>
</template>