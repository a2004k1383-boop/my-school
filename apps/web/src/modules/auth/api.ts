import { apiFetch, refreshSession } from '@/shared/api/http'
import type { LoginPayload, LoginResponse, RegisterPayload, User } from './types'

export function registerUser(payload: RegisterPayload): Promise<User> {
  return apiFetch<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function loginUser(payload: LoginPayload): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function logoutUser(): Promise<void> {
  await apiFetch<void>('/auth/logout', {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
  })
}

export function currentUser(): Promise<User> {
  return apiFetch<User>('/auth/me')
}

export function refreshAccessToken(): Promise<boolean> {
  return refreshSession()
}
