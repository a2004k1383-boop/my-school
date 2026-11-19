import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { ApiError } from '@/shared/api/http'
import type { LoginResponse, User } from '@/modules/auth/types'

vi.mock('@/modules/auth/api', () => ({
  loginUser: vi.fn(),
  registerUser: vi.fn(),
  logoutUser: vi.fn(),
  currentUser: vi.fn(),
  refreshAccessToken: vi.fn().mockResolvedValue(false),
}))

import * as api from '@/modules/auth/api'
import LoginView from '../views/LoginView.vue'

const user: User = {
  id: '2f0f8f9e-0000-4000-8000-000000000001',
  full_name: 'سارا محمدی',
  email: 'sara@example.com',
  role: 'parent',
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
      { path: '/grades', name: 'grades', component: { template: '<div />' } },
    ],
  })
}

async function mountLogin(path = '/login') {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = makeRouter()
  await router.push(path)
  await router.isReady()
  const wrapper = mount(LoginView, {
    attachTo: document.body,
    global: { plugins: [pinia, router] },
  })
  return { wrapper, router, pinia }
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(api.refreshAccessToken).mockResolvedValue(false)
})

describe('LoginView', () => {
  it('renders accessible labelled inputs and the register link', async () => {
    const { wrapper } = await mountLogin()

    expect(wrapper.get('label[for="email"]').text()).toContain('ایمیل')
    expect(wrapper.get('label[for="password"]').text()).toContain('رمز عبور')
    expect(wrapper.get('#email').attributes('type')).toBe('email')
    expect(wrapper.find('a[href="/register"]').exists()).toBe(true)
    expect(document.documentElement.getAttribute('dir')).toBe('rtl')
  })

  it('blocks empty submit, shows field errors and focuses the first invalid field', async () => {
    const { wrapper } = await mountLogin()

    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(api.loginUser).not.toHaveBeenCalled()
    expect(wrapper.get('#email').attributes('aria-invalid')).toBe('true')
    expect(wrapper.text()).toContain('ایمیل را وارد کنید.')
    expect(document.activeElement).toBe(wrapper.get('#email').element)
  })

  it('rejects a malformed email without calling the API', async () => {
    const { wrapper } = await mountLogin()

    await wrapper.get('#email').setValue('not-an-email')
    await wrapper.get('#password').setValue('Parent1404')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(api.loginUser).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('ایمیل معتبر نیست.')
  })

  it('shows the Persian credentials error and clears the password on 401', async () => {
    const { wrapper } = await mountLogin()
    vi.mocked(api.loginUser).mockRejectedValue(
      new ApiError(401, { code: 'invalid_credentials', detail: 'invalid' }),
    )

    await wrapper.get('#email').setValue('sara@example.com')
    await wrapper.get('#password').setValue('Wrong1404')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.get('[role="alert"]').text()).toContain('ایمیل یا رمز عبور نادرست است.')
    expect((wrapper.get('#email').element as HTMLInputElement).value).toBe('sara@example.com')
    expect((wrapper.get('#password').element as HTMLInputElement).value).toBe('')
  })

  it('redirects to the requested page after a successful login', async () => {
    const { wrapper, router } = await mountLogin('/login?redirect=/grades')
    const response: LoginResponse = {
      access_token: 'access-token',
      token_type: 'bearer',
      expires_in: 900,
      user,
    }
    vi.mocked(api.loginUser).mockResolvedValue(response)

    await wrapper.get('#email').setValue('sara@example.com')
    await wrapper.get('#password').setValue('Parent1404')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(api.loginUser).toHaveBeenCalledWith({
      email: 'sara@example.com',
      password: 'Parent1404',
      remember_me: false,
    })
    expect(router.currentRoute.value.fullPath).toBe('/grades')
  })

  it('shows the success message after registration', async () => {
    const { wrapper } = await mountLogin('/login?registered=1')

    expect(wrapper.get('[role="status"]').text()).toContain('حساب شما ساخته شد')
  })
})
