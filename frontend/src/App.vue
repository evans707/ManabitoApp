<script setup>
import Header from './components/layouts/Header.vue'
import SideBar from './components/layouts/SideBar.vue'
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/axios';

const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    await apiClient.get('/csrf/');
    console.log('CSRF token has been successfully refreshed.');
    
    await authStore.checkAuthStatus();
    console.log('Auth status check complete.');
  } catch (error) {
    console.error('An error occurred during the onMounted setup:', error);
  }
});
</script>

<template>
  <div v-if="route.meta.layout === 'AuthLayout'" class="auth-layout-container">
    <RouterView />
  </div>

  <div v-else class="flex h-screen overflow-hidden default-layout-container">
    <SideBar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <Header />
      <main class="flex-1 overflow-y-auto bg-gray-100 p-3 md:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>