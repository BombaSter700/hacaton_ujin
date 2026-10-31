export type UserRole = 'admin' | 'client'
export interface User {
  id: number
  email: string
  role: UserRole
  is_active: boolean
  first_name: string | null
  last_name: string | null
  phone: string | null
  created_at: string
  updated_at: string | null
}
export interface LoginRequest { email: string; password: string }
export type LoginCredentials = LoginRequest
export interface RegisterRequest extends LoginRequest {
  first_name?: string | null
  last_name?: string | null
  phone?: string | null
}
export type RegisterCredentials = RegisterRequest
export interface ProfileUpdate {
  first_name?: string | null
  last_name?: string | null
  phone?: string | null
}
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  refresh_expires_in: number
}
export interface RefreshRequest { refresh_token: string }
export interface UserSession {
  id: number
  is_active: boolean
  is_current: boolean
  created_at: string
  last_activity_at: string
  expires_at: string
}
export interface SessionListResponse { sessions: UserSession[]; total: number }
export interface ValidationIssue { loc: (string | number)[]; msg: string; type: string }
export interface AuthError { detail: string | ValidationIssue[]; error_code?: string }
