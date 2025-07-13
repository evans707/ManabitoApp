import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useScrapingStore = defineStore('scraping', () => {
  // --- State ---
  const isScraping = ref(false);
  const statusMessage = ref('');
  const completedMessages = ref([]);
  const totalTasks = 2; // MoodleとWebClassの2つ

  let socket = null;

  // --- Getters ---
  const headerMessage = computed(() => {
    if (!isScraping.value) return '';
    if (completedMessages.value.length < totalTasks) {
      return '課題情報を取得中...';
    }
    return '取得完了';
  });

  // --- Actions ---
  function connectWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      console.log("WebSocket is already connected.");
      return;
    }

    const socketUrl = `ws://${window.location.host}/ws/scraping-status/`;
    socket = new WebSocket(socketUrl);

    socket.onopen = () => {
      console.log("WebSocket connected!");
      isScraping.value = true;
      statusMessage.value = '課題情報の取得を開始しました...';
      completedMessages.value = [];
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Message from server:", data.message);

      // 完了メッセージを配列に追加
      completedMessages.value.push(data.message);

      // 全てのタスクが完了したかチェック
      if (completedMessages.value.length >= totalTasks) {
        statusMessage.value = '全ての課題取得が完了しました。';

        // 3秒後にローディング表示を消す
        setTimeout(() => {
          isScraping.value = false;
          statusMessage.value = '';
        }, 3000);
      } else {
        statusMessage.value = `${completedMessages.value.length}/${totalTasks}件の処理が完了しました。`;
      }
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected.");
      isScraping.value = false;
      socket = null;
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      isScraping.value = false;
      statusMessage.value = "通知サーバーとの接続に失敗しました。";
      socket = null;
    };
  }

  function disconnectWebSocket() {
    if (socket) {
      socket.close();
    }
  }

  return {
    isScraping,
    statusMessage,
    headerMessage,
    completedMessages,
    totalTasks,
    connectWebSocket,
    disconnectWebSocket
  };
});