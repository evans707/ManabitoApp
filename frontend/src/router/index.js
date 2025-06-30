// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/Home.vue'
import CalendarView from '../views/CalendarView.vue'
import UpcomingAssignmentsView from '../views/UpcomingAssignmentsView.vue'
import AllAssignmentsView from '../views/AllAssignmentsView.vue'
import SettingsView from '../views/SettingsView.vue'
import AssignmentDetailsView from '../views/AssignmentDetails.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from "@/views/ProfileView.vue";

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      guestOnly: true, 
      layout: 'AuthLayout' 
    }
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: CalendarView,
    meta: { requiresAuth: true }
  },
  {
    path: '/upcoming-assignments',
    name: 'UpcomingAssignments',
    component: UpcomingAssignmentsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/all-assignments',
    name: 'AllAssignments',
    component: AllAssignmentsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/assignment/:id',
    name: 'AssignmentDetails',
    component: AssignmentDetailsView,
    props: true,
    meta: { requiresAuth: true }
  },
    {
        path: '/profile',
        name: 'Profile',
        component: ProfileView,
        meta: { requiresAuth: true }
        
    }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const guestOnly = to.matched.some(record => record.meta.guestOnly)

  if (requiresAuth && !authStore.isUserAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (guestOnly && authStore.isUserAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router