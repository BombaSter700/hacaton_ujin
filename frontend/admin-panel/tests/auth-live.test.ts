import { expect, it } from 'vitest'
import { createHttpClient, type TokenStore } from '../utils/api/transport'
import type { TokenResponse, User, SessionListResponse } from '../types/auth'

// Opt-in against a local disposable account; the caller removes it afterwards.
it.skipIf(!process.env.AUTH_SMOKE_URL)(
  'auth roundtrip through the running gateway',
  async () => {
    const email = process.env.FRONTEND_SMOKE_EMAIL!
    const password = process.env.FRONTEND_SMOKE_PASSWORD!
    if (!email?.startsWith('frontend-smoke-') || !password)
      throw new Error('Disposable test credentials required')
    let value: TokenResponse | null = null
    const tokens: TokenStore = {
      get: () => value,
      set: (next) => {
        value = next
      },
      clear: () => {
        value = null
      },
    }
    const request = createHttpClient({ baseUrl: process.env.AUTH_SMOKE_URL!, tokens })
    const user = await request<User>(
      '/auth/register',
      { method: 'POST', body: JSON.stringify({ email, password }) },
      true,
    )
    expect(user.role).toBe('client')
    expect(Number.isInteger(user.id)).toBe(true)
    expect('access_token' in user).toBe(false)
    const login = await request<TokenResponse>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify({ email, password }) },
      true,
    )
    tokens.set(login)
    expect((await request<User>('/auth/me')).id).toBe(user.id)
    const updated = await request<User>('/users/me', {
      method: 'PATCH',
      body: JSON.stringify({ first_name: 'Frontend smoke', phone: null }),
    })
    expect(updated.first_name).toBe('Frontend smoke')
    const sessions = await request<SessionListResponse>('/sessions/')
    expect(sessions.sessions.some((item) => item.is_current)).toBe(true)
    tokens.set({ ...login, access_token: 'invalid-access-token-for-refresh-test' })
    expect((await request<User>('/auth/me')).id).toBe(user.id)
    expect(tokens.get()?.refresh_token !== login.refresh_token).toBe(true)
    await expect(
      request(
        '/auth/refresh',
        { method: 'POST', body: JSON.stringify({ refresh_token: login.refresh_token }) },
        true,
      ),
    ).rejects.toMatchObject({ status: 401 })
    await expect(request('/users/')).rejects.toMatchObject({ status: 403 })
    expect(await request('/auth/logout', { method: 'POST' })).toBeUndefined()
    await expect(request('/auth/me')).rejects.toMatchObject({ status: 401 })
    expect(tokens.get()).toBeNull()
  },
  30000,
)
