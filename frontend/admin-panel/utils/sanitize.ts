import type { ProfileUpdate } from '../types/auth'

export function sanitizeText(input: string | null | undefined): string {
  return typeof input === 'string' ? input.trim() : ''
}

export const sanitizeEmail = (input: string): string => sanitizeText(input).toLowerCase()
export function sanitizeName(input: string | null | undefined): string {
  return Array.from(sanitizeText(input).normalize('NFC'))
    .map((char) => {
      const code = char.codePointAt(0)!
      return code < 32 ||
        (code >= 127 && code <= 159) ||
        code === 0x200b ||
        (code >= 0x202a && code <= 0x202e) ||
        (code >= 0x2066 && code <= 0x2069) ||
        code === 0xfeff
        ? ' '
        : char
    })
    .join('')
    .replace(/\s+/g, ' ')
    .trim()
}
export const sanitizePhone = (input: string | null | undefined): string => sanitizeText(input)

export function sanitizeProfile(data: ProfileUpdate): ProfileUpdate {
  const result: ProfileUpdate = {}
  for (const key of ['first_name', 'last_name', 'phone'] as const) {
    if (data[key] !== undefined)
      result[key] = (key === 'phone' ? sanitizePhone(data[key]) : sanitizeName(data[key])) || null
  }
  return result
}

export function sanitizeUrl(input: string): string {
  try {
    const url = new URL(input.trim())
    return ['http:', 'https:'].includes(url.protocol) && !url.username && !url.password
      ? url.toString()
      : ''
  } catch {
    return ''
  }
}
