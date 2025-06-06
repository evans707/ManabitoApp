<script setup>
import { ref, computed } from 'vue'

const today = new Date()
const currentData = ref(new Date(today.getFullYear(), today.getMonth(), 1))

const year = computed(() => currentData.value.getFullYear())
const month = computed(() => currentData.value.getMonth())

const days = ['日', '月', '火', '水', '木', '金', '土']

function goToday() {
  currentData.value = new Date(today.getFullYear(), today.getMonth(), 1)
}

function prevMonth() {
  currentData.value = new Date(year.value, month.value - 1, 1)
}

function nextMonth() {
  currentData.value = new Date(year.value, month.value + 1, 1)
}

const calendar = computed(() => {
  const firstDay = new Date(year.value, month.value, 1)
  const lastDay = new Date(year.value, month.value + 1, 0)
  const startDay = firstDay.getDay()
  const totalDays = lastDay.getDate()

  const result = []
  let week = []

  // 前月末の日付
  for (let i = 0; i < startDay; i++) {
    week.push({ date: new Date(year.value, month.value, -startDay + i + 1), isCurrent: false })
  }

  // 今月
  for (let i = 1; i <= totalDays; i++) {
    week.push({ date: new Date(year.value, month.value, i), isCurrent: true })
    if (week.length === 7) {
      result.push(week)
      week = []
    }
  }

  // 翌月
  let day = 1;
  while (week.length < 7) {
    week.push({ date: new Date(year.value, month.value + 1, day), isCurrent: false });
    day++;
  }
  if (week.length) result.push(week)

  return result
})

function isToday(dateObj) {
  return (
    dateObj.getFullYear() === today.getFullYear() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getDate() === today.getDate()
  )
}
</script>

<template>
  <div class="calendar">
    <div class="calendar-header">
      <div class="nav-center">
        <button class="button" @click="goToday">今日</button>
        <button class="button" @click="prevMonth">＜</button>
        <button class="button" @click="nextMonth">＞</button>
        <span class="current-month">{{ year }}年 {{ month + 1 }}月</span>
      </div>
    </div>

    <table class="calendar-table">
      <thead>
        <tr class="daily-cell">
          <th v-for="(day, i) in days" :key="i">{{ day }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(week, i) in calendar" :key="i">
          <td v-for="dateObj in week" :key="dateObj.date" class="date-cell">
            <span
              :class="[
                'date-number',
                { today: isToday(dateObj.date) },
                { 'other-month': !dateObj.isCurrent }
              ]"
            >
              {{ dateObj.date.getDate() }}
            </span>
            <div class="event-cell" :class="{ 'other-month': !dateObj.isCurrent }">
              <!-- 予定があればここに表示 -->
              <div class="event-item">予定1</div>
              <div class="event-item">予定2</div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.calendar-header {
  position: relative;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  background-color: white;
  padding: 1rem;
  color: black;
}

.nav-center {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.button{
  background-color: white;
  border: 2px solid #e6e6e6;
  border-radius: 6px;
  padding: 0.5rem 1rem;
}

.current-month {
  font-size: 1.2rem;
  color: black;
}

.calendar-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

th, td {
  border: 1px solid #ddd;
  text-align: center;
  vertical-align: top;
  padding: 6px;
}

.daily-cell th {
  background-color: #e6e6e6;
  color: black;
}

.date-cell {
  background-color: #ffffff;
  height: 40px;
  color: black;
}

.date-number {
  display: inline-block;
  padding: 4px 6px;
  background-color: #ffffff;
  color: black;
}

.today {
  background-color: #028760;
  color: white;
  border-radius: 50%;
  padding: 4px 8px;
  display: inline-block;
}

.other-month {
  opacity: 0.3;
}

.event-cell {
  background-color: white;
  height: 80px;
  font-size: 0.8rem;
  text-align: left;
  padding: 4px;
  position: relative;
  color: black;
}

.event-item {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}


</style>
