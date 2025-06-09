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
  <div>
    <div class="flex items-center justify-start pb-4">
      <div class="flex items-center gap-4">
        <button class="rounded-md border-2 border-gray-200 bg-white px-4 py-1.5 transition-colors hover:bg-gray-100 text-gray-600 font-semibold" @click="goToday">今日</button>
        <button class="rounded-md border-2 border-gray-200 bg-white px-4 py-1.5 transition-colors hover:bg-gray-100 text-gray-600 font-semibold" @click="prevMonth">＜</button>
        <button class="rounded-md border-2 border-gray-200 bg-white px-4 py-1.5 transition-colors hover:bg-gray-100 text-gray-600 font-semibold" @click="nextMonth">＞</button>
        <span class="text-xl text-gray-600 font-semibold">{{ year }}年 {{ month + 1 }}月</span>
      </div>
    </div>

    <div class="rounded-md overflow-hidden">
      <table class="w-full table-fixed border-collapse">
      <thead>
        <tr>
          <th v-for="(day, i) in days" :key="i" class="border border-gray-300 bg-gray-100 p-1.5 text-center text-gray-600">{{ day }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(week, i) in calendar" :key="i">
          <td v-for="dateObj in week" :key="dateObj.date"
              :class="[
                'border border-gray-300 text-left align-top p-1.5 bg-white', // text-center を text-left に変更
                { 'opacity-50': !dateObj.isCurrent }
              ]">
            <span
              :class="[
                isToday(dateObj.date)
                  ? 'bg-green-700 text-white rounded-full w-6 h-6 flex items-center justify-center font-semibold' // 円形表示と中央揃えのためのスタイル
                  : 'inline-block py-1 px-1.5 text-gray-600 font-semibold' // 通常の日付
              ]"
            >
              {{ dateObj.date.getDate() }}
            </span>
            <div class="relative h-12 p-1 text-left text-xs text-gray-600">
              <!-- 予定があればここに表示 (サンプル) -->
              <div class="mb-0.5 overflow-hidden text-ellipsis whitespace-nowrap">予定1</div>
              <div class="mb-0.5 overflow-hidden text-ellipsis whitespace-nowrap">予定2</div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    </div>
  </div>
</template>
