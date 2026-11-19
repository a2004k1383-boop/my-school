<script setup lang="ts">
import { nextTick, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/shared/api/http'
import { toMessage } from '@/shared/i18n/errors'
import { fa } from '@/shared/i18n/fa'

import Alert from '../components/Alert.vue'
import AuthLayout from '../components/AuthLayout.vue'
import FormField from '../components/FormField.vue'
import PasswordField from '../components/PasswordField.vue'
import SubmitButton from '../components/SubmitButton.vue'
import { useAuthStore } from '../store'
import { issuesToFields, loginSchema } from '../validation'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const values = reactive({ email: '', password: '', remember: false })
const errors = ref<Record<string, string>>({})
const formError = ref('')
const loading = ref(false)
const successMessage = ref(route.query.registered === '1' ? fa.auth.success.registered : '')

async function focusFirstInvalid(): Promise<void> {
  await nextTick()
  const element = document.querySelector<HTMLElement>('[aria-invalid="true"]')
  element?.focus()
}

async function onSubmit(): Promise<void> {
  errors.value = {}
  formError.value = ''
  successMessage.value = ''

  const parsed = loginSchema.safeParse({ email: values.email, password: values.password })
  if (!parsed.success) {
    errors.value = issuesToFields(parsed.error)
    await focusFirstInvalid()
    return
  }

  loading.value = true
  try {
    await auth.login(parsed.data.email, parsed.data.password, values.remember)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    await router.push(redirect)
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length > 0) {
      errors.value = error.fields
      await focusFirstInvalid()
    } else {
      formError.value = toMessage(error)
    }
    values.password = ''
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout :title="fa.auth.login.title" :subtitle="fa.auth.login.subtitle">
    <form class="form" novalidate @submit.prevent="onSubmit">
      <Alert v-if="successMessage" :message="successMessage" tone="success" />
      <Alert v-if="formError" :message="formError" />

      <FormField
        id="email"
        v-model="values.email"
        :label="fa.auth.fields.email"
        type="email"
        autocomplete="email"
        placeholder="name@example.com"
        :error="errors.email"
      />
      <PasswordField
        id="password"
        v-model="values.password"
        :label="fa.auth.fields.password"
        autocomplete="current-password"
        :error="errors.password"
      />

      <label class="checkbox">
        <input v-model="values.remember" type="checkbox" name="remember" />
        <span>{{ fa.auth.fields.rememberMe }}</span>
      </label>

      <SubmitButton :label="fa.auth.login.submit" :loading="loading" />

      <p class="switch">
        {{ fa.auth.login.noAccount }}
        <RouterLink to="/register">{{ fa.auth.login.createAccount }}</RouterLink>
      </p>
    </form>
  </AuthLayout>
</template>

<style scoped>
.form {
  display: grid;
  gap: 1rem;
  margin-block-start: 1.5rem;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.switch {
  text-align: center;
  font-size: 0.9rem;
  color: var(--color-muted);
}
</style>
