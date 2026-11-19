import type { RouteLocationNormalized, RouteLocationRaw } from 'vue-router'

import { useAuthStore } from '@/modules/auth/store'

/**
 * Route guard: anonymous users are sent to /login (with a redirect back),
 * authenticated users are kept out of the auth pages.
 */
export async function authGuard(to: RouteLocationNormalized): Promise<true | RouteLocationRaw> {
  const auth = useAuthStore()
  if (auth.status === 'idle') {
    await auth.bootstrap()
  }
  const isPublic = to.meta.public === true
  if (!isPublic && auth.status !== 'authenticated') {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (isPublic && to.name !== 'not-found' && auth.status === 'authenticated') {
    return { name: 'dashboard' }
  }
  return true
}
