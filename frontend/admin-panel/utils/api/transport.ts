import type { TokenResponse } from '../../types/auth'

export interface TokenStore {
  get(): TokenResponse | null
  set(tokens: TokenResponse): void
  clear(): void
}
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export function apiBase(baseUrl: string): string {
  const base = baseUrl.trim().replace(/\/+$/, '')
  if (/\/api\/v1$/.test(base)) return base
  if (/\/api$/.test(base)) return base + '/v1'
  return base + '/api/v1'
}

async function read(response: Response): Promise<unknown> {
  if (response.status === 204) return undefined
  if (response.headers.get('content-type')?.includes('application/json')) {
    return response.json().catch(() => undefined)
  }
  return response.text()
}
function error(response: Response, data: unknown): ApiError {
  const detail = data && typeof data === 'object' && 'detail' in data ? data.detail : undefined
  let message = typeof detail === 'string' ? detail : 'Ошибка запроса: HTTP ' + response.status
  if (Array.isArray(detail)) {
    message = detail
      .map((item) => {
        const field = Array.isArray(item.loc)
          ? item.loc.filter((x: unknown) => x !== 'body').join('.')
          : ''
        return [field, typeof item.msg === 'string' ? item.msg : 'Некорректное значение']
          .filter(Boolean)
          .join(': ')
      })
      .join('; ')
  }
  return new ApiError(response.status, message, data)
}
export function validTokens(value: unknown): value is TokenResponse {
  if (!value || typeof value !== 'object') return false
  const tokens = value as TokenResponse
  return (
    typeof tokens.access_token === 'string' &&
    !!tokens.access_token &&
    typeof tokens.refresh_token === 'string' &&
    !!tokens.refresh_token &&
    typeof tokens.expires_in === 'number' &&
    typeof tokens.refresh_expires_in === 'number'
  )
}

export function createHttpClient(config: {
  baseUrl: string
  tokens: TokenStore
  fetcher?: typeof fetch
  refreshOn401?: boolean
  onUnauthorized?: () => void
}) {
  const fetcher = config.fetcher ?? globalThis.fetch
  const base = apiBase(config.baseUrl)
  let refreshing: Promise<boolean> | null = null
  function invalidate() {
    config.tokens.clear()
    config.onUnauthorized?.()
  }
  async function refresh(): Promise<boolean> {
    if (refreshing) return refreshing
    const current = config.tokens.get()
    if (!current?.refresh_token) {
      invalidate()
      return false
    }
    refreshing = (async () => {
      const response = await fetcher(base + '/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: current.refresh_token }),
      })
      const data = await read(response)
      if (!response.ok) {
        if (response.status === 401) {
          invalidate()
          return false
        }
        throw error(response, data)
      }
      if (!validTokens(data)) throw new ApiError(502, 'Некорректный ответ обновления сессии')
      if (config.tokens.get()?.refresh_token !== current.refresh_token) return false
      config.tokens.set(data)
      return true
    })()
    try {
      return await refreshing
    } finally {
      refreshing = null
    }
  }

  return async function request<T>(
    endpoint: string,
    options: RequestInit = {},
    skipAuth = false,
  ): Promise<T> {
    if (!endpoint.startsWith('/') || endpoint.startsWith('//') || endpoint.includes('://')) {
      throw new Error('API endpoint must be a relative path')
    }
    const accessUsed = config.tokens.get()?.access_token
    async function send() {
      const headers = new Headers(options.headers)
      if (options.body && !(typeof FormData !== 'undefined' && options.body instanceof FormData)) {
        if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
      }
      if (!skipAuth) {
        const token = config.tokens.get()?.access_token
        if (token) headers.set('Authorization', 'Bearer ' + token)
      }
      return fetcher(base + endpoint, {
        ...options,
        headers,
        credentials: 'omit',
        cache: 'no-store',
      })
    }
    let response = await send()
    if (!skipAuth && response.status === 401 && config.refreshOn401 !== false) {
      const changed = config.tokens.get()?.access_token
      const retry = changed && changed !== accessUsed ? true : await refresh()
      if (retry) response = await send()
      if (response.status === 401) invalidate()
    }
    const data = await read(response)
    if (!response.ok) throw error(response, data)
    return data as T
  }
}
