<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main id="main" class="not-found">
    <h1>۴۰۴</h1>
    <p>صفحه‌ای که دنبال آن بودید پیدا نشد.</p>
    <RouterLink to="/dashboard">بازگشت به میزکار</RouterLink>
  </main>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: grid;
  place-content: center;
  gap: 0.75rem;
  text-align: center;
}

.not-found h1 {
  font-size: 3rem;
  color: var(--color-primary);
}
</style>
