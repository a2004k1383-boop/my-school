<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { ApiError } from '@/shared/api/http'
import { toMessage } from '@/shared/i18n/errors'
import { fa } from '@/shared/i18n/fa'

import Alert from '../components/Alert.vue'
import AuthLayout from '../components/AuthLayout.vue'
import FormField from '../components/FormField.vue'
import PasswordField from '../components/PasswordField.vue'
import SubmitButton from '../components/SubmitButton.vue'
import { useAuthStore } from '../store'
import type { RegisterPayload, Role } from '../types'
import { issuesToFields, registerSchema } from '../validation'

const auth = useAuthStore()
const router = useRouter()

const roles: Role[] = ['parent', 'student', 'teacher']
const values = reactive({
  full_name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'parent' as Role,
  invite_code: '',
  accepted_terms: false,
})
const errors = ref<Record<string, string>>({})
const formError = ref('')
const loading = ref(false)

const showInvite = computed(() => values.role === 'teacher')

async function focusFirstInvalid(): Promise<void> {
  await nextTick()
  const element = document.querySelector<HTMLElement>('[aria-invalid="true"]')
  element?.focus()
}

function buildPayload(): RegisterPayload {
  const payload: RegisterPayload = {
    full_name: values.full_name,
    email: values.email,
    password: values.password,
    password_confirm: values.password_confirm,
    role: values.role,
    accepted_terms: values.accepted_terms,
  }
  if (values.role === 'teacher') {
    payload.invite_code = values.invite_code
  }
  return payload
}

async function onSubmit(): Promise<void> {
  errors.value = {}
  formError.value = ''
  const payload = buildPayload()

  const parsed = registerSchema.safeParse(payload)
  if (!parsed.success) {
    errors.value = issuesToFields(parsed.error)
    await focusFirstInvalid()
    return
  }

  loading.value = true
  try {
    await auth.register(parsed.data as RegisterPayload)
    await router.push({ name: 'login', query: { registered: '1' } })
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length > 0) {
      errors.value = error.fields
      await focusFirstInvalid()
    } else if (error instanceof ApiError && error.code === 'invitation_required') {
      errors.value = { invite_code: fa.errors.invitationRequired }
      await focusFirstInvalid()
    } else {
      formError.value = toMessage(error)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout :title="fa.auth.register.title" :subtitle="fa.auth.register.subtitle">
    <form class="form" novalidate @submit.prevent="onSubmit">
      <Alert v-if="formError" :message="formError" />

      <FormField
        id="full_name"
        v-model="values.full_name"
        :label="fa.auth.fields.fullName"
        autocomplete="name"
        :error="errors.full_name"
      />
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
        autocomplete="new-password"
        :error="errors.password"
      />
      <PasswordField
        id="password_confirm"
        v-model="values.password_confirm"
        :label="fa.auth.fields.passwordConfirm"
        autocomplete="new-password"
        :error="errors.password_confirm"
      />

      <fieldset class="roles" :aria-describedby="errors.role ? 'role-error' : undefined">
        <legend class="roles__legend">{{ fa.auth.fields.role }}</legend>
        <label v-for="role in roles" :key="role" class="roles__option">
          <input
            v-model="values.role"
            type="radio"
            name="role"
            :value="role"
            :aria-invalid="errors.role ? 'true' : undefined"
          />
          <span>{{ fa.roles[role] }}</span>
        </label>
      </fieldset>
      <p v-if="errors.role" id="role-error" class="error">{{ errors.role }}</p>

      <FormField
        v-if="showInvite"
        id="invite_code"
        v-model="values.invite_code"
        :label="fa.auth.fields.inviteCode"
        autocomplete="off"
        :error="errors.invite_code"
      />
      <p v-if="showInvite && !errors.invite_code" class="hint">{{ fa.auth.fields.inviteHint }}</p>

      <label class="checkbox">
        <input
          v-model="values.accepted_terms"
          type="checkbox"
          name="terms"
          :aria-invalid="errors.accepted_terms ? 'true' : undefined"
        />
        <span>{{ fa.auth.fields.acceptTerms }}</span>
      </label>
      <p v-if="errors.accepted_terms" class="error">{{ errors.accepted_terms }}</p>

      <SubmitButton :label="fa.auth.register.submit" :loading="loading" />

      <p class="switch">
        {{ fa.auth.register.hasAccount }}
        <RouterLink to="/login">{{ fa.auth.register.signIn }}</RouterLink>
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

.roles {
  margin: 0;
  padding: 0;
  border: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.roles__legend {
  padding: 0;
  margin-block-end: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.roles__option {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: #fff;
  font-size: 0.9rem;
  cursor: pointer;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.hint {
  color: var(--color-muted);
  font-size: 0.8rem;
}

.error {
  color: var(--color-danger);
  font-size: 0.8rem;
}

.switch {
  text-align: center;
  font-size: 0.9rem;
  color: var(--color-muted);
}
</style>
