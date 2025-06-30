<template>
  <aside class="bg-green-700 text-white w-20 hover:w-64 transition-all duration-300 ease-in-out flex flex-col space-y-1 py-4 overflow-hidden group">
    <RouterLink to="/profile" class="flex items-center space-x-3 px-4 py-3 hover:bg-green-600 rounded-lg mx-2 transition-colors">
      <span class="h-7 w-7 shrink-0">
        <IconAccount />
      </span>
      <span class="font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200 ease-in-out whitespace-nowrap">
        学籍番号: {{ authStore.currentUser?.university_id || '未ログイン' }}
      </span>
    </RouterLink>

    <nav class="flex-grow px-2 space-y-1">
      <SidebarItem to="/" label="ホーム">
        <IconHome />
      </SidebarItem>
      <SidebarItem to="/calendar" label="カレンダー">
        <IconCalendar />
      </SidebarItem>
      <SidebarItem to="/all-assignments" label="すべての課題">
        <IconAssingment />
      </SidebarItem>
    </nav>

    <div class="px-2 space-y-1">
      <SidebarItem to="/settings" label="設定">
        <IconSetting />
      </SidebarItem>
      <a href="#" @click.prevent="handleLogout" class="flex items-center space-x-3 px-4 py-3 hover:bg-green-600 rounded-lg transition-colors">
        <span class="h-6 w-6 shrink-0">
          <IconLogout />
        </span>
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

// アイコンコンポーネントをインポート
import IconAccount from '@/components/icons/IconAccount.vue'
import IconHome from '@/components/icons/IconHome.vue'
import IconCalendar from '@/components/icons/IconCalendar.vue'
import IconAssingment from '@/components/icons/IconAssingment.vue'
import IconSetting from '@/components/icons/IconSetting.vue'
import IconLogout from '@/components/icons/IconLogout.vue'

const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
}
</script>