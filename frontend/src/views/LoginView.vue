<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg">
      <h2 class="text-3xl font-bold text-center text-gray-900">ログイン</h2>
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="university_id" class="block text-sm font-medium text-gray-700">学籍番号</label>
          <input
            id="university_id"
            v-model="university_id"
            name="university_id"
            type="text"  ometries 
            autocomplete="username"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
            placeholder="学籍番号を入力"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">パスワード</label>
          <input
            id="password"
            v-model="password"
            name="password"
            type="password"
            autocomplete="current-password"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
            placeholder="********"
          />
        </div>

        <div v-if="error_message" class="text-sm text-red-600">
          {{ error_message }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            <span v-if="isLoading">処理中...</span>
            <span v-else>ログイン</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
// import { useRouter } from 'vue-router' // ストア内でリダイレクトするため不要
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore();

const university_id = ref('');
const password = ref('');
const error_message = ref('');
const isLoading = ref(false);

async function handleLogin() {
  isLoading.value = true;
  error_message.value = '';

  try {
    await authStore.login({
      university_id: university_id.value,
      password: password.value
    });
    // ログイン成功時のリダイレクトはストアのloginアクション内で行われる
  } catch (error) {
    error_message.value = error.response?.data?.message || error.message || 'ログイン処理中にエラーが発生しました。';
    console.error('ログインエラー (View):', error);
  } finally {
    isLoading.value = false;
  }
}
</script>