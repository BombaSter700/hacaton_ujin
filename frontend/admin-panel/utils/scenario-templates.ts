import type { Device } from '../types/integration'
import type { ScenarioInput } from '../types/scenario'

export type ScenarioTemplate = Pick<
  ScenarioInput,
  'name' | 'description' | 'conditions' | 'actions'
>
export function scenarioTemplates(devices: Device[]): ScenarioTemplate[] {
  const result: ScenarioTemplate[] = []
  for (const device of devices) {
    const writable = (key: string) =>
      device.signals.find(
        (signal) =>
          signal.external_signal_id === key && signal.is_writable && signal.value_type === 'number',
      )
    const co2 = device.signals.find(
      (signal) => signal.external_signal_id === 'co2' && signal.value_type === 'number',
    )
    const fan = writable('fan_speed')
    if (
      co2 &&
      fan &&
      (fan.min_value === null || fan.min_value <= 3) &&
      (fan.max_value === null || fan.max_value >= 3)
    ) {
      result.push({
        name: 'Свежий воздух',
        description: 'При CO₂ выше 1000 ppm увеличить скорость вентиляции.',
        conditions: [
          { kind: 'signal', device_id: device.id, signal_id: co2.id, operator: 'gt', value: 1000 },
        ],
        actions: [{ device_id: device.id, signal_id: fan.id, value: 3 }],
      })
    }
    const lamp = writable('lamp')
    if (
      lamp &&
      (lamp.min_value === null || lamp.min_value <= 1) &&
      (lamp.max_value === null || lamp.max_value >= 1)
    ) {
      result.push({
        name: 'Вечернее освещение',
        description: 'Включить освещение с 18:00 до 23:00.',
        conditions: [
          {
            kind: 'time',
            start_time: '18:00',
            end_time: '23:00',
            timezone: device.timezone || 'Europe/Moscow',
          },
        ],
        actions: [{ device_id: device.id, signal_id: lamp.id, value: 1 }],
      })
    }
  }
  return result
}
