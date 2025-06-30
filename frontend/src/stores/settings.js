import { defineStore } from 'pinia'

export const useCalendarSettingsStore = defineStore('calendarSettings', {
  state: () => ({
    weekStartsOn: 0  // 0: 日曜, 1: 月曜
  }),
  actions: {
    setWeekStart(day) {
      this.weekStartsOn = day
    }
  }
})