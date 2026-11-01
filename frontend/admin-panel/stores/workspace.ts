import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  getDemoContext,
  getDeviceObjects,
  getDevices,
  getDeviceState,
  prepareDemo,
} from '~/utils/api/integration'
import type { DemoContext, Device, DeviceObject, DeviceState } from '~/types/integration'

export const useWorkspaceStore = defineStore('workspace', () => {
  const context = ref<DemoContext | null>(null)
  const objects = ref<DeviceObject[]>([])
  const selectedId = ref('')
  const devices = ref<Device[]>([])
  const states = ref<Record<string, DeviceState>>({})
  const loading = ref(false)
  const preparing = ref(false)
  const initialized = ref(false)
  const error = ref('')
  let flight: Promise<void> | null = null
  let generation = 0
  const selectedName = computed(
    () =>
      objects.value.find((item) => item.object_id === selectedId.value)?.name ||
      context.value?.name ||
      'Выберите объект',
  )
  const online = computed(() => devices.value.filter((device) => device.status === 'online').length)
  const attention = computed(
    () => devices.value.filter((device) => ['offline', 'error'].includes(device.status)).length,
  )

  async function select(id: string) {
    const version = ++generation
    selectedId.value = id
    if (import.meta.client) {
      try {
        sessionStorage.setItem('ujin.selected-object', id)
      } catch {
        /* Ignore errors */
      }
    }
    devices.value = []
    states.value = {}
    if (!id) return
    loading.value = true
    error.value = ''
    try {
      const result = await getDevices(id)
      if (version !== generation) return
      devices.value = result
      const readings = await Promise.allSettled(result.map((device) => getDeviceState(device.id)))
      if (version === generation) {
        states.value = Object.fromEntries(
          readings.flatMap((reading, index) =>
            reading.status === 'fulfilled' ? [[result[index]!.id, reading.value]] : [],
          ),
        )
      }
    } catch (cause) {
      if (version === generation)
        error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить устройства'
    } finally {
      if (version === generation) loading.value = false
    }
  }

  async function refresh(preferred = '') {
    if (flight) {
      await flight
      if (preferred && preferred !== selectedId.value) await select(preferred)
      return
    }
    loading.value = true
    error.value = ''
    flight = (async () => {
      try {
        const [demo, catalogue] = await Promise.all([getDemoContext(), getDeviceObjects()])
        context.value = demo
        objects.value = catalogue
        let saved = selectedId.value
        if (!saved && import.meta.client) {
          try {
            saved = sessionStorage.getItem('ujin.selected-object') || ''
          } catch {
            /* Use the server default when storage is unavailable. */
          }
        }
        const requested = preferred || saved
        const id = catalogue.some((item) => item.object_id === requested)
          ? requested
          : catalogue.find((item) => item.object_id === demo.object_id)?.object_id ||
            catalogue[0]?.object_id ||
            demo.object_id
        await select(id)
        initialized.value = true
      } catch (cause) {
        error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить объекты'
      } finally {
        loading.value = false
      }
    })()
    try {
      await flight
    } finally {
      flight = null
    }
  }

  async function initialize(preferred = '') {
    if (!initialized.value) await refresh(preferred)
    else if (preferred && preferred !== selectedId.value) await select(preferred)
  }

  async function prepare() {
    if (preparing.value) return false
    preparing.value = true
    error.value = ''
    try {
      const result = await prepareDemo()
      await refresh(result.object_id)
      return !error.value
    } catch (cause) {
      error.value = cause instanceof Error ? cause.message : 'Не удалось подготовить демонстрацию'
      return false
    } finally {
      preparing.value = false
    }
  }
  return {
    context,
    objects,
    selectedId,
    selectedName,
    devices,
    states,
    loading,
    preparing,
    initialized,
    error,
    online,
    attention,
    select,
    refresh,
    initialize,
    prepare,
  }
})
