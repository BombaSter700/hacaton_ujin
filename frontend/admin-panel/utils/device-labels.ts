import type { Device, DeviceState, Signal } from '../types/integration'
import { sanitizeName } from './sanitize'
import { formatSignalValue } from './format'

const families: Record<string, string> = {
  leak: 'Датчик протечки',
  barrier: 'Шлагбаум',
  thermostat: 'Термостат',
  elevator: 'Лифт',
  hub: 'Центр защиты от протечек',
  counter: 'Счётчик',
  ventilation: 'Вентиляция',
  fire: 'Пожарный датчик',
  light: 'Освещение',
}
const words: Record<string, string> = {
  temperature: 'Температура',
  target_temp: 'Целевая температура',
  floor: 'Этаж',
  floor_current: 'Текущий этаж',
  floor_destination: 'Этаж назначения',
  direction: 'Направление',
  door: 'Двери',
  speed: 'Скорость',
  mode: 'Режим',
  state: 'Состояние',
  status: 'Состояние',
  lamp: 'Свет',
  brightness: 'Яркость',
  power_w: 'Мощность',
  energy_kwh: 'Энергия',
  call_requested: 'Вызвать на этаж',
  fan_speed: 'Скорость вентилятора',
  co2: 'Уровень CO₂',
  supply_temp: 'Температура притока',
  pm25: 'Мелкодисперсные частицы PM2.5',
  leak: 'Протечка',
  alarm: 'Тревога',
  battery: 'Заряд батареи',
  online: 'В сети',
  open_cmd: 'Открыть',
  close_cmd: 'Закрыть',
  emergency_btn: 'Аварийная остановка',
  boolean: 'Да / нет',
  number: 'Число',
  string: 'Текст',
  emulator: 'Демонстрационные устройства',
  Emulators: 'Демонстрационные устройства',
  good: 'Актуальные',
  unknown: 'Нет данных',
  stale: 'Устаревшие',
  offline: 'Нет связи',
  error: 'Ошибка',
  success: 'Выполнено',
  pending: 'Ожидание',
  failed: 'Не выполнено',
  timeout: 'Нет подтверждения',
  true: 'Да',
  false: 'Нет',
  on: 'Включено',
  off: 'Выключено',
  open: 'Открыто',
  closed: 'Закрыто',
}
export function displayLabel(value: string | null | undefined): string {
  const text = sanitizeName(value)
  return words[text] || families[text.replace(/^emul_/, '')] || text || 'Нет данных'
}
export const deviceTypeLabel = (type: string): string =>
  families[type.replace(/^emul_/, '')] || displayLabel(type)
export const deviceName = (device: Pick<Device, 'name' | 'device_type'>): string =>
  device.name === device.device_type || device.name === 'emul_' + device.device_type
    ? deviceTypeLabel(device.device_type)
    : displayLabel(device.name)
export const signalName = (
  signal: Pick<Signal, 'name' | 'external_signal_id' | 'is_customized'>,
): string =>
  signal.is_customized
    ? sanitizeName(signal.name)
    : displayLabel(signal.name || signal.external_signal_id)

const layouts: Record<string, Record<string, Record<string, string>>> = {
  elevator: {
    direction: { '0': 'Стоит', '1': 'Движется вверх', '2': 'Движется вниз' },
    door: { '0': 'Двери закрыты', '1': 'Двери открыты' },
  },
  barrier: {
    state: {
      '0': 'Закрыт',
      '1': 'Открывается',
      '2': 'Открыт',
      '3': 'Закрывается',
      '4': 'Удержание',
    },
  },
  thermostat: {
    mode: { '0': 'Выключен', '1': 'Нагрев', '2': 'Охлаждение', '3': 'Автоматический' },
    output: { '0': 'Ожидание', '1': 'Нагрев', '2': 'Охлаждение' },
  },
  ventilation: { mode: { '0': 'Выключена', '1': 'Автоматический', '2': 'Ручной' } },
  light: { lamp: { '0': 'Выключен', '1': 'Включён' } },
}
export function signalValueLabel(type: string, signal: Signal, value: unknown): string {
  const translated =
    layouts[type.replace(/^emul_/, '')]?.[signal.external_signal_id]?.[String(value)]
  return translated || (typeof value === 'string' ? displayLabel(value) : formatSignalValue(value))
}

export function signalOptions(type: string, signal: Signal): { value: string; label: string }[] {
  if (signal.value_type === 'boolean')
    return [
      { value: 'true', label: 'Да' },
      { value: 'false', label: 'Нет' },
    ]
  if (signal.value_type !== 'number') return []
  return Object.entries(layouts[type.replace(/^emul_/, '')]?.[signal.external_signal_id] || {})
    .filter(
      ([value]) =>
        (signal.min_value === null || Number(value) >= signal.min_value) &&
        (signal.max_value === null || Number(value) <= signal.max_value),
    )
    .map(([value, label]) => ({ value, label }))
}

export function primaryReading(device: Device, state?: DeviceState): string {
  const preferred = [
    'floor',
    'floor_current',
    'temperature',
    'co2',
    'power_w',
    'leak',
    'alarm',
    'state',
  ]
  const signal =
    preferred
      .map((key) => device.signals.find((item) => item.external_signal_id === key))
      .find(Boolean) || device.signals.find((item) => !item.is_writable)
  if (!signal || !state) return 'Показания пока недоступны'
  const value = signalValueLabel(
    device.device_type,
    signal,
    state.signals[signal.external_signal_id],
  )
  return `${signalName(signal)}: ${value}${signal.unit ? ' ' + signal.unit : ''}`
}
