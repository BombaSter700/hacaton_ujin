import type { UUID } from './integration'

export type SignalValue = number | string | boolean
export type Operator = 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte'
export interface SignalCondition {
  kind: 'signal'
  device_id: UUID
  signal_id: UUID
  operator: Operator
  value: SignalValue
}
export interface TimeCondition {
  kind: 'time'
  start_time: string
  end_time: string
  timezone: string
}
export type ScenarioCondition = SignalCondition | TimeCondition
export interface ScenarioAction {
  device_id: UUID
  signal_id: UUID
  value: SignalValue
}
export interface ScenarioInput {
  object_id: UUID
  name: string
  description: string
  enabled: boolean
  match_mode: 'all' | 'any'
  conditions: ScenarioCondition[]
  actions: ScenarioAction[]
}
export interface Scenario extends ScenarioInput {
  id: UUID
  revision: number
  created_by: number
  created_at: string
  updated_at: string
}
export interface ScenarioPage {
  items: Scenario[]
  total: number
}
