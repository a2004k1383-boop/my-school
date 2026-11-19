<script setup lang="ts">
import { fa } from '@/shared/i18n/fa'

defineProps<{
  title: string
  subtitle: string
}>()
</script>

<template>
  <main id="main" class="auth">
    <section class="auth__brand" aria-hidden="true">
      <p class="auth__mark">{{ fa.app.name }}</p>
      <p class="auth__tagline">{{ fa.app.tagline }}</p>
      <ul class="auth__points">
        <li>تکالیف و تاریخ تحویل</li>
        <li>اطلاعیه‌های مدرسه</li>
        <li>نمرات و روند پیشرفت</li>
      </ul>
    </section>

    <section class="auth__panel">
      <div class="auth__card">
        <header class="auth__header">
          <h1 class="auth__title">{{ title }}</h1>
          <p class="auth__subtitle">{{ subtitle }}</p>
        </header>
        <slot />
      </div>
      <p class="auth__footer">{{ fa.app.name }} · نسخه ۰.۱</p>
    </section>
  </main>
</template>

<style scoped>
.auth {
  display: grid;
  min-height: 100vh;
  grid-template-columns: 1fr;
}

.auth__brand {
  display: none;
  padding: 3rem;
  background: linear-gradient(160deg, #0d544d 0%, #146c63 55%, #1c8a7e 100%);
  color: #eaf7f4;
}

.auth__mark {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.auth__tagline {
  margin-block-start: 1rem;
  max-width: 30ch;
  font-size: 1.05rem;
  opacity: 0.92;
}

.auth__points {
  margin-block-start: 2.5rem;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.75rem;
  font-size: 0.95rem;
}

.auth__points li::before {
  content: '✓';
  margin-inline-end: 0.5rem;
  color: #9fe3d8;
}

.auth__panel {
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 1.5rem;
  padding: 2rem 1rem;
}

.auth__card {
  width: min(100%, 26rem);
  padding: 2rem;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.auth__title {
  font-size: 1.5rem;
  font-weight: 800;
}

.auth__subtitle {
  margin-block-start: 0.5rem;
  color: var(--color-muted);
  font-size: 0.95rem;
}

.auth__footer {
  color: var(--color-muted);
  font-size: 0.8rem;
}

@media (min-width: 900px) {
  .auth {
    grid-template-columns: 1.05fr 1fr;
  }

  .auth__brand {
    display: block;
  }
}
</style>
