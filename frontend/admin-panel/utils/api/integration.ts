import { http } from './httpClient'
import type { DeviceObject } from '../../types/integration'
import type { DeviceDefinition } from '../../types/integration'
import type {
  Integration,
  IntegrationCreate,
  IntegrationUpdate,
  Device,
  DeviceUpdate,
  CommandRequest,
  CommandResponse,
  DeviceState,
  TelemetryPoint,
  EmulatorSyncResult,
} from '../../types/integration'

// Shared authenticated gateway client; refresh is coordinated with auth requests.
const request = <T>(path: string, options: RequestInit = {}) => http<T>(path, options)
export const getIntegrations = (organizationId: string) =>
  request<Integration[]>(`/integrations/?organization_id=${encodeURIComponent(organizationId)}`)
export const getIntegration = (id: string) =>
  request<Integration>(`/integrations/${encodeURIComponent(id)}`)
export const createIntegration = (data: IntegrationCreate) =>
  request<Integration>('/integrations/', { method: 'POST', body: JSON.stringify(data) })
export const updateIntegration = (id: string, data: IntegrationUpdate) =>
  request<Integration>(`/integrations/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
export const deleteIntegration = (id: string) =>
  request<void>(`/integrations/${encodeURIComponent(id)}`, { method: 'DELETE' })
export const getDevices = (objectId: string, roomId?: string) => {
  const query = new URLSearchParams({ object_id: objectId })
  if (roomId) query.set('room_id', roomId)
  return request<Device[]>('/devices/?' + query)
}
export const getDevice = (id: string) => request<Device>(`/devices/${encodeURIComponent(id)}`)
export const saveDeviceDefinition = (id: string, data: DeviceDefinition) =>
  request<Device>(`/devices/${encodeURIComponent(id)}/definition`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
export const getDeviceObjects = () => request<DeviceObject[]>('/devices/objects')
export const updateDevice = (id: string, data: DeviceUpdate) =>
  request<Device>(`/devices/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
export const sendCommand = (id: string, data: CommandRequest) =>
  request<CommandResponse>(`/commands/${encodeURIComponent(id)}/send`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
export const getDeviceState = (id: string) =>
  request<DeviceState>(`/devices/${encodeURIComponent(id)}/state`)
export const getDeviceHistory = (id: string, signalName: string, limit = 100) =>
  request<TelemetryPoint[]>(
    `/devices/${encodeURIComponent(id)}/history?${new URLSearchParams({ signal_name: signalName, limit: String(limit) })}`,
  )
export const syncEmulators = (organizationId: string, objectId: string) =>
  request<EmulatorSyncResult>('/integrations/emulators/sync', {
    method: 'POST',
    body: JSON.stringify({ organization_id: organizationId, object_id: objectId }),
  })
