<script setup>
import Header from './components/Header.vue'
import SideBar from './components/SideBar.vue'
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <SideBar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <Header />
      <main class="flex-1 overflow-y-auto bg-gray-100 p-3 md:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>