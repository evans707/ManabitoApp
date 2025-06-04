// src/views/Home.vue
<template>
  <div class="home-page">
    <h2>ホーム</h2> {/* */}
    <p>ここにホームページの主要なコンテンツ（例：直近の課題概要、通知など）が表示されます。</p>
    
    <section class="quick-look-assignments">
      <h3>直近の課題 (サンプル)</h3> {/* */}
      <ul>
        <li>情報工学実験A - 提出期限: 2025年6月10日</li> {/* */}
        <li>卒業論文テーマ提出 - 提出期限: 2025年6月15日</li> {/* */}
      </ul>
    </section>

    <section class="calendar-summary">
      <h3>カレンダー概要 (プレースホルダー)</h3> {/* */}
      <p>ここにカレンダーの簡易表示や、今日の予定などが表示されます。</p>
    </section>
  </div>
</template>

<style scoped>
.home-page h2 {
  margin-bottom: 1rem;
}
.quick-look-assignments, .calendar-summary {
  margin-top: 1.5rem;
  padding: 1rem;
  /* border: 1px solid #ddd; */ /* 構造把握のための仮枠線 */
  /* border-radius: 8px; */
}
.quick-look-assignments ul {
  list-style: none;
  padding-left: 0;
}
.quick-look-assignments li {
  margin-bottom: 0.5rem;
}
</style>