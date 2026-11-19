<script setup lang="ts">
withDefaults(
  defineProps<{
    message: string
    tone?: 'error' | 'success'
  }>(),
  { tone: 'error' },
)
</script>

<template>
  <p
    class="alert"
    :class="`alert--${tone}`"
    :role="tone === 'error' ? 'alert' : 'status'"
    aria-live="polite"
  >
    {{ message }}
  </p>
</template>

<style scoped>
.alert {
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
}

.alert--error {
  color: var(--color-danger);
  background: var(--color-danger-soft);
}

.alert--success {
  color: var(--color-success);
  background: var(--color-success-soft);
}
</style>
