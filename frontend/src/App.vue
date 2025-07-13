<template>
  <div v-if="route.meta.layout === 'AuthLayout'" class="auth-layout-container">
    <RouterView />
  </div>

  <div v-else class="flex h-screen overflow-hidden default-layout-container">
    <SideBar />

    <div class="flex-1 flex flex-col overflow-hidden">
      <Header />

      <main class="flex-1 overflow-y-auto bg-gray-100 p-4 md:p-6 pb-20 md:pb-6">
        <RouterView />
      </main>
    </div>

    <BottomBar class="md:hidden" />
  </div>
</template>

<script setup>
import Header from './components/layouts/Header.vue'
import SideBar from './components/layouts/SideBar.vue'
import BottomBar from './components/layouts/BottomBar.vue'
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/axios';

const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    await apiClient.get('/csrf/');
    await authStore.checkAuthStatus();
  } catch (error) {}
});
</script>