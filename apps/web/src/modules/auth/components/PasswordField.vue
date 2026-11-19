<script setup lang="ts">
import { computed, ref } from 'vue'

import { fa } from '@/shared/i18n/fa'

const props = defineProps<{
  id: string
  label: string
  modelValue: string
  error?: string
  autocomplete?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const visible = ref(false)
const inputType = computed(() => (visible.value ? 'text' : 'password'))
const describedBy = computed(() => (props.error ? `${props.id}-error` : undefined))
const toggleLabel = computed(() =>
  visible.value ? fa.auth.actions.hidePassword : fa.auth.actions.showPassword,
)

function onInput(event: Event): void {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="field">
    <label class="field__label" :for="id">{{ label }}</label>
    <div class="field__row">
      <input
        :id="id"
        class="field__input"
        :class="{ 'field__input--invalid': error }"
        :type="inputType"
        :value="modelValue"
        :autocomplete="autocomplete"
        :aria-invalid="error ? 'true' : undefined"
        :aria-describedby="describedBy"
        @input="onInput"
      />
      <button
        type="button"
        class="field__toggle"
        :aria-label="toggleLabel"
        :aria-pressed="visible"
        @click="visible = !visible"
      >
        {{ visible ? '🙈' : '👁' }}
      </button>
    </div>
    <p v-if="error" :id="`${id}-error`" class="field__error">{{ error }}</p>
  </div>
</template>

<style scoped>
.field {
  display: grid;
  gap: 0.35rem;
}

.field__label {
  font-size: 0.9rem;
  font-weight: 600;
}

.field__row {
  display: flex;
  gap: 0.5rem;
}

.field__input {
  flex: 1;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font: inherit;
  background: #fff;
}

.field__input--invalid {
  border-color: var(--color-danger);
  background: var(--color-danger-soft);
}

.field__toggle {
  padding-inline: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: #fff;
  cursor: pointer;
}

.field__error {
  color: var(--color-danger);
  font-size: 0.8rem;
}
</style>
