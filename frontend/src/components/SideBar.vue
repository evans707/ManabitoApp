// src/components/SideBar.vue
<template>
  <aside class="sidebar-navigation">
    <div class="user-profile">
      <p>学籍番号: S12345</p>
    </div>
    <nav>
      <ul>
        <li><RouterLink to="/">ダッシュボード (ホーム)</RouterLink></li>
        <li><RouterLink to="/calendar">カレンダー</RouterLink></li>
        <li><RouterLink to="/upcoming-assignments">直近の課題</RouterLink></li>
        <li><RouterLink to="/all-assignments">すべての課題</RouterLink></li>
      </ul>
    </nav>
    <div class="sidebar-footer">
      <ul>
        <li><RouterLink to="/settings">設定</RouterLink></li>
        <li><a href="#" @click.prevent="logout">ログアウト</a></li>
      </ul>
    </div>
  </aside>
</template>

<script setup>
import { RouterLink } from 'vue-router'

function logout() {
  alert('ログアウト処理（仮）');
}
</script>

<style scoped>
.sidebar-navigation {
  width: 220px; /* HTMLの w-20 hover:w-64 の中間的な幅で固定 */
  padding: 1rem;
  /* background-color: #333; */ /* HTMLの bg-green-700 のような濃い色を想定 */
  /* color: white; */
  height: 100%;
  display: flex;
  flex-direction: column;
}
.user-profile {
  padding: 1rem 0;
  margin-bottom: 1rem;
  /* border-bottom: 1px solid #555; */
}
.sidebar-navigation nav {
  flex-grow: 1;
}
.sidebar-navigation ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-navigation li a {
  display: block;
  padding: 0.75rem 1rem;
  /* color: white; */
  text-decoration: none;
  border-radius: 4px;
}
.sidebar-footer {
  margin-top: auto;
}
</style>