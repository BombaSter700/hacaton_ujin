import { useRuntimeConfig } from '#app'
import type { TokenResponse } from '../../types/auth'
import { createHttpClient, validTokens, type TokenStore } from './transport'
export { ApiError } from './transport'

const KEY = 'programmisto.auth'
export const tokenStore: TokenStore = {
  get() {
    if (typeof window === 'undefined') return null
    try {
      const data = JSON.parse(window.sessionStorage.getItem(KEY) ?? 'null')
      return validTokens(data) ? data : null
    } catch { return null }
  },
  set(tokens: TokenResponse) {
    if (!validTokens(tokens)) throw new Error('Invalid token response')
    if (typeof window !== 'undefined') window.sessionStorage.setItem(KEY, JSON.stringify(tokens))
  },
  clear() { if (typeof window !== 'undefined') window.sessionStorage.removeItem(KEY) },
}
let client: ReturnType<typeof createHttpClient> | undefined

export function configureApiClients(apiUrl: string) {
  client = createHttpClient({
    baseUrl: apiUrl, tokens: tokenStore,
    onUnauthorized: () => window.dispatchEvent(new Event('programmisto:unauthorized')),
  })
}
export function http<T>(endpoint: string, options: RequestInit = {}, skipAuth = false): Promise<T> {
  if (typeof window === 'undefined') throw new Error('Authenticated API calls must run on the client')
  if (!client) configureApiClients(String(useRuntimeConfig().public.apiUrl || ''))
  // Auth and integration share the gateway and one in-flight refresh.
  return client!<T>(endpoint, options, skipAuth)
}
