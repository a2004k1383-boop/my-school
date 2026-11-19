<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  id: string
  label: string
  modelValue: string
  type?: string
  error?: string
  autocomplete?: string
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const describedBy = computed(() => (props.error ? `${props.id}-error` : undefined))

function onInput(event: Event): void {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="field">
    <label class="field__label" :for="id">{{ label }}</label>
    <input
      :id="id"
      class="field__input"
      :class="{ 'field__input--invalid': error }"
      :type="type ?? 'text'"
      :value="modelValue"
      :autocomplete="autocomplete"
      :placeholder="placeholder"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="describedBy"
      @input="onInput"
    />
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

.field__input {
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

.field__error {
  color: var(--color-danger);
  font-size: 0.8rem;
}
</style>
