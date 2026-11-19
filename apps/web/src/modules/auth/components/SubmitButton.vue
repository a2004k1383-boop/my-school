<script setup lang="ts">
import { fa } from '@/shared/i18n/fa'

defineProps<{
  label: string
  loading?: boolean
}>()
</script>

<template>
  <button class="btn" type="submit" :disabled="loading" :aria-busy="loading ? 'true' : undefined">
    <span v-if="loading" class="spinner" aria-hidden="true" />
    {{ loading ? fa.common.loading : label }}
  </button>
</template>
