import { createPinia, setActivePinia } from 'pinia'
import type { RouteLocationNormalized } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/modules/auth/api', () => ({
  loginUser: vi.fn(),
  registerUser: vi.fn(),
  logoutUser: vi.fn(),
  currentUser: vi.fn(),
  refreshAccessToken: vi.fn().mockResolvedValue(false),
}))

import { authGuard } from '@/router/guard'
import { useAuthStore } from '@/modules/auth/store'

function route(name: string, fullPath: string, isPublic = false): RouteLocationNormalized {
  return {
    name,
    fullPath,
    meta: isPublic ? { public: true } : {},
  } as unknown as RouteLocationNormalized
}

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('authGuard', () => {
  it('redirects anonymous visitors to /login with a redirect query', async () => {
    const auth = useAuthStore()
    auth.status = 'anonymous'

    const result = await authGuard(route('dashboard', '/dashboard'))

    expect(result).toEqual({ name: 'login', query: { redirect: '/dashboard' } })
  })

  it('allows anonymous visitors to open the login page', async () => {
    const auth = useAuthStore()
    auth.status = 'anonymous'

    const result = await authGuard(route('login', '/login', true))

    expect(result).toBe(true)
  })

  it('keeps authenticated users out of auth pages', async () => {
    const auth = useAuthStore()
    auth.status = 'authenticated'

    const result = await authGuard(route('login', '/login', true))

    expect(result).toEqual({ name: 'dashboard' })
  })

  it('lets authenticated users reach the dashboard', async () => {
    const auth = useAuthStore()
    auth.status = 'authenticated'

    const result = await authGuard(route('dashboard', '/dashboard'))

    expect(result).toBe(true)
  })
})
