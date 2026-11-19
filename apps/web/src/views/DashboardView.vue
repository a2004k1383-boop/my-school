<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/modules/auth/store'
import { fa } from '@/shared/i18n/fa'

const auth = useAuthStore()
const router = useRouter()

const user = computed(() => auth.user)
const roleLabel = computed(() => (user.value ? fa.roles[user.value.role] : ''))
const modules = computed(() => Object.values(fa.dashboard.modules))

async function onLogout(): Promise<void> {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <main id="main" class="dashboard">
    <header class="dashboard__bar">
      <p class="dashboard__brand">{{ fa.app.name }}</p>
      <button class="btn btn--ghost" type="button" @click="onLogout">
        {{ fa.dashboard.logout }}
      </button>
    </header>

    <section v-if="user" class="dashboard__welcome">
      <h1>{{ fa.dashboard.welcome }}، {{ user.full_name }}</h1>
      <p class="dashboard__meta">
        {{ fa.dashboard.roleLabel }}: <strong>{{ roleLabel }}</strong>
      </p>
    </section>

    <section class="dashboard__grid" aria-label="ماژول‌ها">
      <article v-for="moduleName in modules" :key="moduleName" class="card">
        <h2 class="card__title">{{ moduleName }}</h2>
        <p class="card__badge">{{ fa.dashboard.comingSoon }}</p>
      </article>
    </section>
    <p class="dashboard__hint">{{ fa.dashboard.modulesHint }}</p>
  </main>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 1.5rem clamp(1rem, 4vw, 3rem);
  display: grid;
  align-content: start;
  gap: 2rem;
}

.dashboard__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dashboard__brand {
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--color-primary);
}

.dashboard__welcome h1 {
  font-size: clamp(1.4rem, 3vw, 2rem);
}

.dashboard__meta {
  margin-block-start: 0.5rem;
  color: var(--color-muted);
}

.dashboard__grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
}

.card {
  padding: 1.25rem;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.card__title {
  font-size: 1rem;
  font-weight: 700;
}

.card__badge {
  margin-block-start: 0.75rem;
  display: inline-block;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  background: var(--color-primary-soft);
  color: var(--color-primary-strong);
  font-size: 0.75rem;
}

.dashboard__hint {
  color: var(--color-muted);
  font-size: 0.85rem;
}
</style>
