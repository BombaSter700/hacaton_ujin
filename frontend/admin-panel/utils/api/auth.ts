import { http } from './httpClient'
import type {
  LoginRequest,
  RegisterRequest,
  ProfileUpdate,
  TokenResponse,
  User,
  SessionListResponse,
} from '../../types/auth'

export const login = (data: LoginRequest) =>
  http<TokenResponse>('/auth/login', { method: 'POST', body: JSON.stringify(data) }, true)
export const getDemoStatus = () =>
  http<{ enabled: boolean }>('/auth/demo', { cache: 'no-store' }, true)
export const demoLogin = () => http<TokenResponse>('/auth/demo', { method: 'POST' }, true)
export const register = (data: RegisterRequest) =>
  http<User>('/auth/register', { method: 'POST', body: JSON.stringify(data) }, true)
export const refresh = (refresh_token: string) =>
  http<TokenResponse>(
    '/auth/refresh',
    { method: 'POST', body: JSON.stringify({ refresh_token }) },
    true,
  )
export const getProfile = () => http<User>('/auth/me')
export const updateProfile = (data: ProfileUpdate) =>
  http<User>('/users/me', { method: 'PATCH', body: JSON.stringify(data) })
export const logout = () => http<void>('/auth/logout', { method: 'POST' })
export const getSessions = () => http<SessionListResponse>('/sessions/')
export const revokeSession = (id: number) =>
  http<{ success: boolean }>(`/sessions/${id}`, { method: 'DELETE' })
export const getUsers = (skip = 0, limit = 100) =>
  http<User[]>(`/users/?skip=${skip}&limit=${limit}`)
