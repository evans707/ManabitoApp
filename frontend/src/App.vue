<template>
  <div class="app">
    <!-- ヘッダー -->
    <header class="header">
      <div class="logo-section">
        <div class="icon">icon</div>
        <div class="title">manabito</div>
      </div>
      <div class="user-section">
        <div class="id">00RD000</div>
        <div class="name">電大 太郎</div>
      </div>
    </header>

    <!-- メイン -->
    <main class="main-content">
      <!-- 課題テーブル -->
      <section class="section-table">
        <div class="tab">📋 課題テーブル</div>
        <div class="table-box">
          <p>（ここに課題を表示）</p>
        </div>
      </section>

      <!-- カレンダー -->
      <section class="section-calendar">
        <div class="tab">🗓 カレンダー</div>
        <div class="calendar-grid">
          <div
            v-for="i in 35"
            :key="i"
            class="calendar-cell"
          >
            <div class="date-number">{{ i }}</div>
            <div v-if="i === 5 || i === 18" class="badge">予定</div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', sans-serif;
  background-color: #f4f6f8;
  padding: 24px;
  color: #333;
}

/* ヘッダー */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.logo-section {
  display: flex;
  align-items: center;
}

.icon {
  background-color: #007bff;
  color: white;
  font-weight: bold;
  padding: 10px 14px;
  border-radius: 8px;
  margin-right: 12px;
  font-size: 16px;
}

.title {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.user-section {
  text-align: right;
  font-size: 14px;
  color: #555;
  line-height: 1.4;
}

/* メインレイアウト */
.main-content {
  flex: 1;
  display: flex;
  gap: 24px;
  overflow: hidden;
}

/* 課題テーブル */
.section-table, .section-calendar {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* prevent overflow */
}

.tab {
  background-color: white;
  padding: 10px 20px;
  border-radius: 12px 12px 0 0;
  font-weight: 600;
  font-size: 16px;
  margin-bottom: -1px;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
  display: inline-block;
}

.table-box {
  flex: 1;
  background: white;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 24px;
  overflow-y: auto;
  font-size: 14px;
}

/* カレンダー */
.calendar-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(5, 1fr);
  background: white;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.calendar-cell {
  border: 1px solid #eee;
  aspect-ratio: 1 / 1;
  padding: 6px;
  position: relative;
  transition: background 0.2s;
}

.calendar-cell:hover {
  background: #f0f8ff;
  cursor: pointer;
}

.date-number {
  font-weight: 600;
  font-size: 13px;
  color: #333;
}

.badge {
  background-color: #ff6961;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 12px;
  position: absolute;
  bottom: 6px;
  right: 6px;
}
</style>
