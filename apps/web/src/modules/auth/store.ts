import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getAccessToken, setAccessToken } from '@/shared/api/http'
import {
  currentUser,
  loginUser,
  logoutUser,
  refreshAccessToken,
  registerUser,
} from './api'
import type { RegisterPayload, User } from './types'

export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'anonymous'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const status = ref<AuthStatus>('idle')

  function clearSession(): void {
    setAccessToken(null)
    accessToken.value = null
    user.value = null
    status.value = 'anonymous'
  }

  async function login(email: string, password: string, rememberMe = false): Promise<User> {
    const result = await loginUser({ email, password, remember_me: rememberMe })
    setAccessToken(result.access_token)
    accessToken.value = result.access_token
    user.value = result.user
    status.value = 'authenticated'
    return result.user
  }

  async function register(payload: RegisterPayload): Promise<User> {
    return registerUser(payload)
  }

  async function bootstrap(): Promise<void> {
    status.value = 'loading'
    try {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        user.value = await currentUser()
        accessToken.value = getAccessToken()
        status.value = 'authenticated'
        return
      }
    } catch {
      // A failed silent refresh simply means "not logged in".
    }
    clearSession()
  }

  async function logout(): Promise<void> {
    try {
      await logoutUser()
    } catch {
      // Logging out locally must succeed even if the server call fails.
    } finally {
      clearSession()
    }
  }

  return { user, accessToken, status, login, register, bootstrap, logout, clearSession }
})
