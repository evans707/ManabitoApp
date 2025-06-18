<script setup>
import { ref, computed, defineProps } from 'vue'
import { 
  startOfMonth, 
  endOfMonth, 
  startOfWeek, 
  endOfWeek, 
  eachDayOfInterval,
  format,
  isSameMonth,
  isSameDay,
  parseISO
} from 'date-fns'

// --- Propsの定義 ---
// 親コンポーネントから課題データを受け取る
const props = defineProps({
  assignments: {
    type: Array,
    default: () => []
  }
})

// --- リアクティブな状態管理 ---
const today = new Date()
const currentMonth = ref(startOfMonth(today))

// --- 表示用データ (Computed Properties) ---
const year = computed(() => format(currentMonth.value, 'yyyy'))
const month = computed(() => format(currentMonth.value, 'M'))

// カレンダーに表示する日付の配列を生成
const calendarDays = computed(() => {
  // 表示月の最初と最後の日を取得
  const monthStart = startOfMonth(currentMonth.value)
  const monthEnd = endOfMonth(currentMonth.value)
  
  // カレンダーの表示開始日（月の初日を含む週の日曜日）と終了日（月の最終日を含む週の土曜日）を取得
  const startDate = startOfWeek(monthStart, { weekStartsOn: 0 }) // 週の始まりを日曜日に設定
  const endDate = endOfWeek(monthEnd, { weekStartsOn: 0 })

  // startDateからendDateまでのすべての日付の配列を生成
  return eachDayOfInterval({ start: startDate, end: endDate })
})

// --- イベントハンドラ ---
function nextMonth() {
  currentMonth.value = new Date(currentMonth.value.setMonth(currentMonth.value.getMonth() + 1))
}

function prevMonth() {
  currentMonth.value = new Date(currentMonth.value.setMonth(currentMonth.value.getMonth() - 1))
}

function goToday() {
  currentMonth.value = startOfMonth(today)
}

// --- ヘルパー関数 ---
function getAssignmentsForDate(date) {
  return props.assignments.filter(assignment => {
    // assignment.due_date (YYYY-MM-DD形式) をDateオブジェクトに変換して比較
    return assignment.due_date && isSameDay(parseISO(assignment.due_date), date)
  })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between pb-4">
      <h2 class="text-xl text-gray-700 font-semibold">{{ year }}年 {{ month }}月</h2>
      <div class="flex items-center gap-2">
        <button class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50" @click="goToday">今日</button>
        <button class="rounded-md border border-gray-300 bg-white p-1.5 transition-colors hover:bg-gray-50" @click="prevMonth" aria-label="前の月">
          <svg class="h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>
        </button>
        <button class="rounded-md border border-gray-300 bg-white p-1.5 transition-colors hover:bg-gray-50" @click="nextMonth" aria-label="次の月">
          <svg class="h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
        </button>
      </div>
    </div>

    <div class="grid grid-cols-7 border-l border-b border-gray-200">
      <div v-for="day in ['日', '月', '火', '水', '木', '金', '土']" :key="day" class="text-center text-sm font-medium text-gray-500 py-2 border-t border-r border-gray-200 bg-gray-50">{{ day }}</div>
      
      <div 
        v-for="day in calendarDays" 
        :key="day.toString()"
        :class="[
          'relative border-t border-r border-gray-200 h-28 p-1.5', 
          { 'bg-gray-50': !isSameMonth(day, currentMonth) } // 当月以外の日付の背景色
        ]"
      >
        <span
          :class="[
            'text-sm font-semibold',
            isSameDay(day, today) ? 'bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center' : '',
            isSameMonth(day, currentMonth) ? 'text-gray-700' : 'text-gray-400' // 当月以外の日付の文字色
          ]"
        >
          {{ format(day, 'd') }}
        </span>
        
        <div class="mt-1 space-y-1 overflow-y-auto max-h-16 text-xs">
          <div 
            v-for="assignment in getAssignmentsForDate(day)" 
            :key="assignment.id"
            class="bg-green-100 text-green-800 rounded px-1.5 py-0.5 text-ellipsis whitespace-nowrap overflow-hidden"
            :title="assignment.title"
          >
            {{ assignment.title }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>