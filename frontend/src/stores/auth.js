import { defineStore } from 'pinia'
import axios from 'axios'
import router from '@/router' // ルーターインスタンスをインポート

// Axiosのデフォルト設定 (クロスオリジンでクッキーを送信するために必要)
axios.defaults.withCredentials = true;
// DjangoのCSRF保護に対応するため、AxiosにCSRFトークンの扱いを任せる設定
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';


export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: !!localStorage.getItem('isAuthenticated'),
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  actions: {
    async login(credentials) {
      try {
        const response = await axios.post('http://localhost:8000/api/login/', credentials)
        const data = response.data
        if (data.success) {
          this.isAuthenticated = true
          this.user = data.user
          localStorage.setItem('isAuthenticated', 'true')
          localStorage.setItem('user', JSON.stringify(data.user))
          router.push({ name: 'Home' })
          return true
        } else {
          throw new Error(data.message || 'ログインに失敗しました。')
        }
      } catch (error) {
        console.error('Login error in store:', error)
        this.isAuthenticated = false; // 失敗時は認証状態をクリア
        this.user = null;
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('user');
        throw error
      }
    },
    async logout() {
      try {
        await axios.post('http://localhost:8000/api/logout/')
      } catch (error) {
        console.error('Error during API logout call:', error)
        // API呼び出しが失敗しても、フロントエンド側ではログアウト処理を続行
      } finally {
        this.isAuthenticated = false
        this.user = null
        localStorage.removeItem('isAuthenticated')
        localStorage.removeItem('user')
        router.push({ name: 'Login' })
      }
    },
    async checkAuthStatus() {
      if (!this.isAuthenticated && localStorage.getItem('isAuthenticated') !== 'true') {
        // localStorageにも認証情報がない場合は、チェック不要
        return;
      }
      try {
        const response = await axios.get('http://localhost:8000/api/auth/status/')
        if (response.status === 200 && response.data.isAuthenticated) {
          this.isAuthenticated = true
          this.user = response.data.user
          localStorage.setItem('isAuthenticated', 'true')
          localStorage.setItem('user', JSON.stringify(response.data.user))
        } else {
          await this.forceLogout();
        }
      } catch (error) {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          await this.forceLogout();
        } else {
          console.error('Error checking auth status:', error)
        }
      }
    },
    forceLogout() {
        this.isAuthenticated = false;
        this.user = null;
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('user');
        if (router.currentRoute.value.name !== 'Login') {
            router.push({ name: 'Login' });
        }
    }
  },
  getters: {
    isUserAuthenticated: (state) => state.isAuthenticated,
    currentUser: (state) => state.user,
  },
})