import type { ProfileUpdate } from '../types/auth'

export function validateEmail(email: string): string {
  if (!email) return 'Введите email'
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return 'Некорректный email'
  }
  return ''
}

export function validatePassword(password: string, registration = true): string {
  if (!password) return 'Введите пароль'
  if (registration && Array.from(password).length < 8) {
    return 'Пароль должен содержать не менее 8 символов'
  }
  if (new TextEncoder().encode(password).length > 72) {
    return 'Пароль должен занимать не более 72 байт UTF-8'
  }
  return ''
}

export function validateProfile(data: ProfileUpdate): string {
  if (Array.from(data.first_name || '').length > 50) return 'Имя: максимум 50 символов'
  if (Array.from(data.last_name || '').length > 50) return 'Фамилия: максимум 50 символов'
  if (Array.from(data.phone || '').length > 20) return 'Телефон: максимум 20 символов'
  return ''
}

export function validateUuid(value: string, label = 'Идентификатор'): string {
  return /^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$/i.test(value)
    ? ''
    : `${label}: укажите корректный UUID`
}

export function assertValid(...errors: string[]): void {
  const error = errors.find(Boolean)
  if (error) throw new Error(error)
}
