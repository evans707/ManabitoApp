<template>
  <aside class="bg-green-700 text-white w-20 hover:w-64 transition-all duration-300 ease-in-out flex flex-col space-y-1 py-4 overflow-hidden group">
    <!-- ユーザーアイコンと学籍番号 -->
    <RouterLink to="/profile" class="flex items-center space-x-3 px-4 py-3 hover:bg-green-600 rounded-lg mx-2 transition-colors">
      <!-- 
        TODO: プロフィールページ (to="/profile") は未作成なので、必要に応じて作成してください。
       -->
      <span class="h-7 w-7 shrink-0" v-html="userIconSvg"></span>
      <span class="font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200 ease-in-out whitespace-nowrap">
        学籍番号: {{ authStore.currentUser?.university_id || '未ログイン' }}
      </span>
    </RouterLink>

    <!-- ナビゲーションメニュー -->
    <nav class="flex-grow px-2 space-y-1">
      <SidebarItem to="/" label="ホーム" :iconSvg="homeIconSvg" />
      <SidebarItem to="/calendar" label="カレンダー" :iconSvg="calendarIconSvg" />
      <SidebarItem to="/upcoming-assignments" label="直近の課題" :iconSvg="clockIconSvg" />
      <SidebarItem to="/all-assignments" label="すべての課題" :iconSvg="folderIconSvg" />
    </nav>

    <!-- 設定とログアウト -->
    <div class="px-2 space-y-1">
      <SidebarItem to="/settings" label="設定" :iconSvg="settingsIconSvg" />
      <a href="#" @click.prevent="handleLogout" class="flex items-center space-x-3 px-4 py-3 hover:bg-green-600 rounded-lg transition-colors">
        <span class="h-6 w-6 shrink-0" v-html="logoutIconSvg"></span>
        <span class="opacity-0 group-hover:opacity-100 transition-opacity duration-200 ease-in-out whitespace-nowrap">
          ログアウト
        </span>
      </a>
    </div>
  </aside>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import SidebarItem from '../SideBarItem.vue'
import { useAuthStore } from '@/stores/auth'

// SVGアイコンの定義 (HTML文字列として)
const userIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`
const homeIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955a.75.75 0 011.06 0l8.955 8.955M11.25 10.5v6.75a.75.75 0 00.75.75h3.75a.75.75 0 00.75-.75V10.5m-6.75 0V6.75A.75.75 0 016 6h1.5a.75.75 0 01.75.75v3.75m-1.5 0h1.5m-1.5 0H6m6 0h1.5m0 0V6.75A.75.75 0 0016.5 6h-1.5a.75.75 0 00-.75.75v3.75m0 0H15m0 0h1.5m0 0H18m-3 .75H9m6.75 0a2.25 2.25 0 012.25 2.25v3.75a2.25 2.25 0 01-2.25 2.25H9a2.25 2.25 0 01-2.25-2.25V15a2.25 2.25 0 012.25-2.25h6.75z" /></svg>`
const calendarIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>`
const clockIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`
const folderIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>`
const settingsIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`
const logoutIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M15.75 9l-3.75 3.75M15.75 9h-3.75m3.75 0v3.75" /></svg>`
const authStore = useAuthStore();

async function handleLogout() {
  await authStore.logout();
}
</script>