import { describe, expect, it } from 'vitest'
import { parseSignalValue } from '../utils/signal-values'

describe('typed values for commands and scenario thresholds', () => {
  const numeric = { value_type: 'number' as const, min_value: 16, max_value: 30 }
  it('preserves numeric zero, decimals and checks command bounds', () => {
    expect(parseSignalValue({ ...numeric, min_value: 0 }, '0')).toBe(0)
    expect(parseSignalValue(numeric, '24.5')).toBe(24.5)
    expect(parseSignalValue(numeric, 24.5)).toBe(24.5)
    expect(() => parseSignalValue(numeric, '31')).toThrow()
    expect(() => parseSignalValue(numeric, 'Infinity')).toThrow()
    expect(() => parseSignalValue(numeric, '')).toThrow()
  })
  it('allows thresholds outside the command range', () => {
    expect(parseSignalValue(numeric, '40', false)).toBe(40)
  })
  it('does not convert false into true or accept numeric booleans', () => {
    const boolean = { ...numeric, value_type: 'boolean' as const }
    expect(parseSignalValue(boolean, 'false')).toBe(false)
    expect(parseSignalValue(boolean, 'true')).toBe(true)
    expect(() => parseSignalValue(boolean, '0')).toThrow()
  })
  it('preserves text values', () => {
    expect(parseSignalValue({ ...numeric, value_type: 'string' }, 'night')).toBe('night')
  })
})
