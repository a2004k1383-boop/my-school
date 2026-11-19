import type { ProblemDetail } from '@/modules/auth/types'

/**
 * Error thrown for any non-2xx API response. Carries the stable backend code so
 * the UI can map it to a Persian message instead of showing raw text.
 */
export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly fields: Record<string, string>

  constructor(status: number, problem: ProblemDetail) {
    super(problem.detail ?? 'Request failed')
    this.name = 'ApiError'
    this.status = status
    this.code = problem.code ?? 'unknown_error'
    this.fields = {}
    for (const issue of problem.errors ?? []) {
      this.fields[issue.field] = issue.message
    }
  }
}

let accessToken: string | null = null
let refreshInFlight: Promise<boolean> | null = null

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export function getAccessToken(): string | null {
  return accessToken
}

async function performRefresh(): Promise<boolean> {
  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  if (!response.ok) {
    return false
  }
  const data = (await response.json()) as { access_token: string }
  setAccessToken(data.access_token)
  return true
}

/**
 * Refresh the session at most once at a time: parallel 401s share one request
 * (single-flight), which avoids rotating the refresh token twice.
 */
export function refreshSession(): Promise<boolean> {
  if (refreshInFlight === null) {
    refreshInFlight = performRefresh().finally(() => {
      refreshInFlight = null
    })
  }
  return refreshInFlight
}

async function readProblem(response: Response): Promise<ProblemDetail> {
  try {
    return (await response.json()) as ProblemDetail
  } catch {
    return { code: 'unknown_error', detail: response.statusText }
  }
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  allowRetry = true,
): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }
  const token = getAccessToken()
  if (token !== null) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let response: Response
  try {
    response = await fetch(`/api/v1${path}`, { ...init, headers, credentials: 'include' })
  } catch {
    throw new ApiError(0, {
      code: 'network_error',
      detail: 'ارتباط با سرور برقرار نشد.',
    })
  }

  if (response.status === 401 && allowRetry && !path.startsWith('/auth/refresh')) {
    if (await refreshSession()) {
      return apiFetch<T>(path, init, false)
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, await readProblem(response))
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}
