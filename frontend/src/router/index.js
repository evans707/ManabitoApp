// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/Home.vue'
import CalendarView from '../views/CalendarView.vue'
import UpcomingAssignmentsView from '../views/UpcomingAssignmentsView.vue'
import AllAssignmentsView from '../views/AllAssignmentsView.vue'
import SettingsView from '../views/SettingsView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: CalendarView
  },
  {
    path: '/upcoming-assignments',
    name: 'UpcomingAssignments',
    component: UpcomingAssignmentsView
  },
  {
    path: '/all-assignments',
    name: 'AllAssignments',
    component: AllAssignmentsView
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Viteプロジェクトの場合
  // history: createWebHistory(process.env.BASE_URL), // Vue CLIプロジェクトの場合
  routes
})

export default router