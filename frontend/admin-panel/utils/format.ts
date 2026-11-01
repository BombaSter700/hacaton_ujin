import type { UserRole } from '../types/auth'
import type { DeviceStatus, IntegrationStatus } from '../types/integration'

type DateInput = string | number | Date | null | undefined
export const NO_DATA = 'Нет данных'

function dateValue(value: DateInput): Date | null {
  if (value === null || value === undefined || value === '') return null
  const date = value instanceof Date ? value : new Date(value)
  return Number.isFinite(date.getTime()) ? date : null
}

export function formatDate(value: DateInput, locale = 'ru-RU'): string {
  const date = dateValue(value)
  return date ? date.toLocaleDateString(locale) : NO_DATA
}

export function formatDateTime(value: DateInput, locale = 'ru-RU'): string {
  const date = dateValue(value)
  return date
    ? date.toLocaleString(locale, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    : NO_DATA
}

export function formatRelativeTime(value: DateInput, now = Date.now()): string {
  const date = dateValue(value)
  if (!date || !Number.isFinite(now)) return NO_DATA
  const seconds = Math.round((date.getTime() - now) / 1000)
  const formatter = new Intl.RelativeTimeFormat('ru-RU', { numeric: 'auto' })
  if (Math.abs(seconds) < 60) return formatter.format(seconds, 'second')
  if (Math.abs(seconds) < 3600) return formatter.format(Math.round(seconds / 60), 'minute')
  if (Math.abs(seconds) < 86400) return formatter.format(Math.round(seconds / 3600), 'hour')
  return formatter.format(Math.round(seconds / 86400), 'day')
}

export function formatNumber(value: number | null | undefined, locale = 'ru-RU'): string {
  return typeof value === 'number' && Number.isFinite(value)
    ? new Intl.NumberFormat(locale, { maximumFractionDigits: 6 }).format(value)
    : '—'
}

export function formatSignalValue(value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'boolean') return value ? 'Да' : 'Нет'
  if (typeof value === 'number') return formatNumber(value)
  return String(value)
}

export function formatFullName(
  firstName?: string | null,
  lastName?: string | null,
  fallback = 'Без имени',
): string {
  return [firstName?.trim(), lastName?.trim()].filter(Boolean).join(' ') || fallback
}

export function formatInitials(firstName?: string | null, lastName?: string | null): string {
  return (
    [firstName, lastName]
      .map((value) => Array.from(value?.trim() || '')[0]?.toLocaleUpperCase('ru-RU') || '')
      .join('') || '?'
  )
}

export function formatPhone(phone: string | null | undefined): string {
  if (!phone?.trim()) return NO_DATA
  const digits = phone.replace(/\D/g, '')
  if (digits.length === 11 && ['7', '8'].includes(digits[0]!)) {
    return `+7 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7, 9)}-${digits.slice(9)}`
  }
  return phone.trim()
}

export function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return NO_DATA
  if (seconds < 60) return `${Math.floor(seconds)} сек`
  if (seconds < 3600) return `${Math.floor(seconds / 60)} мин`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} ч`
  const hours = Math.floor((seconds % 86400) / 3600)
  return `${Math.floor(seconds / 86400)} дн${hours ? ` ${hours} ч` : ''}`
}

export const formatDeviceStatus = (status: DeviceStatus): string =>
  ({ unknown: 'Нет данных', online: 'В сети', offline: 'Нет связи', error: 'Ошибка' })[status] ||
  status

export const formatIntegrationStatus = (status: IntegrationStatus): string =>
  ({ active: 'Активно', error: 'Ошибка', disabled: 'Отключено' })[status] || status

export const formatUserRole = (role: UserRole): string =>
  ({ admin: 'Администратор', client: 'Клиент' })[role] || role
