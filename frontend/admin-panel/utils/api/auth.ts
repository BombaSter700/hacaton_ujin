import { http } from './httpClient'
import { sanitizeEmail, sanitizeProfile } from '../sanitize'
import { assertValid, validateEmail, validatePassword, validateProfile } from '../validation'
import type {
  LoginRequest,
  RegisterRequest,
  ProfileUpdate,
  TokenResponse,
  User,
  SessionListResponse,
} from '../../types/auth'

export const login = async (data: LoginRequest) => {
  const email = sanitizeEmail(data.email)
  assertValid(validateEmail(email), validatePassword(data.password, false))
  return http<TokenResponse>(
    '/auth/login',
    {
      method: 'POST',
      body: JSON.stringify({ email, password: data.password }),
    },
    true,
  )
}
export const getDemoStatus = () =>
  http<{ enabled: boolean }>('/auth/demo', { cache: 'no-store' }, true)
export const demoLogin = () => http<TokenResponse>('/auth/demo', { method: 'POST' }, true)
export const register = async (data: RegisterRequest) => {
  const email = sanitizeEmail(data.email)
  const profile = sanitizeProfile(data)
  assertValid(validateEmail(email), validatePassword(data.password), validateProfile(profile))
  return http<User>(
    '/auth/register',
    {
      method: 'POST',
      body: JSON.stringify({ ...profile, email, password: data.password }),
    },
    true,
  )
}
export const refresh = (refresh_token: string) =>
  http<TokenResponse>(
    '/auth/refresh',
    { method: 'POST', body: JSON.stringify({ refresh_token }) },
    true,
  )
export const getProfile = () => http<User>('/auth/me')
export const updateProfile = async (data: ProfileUpdate) => {
  const profile = sanitizeProfile(data)
  assertValid(validateProfile(profile))
  return http<User>('/users/me', { method: 'PATCH', body: JSON.stringify(profile) })
}
export const logout = () => http<void>('/auth/logout', { method: 'POST' })
export const getSessions = () => http<SessionListResponse>('/sessions/')
export const revokeSession = (id: number) =>
  http<{ success: boolean }>(`/sessions/${id}`, { method: 'DELETE' })
export const getUsers = (skip = 0, limit = 100) =>
  http<User[]>(`/users/?skip=${skip}&limit=${limit}`)
