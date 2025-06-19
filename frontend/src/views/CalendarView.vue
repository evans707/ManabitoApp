<template>
    <div class="calendar-page">
        <h1 class="text-2xl font-semibold mb-4 text-gray-700">カレンダー</h1>
        <Card>
        <Calendar />
        </Card>
    </div>
</template>
<script setup>
import Calendar from '@/components/Calendar.vue'
import Card from '@/components/common/Card.vue'
</script>