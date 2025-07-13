<template>
  <div class="relative">
    <button @click="isOpen = !isOpen" class="p-2 rounded-full hover:bg-gray-100 transition-colors">
      <svg class="h-6 w-6 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
      </svg>
    </button>

    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div v-if="isOpen" @click="isOpen = false" class="absolute left-0 mt-2 w-56 origin-top-left bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
        <div class="py-1" role="menu" aria-orientation="vertical">
          <RouterLink to="/profile" class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
            <IconAccount class="h-5 w-5 text-gray-500"/>
            <span>プロフィール</span>
          </RouterLink>
          <RouterLink to="/settings" class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
            <IconSetting class="h-5 w-5 text-gray-500"/>
            <span>設定</span>
          </RouterLink>
          <a href="#" @click.prevent="handleLogout" class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full" role="menuitem">
            <IconLogout class="h-5 w-5 text-gray-500"/>
            <span>ログアウト</span>
          </a>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import IconAccount from '@/components/icons/IconAccount.vue'
import IconSetting from '@/components/icons/IconSetting.vue'
import IconLogout from '@/components/icons/IconLogout.vue'

const isOpen = ref(false)
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
}
</script>