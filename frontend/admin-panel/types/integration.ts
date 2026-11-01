// Current integration contract. IoT access is admin-only until per-object ACLs exist.
export type UUID = string
export interface DeviceObject {
  object_id: UUID
  devices_count: number
}
export type IntegrationStatus = 'active' | 'error' | 'disabled'
export type DeviceStatus = 'unknown' | 'online' | 'offline' | 'error'
export interface IntegrationCreate {
  name: string
  platform_type: string
  base_url: string
  organization_id: UUID
  credentials: string
}
export interface IntegrationUpdate {
  name?: string
  base_url?: string
  credentials?: string
  status?: IntegrationStatus
}
export interface Integration {
  id: UUID
  organization_id: UUID
  name: string
  platform_type: string
  base_url: string
  status: IntegrationStatus
  last_sync_at: string | null
  created_at: string
}
export interface Signal {
  id: UUID
  external_signal_id: string
  name: string
  signal_type: string
  unit: string | null
  is_writable: boolean
  min_value: number | null
  max_value: number | null
  value_type: 'number' | 'string' | 'boolean'
  source_is_writable: boolean
  is_customized: boolean
}
export interface SignalDefinition {
  id: UUID
  name: string
  value_type: Signal['value_type']
  unit: string | null
  is_writable: boolean
  min_value: number | null
  max_value: number | null
}
export interface DeviceDefinition {
  name: string
  signals: SignalDefinition[]
}
export interface Device {
  id: UUID
  integration_id: UUID
  external_id: string
  object_id: UUID
  room_id: UUID | null
  name: string
  device_type: string
  is_active: boolean
  status: DeviceStatus
  timezone: string
  polling_interval_seconds: number
  tags: string[]
  connected_at: string | null
  last_seen_at: string | null
  disconnected_at: string | null
  created_at: string
  signals: Signal[]
}
export interface DeviceUpdate {
  name?: string
  room_id?: UUID | null
  timezone?: string
  polling_interval_seconds?: number
  tags?: string[]
  is_active?: boolean
}
export interface CommandRequest {
  signal_id: UUID
  value: number | string | boolean
  idempotency_key?: string
}
export interface CommandResponse {
  command_id: UUID
  status: string
  message: string | null
  created_at: string | null
  completed_at: string | null
}
export interface DeviceState {
  device_id: UUID
  name: string
  status: DeviceStatus
  last_seen_at: string | null
  state_received_at: string | null
  quality: string
  signals: Record<string, number | string | boolean | null>
}
export interface TelemetryPoint {
  time: string
  value: number
  unit: string
  quality: string
}
export interface EmulatorSyncResult {
  integration_id: UUID
  object_id: UUID
  devices_count: number
}
