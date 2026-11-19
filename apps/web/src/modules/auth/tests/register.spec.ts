import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { ApiError } from '@/shared/api/http'
import type { User } from '@/modules/auth/types'

vi.mock('@/modules/auth/api', () => ({
  loginUser: vi.fn(),
  registerUser: vi.fn(),
  logoutUser: vi.fn(),
  currentUser: vi.fn(),
  refreshAccessToken: vi.fn().mockResolvedValue(false),
}))

import * as api from '@/modules/auth/api'
import RegisterView from '../views/RegisterView.vue'

const user: User = {
  id: '2f0f8f9e-0000-4000-8000-000000000002',
  full_name: 'رضا کریمی',
  email: 'teacher@example.com',
  role: 'teacher',
  is_active: true,
  created_at: '2026-11-19T10:00:00Z',
}

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/login', name: 'login', component: { template: '<div />' } },
      { path: '/register', name: 'register', component: { template: '<div />' } },
      { path: '/dashboard', name: 'dashboard', component: { template: '<div />' } },
    ],
  })
}

async function mountRegister() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = makeRouter()
  await router.push('/register')
  await router.isReady()
  const wrapper = mount(RegisterView, { global: { plugins: [pinia, router] } })
  return { wrapper, router }
}

async function fillValidForm(wrapper: Awaited<ReturnType<typeof mountRegister>>['wrapper']) {
  await wrapper.get('#full_name').setValue('سارا محمدی')
  await wrapper.get('#email').setValue('sara@example.com')
  await wrapper.get('#password').setValue('Parent1404')
  await wrapper.get('#password_confirm').setValue('Parent1404')
  await wrapper.get('input[name="terms"]').setValue(true)
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(api.refreshAccessToken).mockResolvedValue(false)
})

describe('RegisterView', () => {
  it('offers the three roles and no invite field by default', async () => {
    const { wrapper } = await mountRegister()

    const roles = wrapper.findAll('input[name="role"]')
    expect(roles).toHaveLength(3)
    expect(wrapper.find('#invite_code').exists()).toBe(false)
  })

  it('asks for the invite code when the teacher role is selected', async () => {
    const { wrapper } = await mountRegister()

    await wrapper.get('input[value="teacher"]').setValue(true)

    expect(wrapper.find('#invite_code').exists()).toBe(true)
  })

  it('shows a mismatch error without calling the API', async () => {
    const { wrapper } = await mountRegister()

    await fillValidForm(wrapper)
    await wrapper.get('#password_confirm').setValue('Different1404')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(api.registerUser).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('تکرار رمز عبور مطابقت ندارد.')
  })

  it('requires the invite code for a teacher', async () => {
    const { wrapper } = await mountRegister()

    await fillValidForm(wrapper)
    await wrapper.get('input[value="teacher"]').setValue(true)
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(api.registerUser).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('کد دعوت معلم را وارد کنید.')
  })

  it('requires accepting the terms', async () => {
    const { wrapper } = await mountRegister()

    await wrapper.get('#full_name').setValue('سارا محمدی')
    await wrapper.get('#email').setValue('sara@example.com')
    await wrapper.get('#password').setValue('Parent1404')
    await wrapper.get('#password_confirm').setValue('Parent1404')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(api.registerUser).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('برای ادامه باید قوانین را بپذیرید.')
  })

  it('redirects to login with a success flag after registration', async () => {
    const { wrapper, router } = await mountRegister()
    vi.mocked(api.registerUser).mockResolvedValue(user)

    await fillValidForm(wrapper)
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.registered).toBe('1')
  })

  it('maps a duplicate email response to a field error', async () => {
    const { wrapper } = await mountRegister()
    vi.mocked(api.registerUser).mockRejectedValue(
      new ApiError(409, { code: 'email_already_registered', detail: 'taken' }),
    )

    await fillValidForm(wrapper)
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('این ایمیل قبلاً ثبت شده است.')
  })

  it('maps an invalid invite code to the invite field', async () => {
    const { wrapper } = await mountRegister()
    vi.mocked(api.registerUser).mockRejectedValue(
      new ApiError(403, { code: 'invitation_required', detail: 'invite' }),
    )

    await fillValidForm(wrapper)
    await wrapper.get('input[value="teacher"]').setValue(true)
    await wrapper.get('#invite_code').setValue('WRONG')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('کد دعوت معلم معتبر نیست.')
  })
})
