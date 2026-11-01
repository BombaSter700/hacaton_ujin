import type { Signal } from '~/types/integration'

export function parseSignalValue(
  signal: Pick<Signal, 'value_type' | 'min_value' | 'max_value'>,
  input: string | number,
  checkRange = true,
): string | number | boolean {
  const text = String(input)
  if (!text.trim()) throw new Error('Введите значение')
  if (signal.value_type === 'boolean') {
    if (!['true', 'false'].includes(text.trim().toLowerCase()))
      throw new Error('Выберите true или false')
    return text.trim().toLowerCase() === 'true'
  }
  if (signal.value_type === 'string') return text
  const value = Number(text)
  if (!Number.isFinite(value)) throw new Error('Введите конечное число')
  if (
    checkRange &&
    ((signal.min_value !== null && value < signal.min_value) ||
      (signal.max_value !== null && value > signal.max_value))
  )
    throw new Error('Значение вне допустимого диапазона')
  return value
}
