<template>
  <div class="profile-page">
    <h2 class="text-2xl font-semibold mb-4 text-gray-700">プロフィール</h2>

    <Card>
      <div class="p-2">
        <div class="flex flex-col sm:flex-row items-center gap-6">
          <div class="flex-shrink-0">
            <div class="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
              <svg class="w-16 h-16 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
          </div>

          <div class="flex-grow text-center sm:text-left">
            <h3 class="text-xl font-bold text-gray-900">{{ authStore.user?.username || 'ユーザー名' }}</h3>
            <p class="text-md text-gray-500 mt-1">{{ authStore.user?.email || 'email@example.com' }}</p>

            <dl class="mt-4 text-sm text-gray-700">
              <div class="flex justify-center sm:justify-start">
                <dt class="font-medium w-24">学籍番号</dt>
                <dd class="font-mono">{{ authStore.user?.university_id || 'N/A' }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <div class="mt-6 pt-6 border-t border-gray-200 flex flex-col sm:flex-row justify-end items-center gap-3">
          <button @click="handleLogout" class="w-full sm:w-auto bg-red-600 text-white font-medium py-2 px-4 rounded-lg hover:bg-red-700 transition-colors">
            ログアウト
          </button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Card from '@/components/common/Card.vue'

const router = useRouter()
const authStore = useAuthStore()

// ログアウト処理
async function handleLogout() {
  await authStore.logout()
  // authStoreのlogoutアクション内でリダイレクト処理が行われることを想定
  // もしリダイレクトされない場合は、ここで明示的に行う
  // router.push({ name: 'Login' })
}
</script>