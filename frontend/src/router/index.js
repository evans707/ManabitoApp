// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/Home.vue'
import CalendarView from '../views/CalendarView.vue'
import UpcomingAssignmentsView from '../views/UpcomingAssignmentsView.vue'
import AllAssignmentsView from '../views/AllAssignmentsView.vue'
import SettingsView from '../views/SettingsView.vue'
import AssignmentDetailsView from '../views/AssignmentDetails.vue'
import LoginView from '../views/LoginView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      guestOnly: true, 
      requiresAuth: false, 
      layout: 'AuthLayout' 
    }
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
  },
  {
    path: '/assignment/:id',
    name: 'AssignmentDetails',
    component: AssignmentDetailsView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router