<script setup>
import Header from './components/Header.vue'
import SideBar from './components/SideBar.vue'
</script>

<template>
  <div class="app-layout">
    <SideBar />
    <div class="main-container">
      <Header />
      <main class="content-area">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* 最低限のレイアウト構造を示すためのスタイル */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden; /* HTMLの h-screen overflow-hidden に対応 */
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* HTMLの flex-1 flex flex-col overflow-hidden に対応 */
}

.content-area {
  flex: 1;
  overflow-y: auto; /* HTMLの overflow-y-auto に対応 */
  padding: 1rem; /* HTMLの p-3 md:p-6 に対応 */
  /* background-color: #f0f0f0; 雛形なので背景色はコメントアウト */
}
</style>