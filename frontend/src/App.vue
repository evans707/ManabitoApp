<script setup>
import Header from './components/layouts/Header.vue'
import SideBar from './components/layouts/SideBar.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
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