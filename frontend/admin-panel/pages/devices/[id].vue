<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import {
  deviceName,
  deviceTypeLabel,
  signalName,
  signalValueLabel,
  signalOptions,
  displayLabel,
} from '~/utils/device-labels'
import { formatDateTime, formatDeviceStatus, formatNumber } from '~/utils/format'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table'
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getDevice, getDeviceState, getDeviceHistory, sendCommand } from '~/utils/api/integration'
import type { Device, DeviceState, Signal, TelemetryPoint } from '~/types/integration'
import DeviceDefinitionEditor from '~/components/DeviceDefinitionEditor.vue'
import { parseSignalValue } from '~/utils/signal-values'
import { useAuthStore } from '~/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
const route = useRoute()
const auth = useAuthStore()
const device = ref<Device | null>(null)
const state = ref<DeviceState | null>(null)
const history = ref<TelemetryPoint[]>([])
const selectedSignal = ref('')
const error = ref('')
const stateError = ref('')
const historyError = ref('')
const commandMessage = ref('')
const commandError = ref('')
const loading = ref(false)
const historyLoading = ref(false)
const sending = ref(false)
const drafts = reactive<Record<string, string | number>>({})
let generation = 0
let timer: ReturnType<typeof setInterval> | undefined
const message = (e: unknown) => (e instanceof Error ? e.message : 'Не удалось выполнить запрос')
async function refreshState() {
  const version = generation
  const id = String(route.params.id)
  try {
    const result = await getDeviceState(id)
    if (version === generation) {
      state.value = result
      stateError.value = ''
    }
  } catch (e) {
    if (version === generation) stateError.value = message(e)
  }
}
async function loadHistory() {
  if (!selectedSignal.value) return
  const version = generation
  const signal = selectedSignal.value
  historyLoading.value = true
  historyError.value = ''
  try {
    const result = await getDeviceHistory(String(route.params.id), signal)
    if (version === generation && selectedSignal.value === signal) history.value = result
  } catch (e) {
    if (version === generation) {
      historyError.value = message(e)
      history.value = []
    }
  } finally {
    if (version === generation) historyLoading.value = false
  }
}
async function load() {
  generation++
  const version = generation
  device.value = null
  state.value = null
  history.value = []
  error.value = ''
  commandMessage.value = ''
  loading.value = true
  try {
    const result = await getDevice(String(route.params.id))
    if (version !== generation) return
    device.value = result
    selectedSignal.value =
      result.signals.find((signal) => signal.value_type !== 'string')?.external_signal_id || ''
    await Promise.all([refreshState(), loadHistory()])
  } catch (e) {
    if (version === generation) error.value = message(e)
  } finally {
    if (version === generation) loading.value = false
  }
}
async function command(signal: Signal) {
  if (sending.value) return
  commandError.value = ''
  commandMessage.value = ''
  const raw = String(drafts[signal.id] ?? '').trim()
  if (!raw) {
    commandError.value = 'Введите значение команды'
    return
  }
  let value: string | number | boolean
  try {
    value = parseSignalValue(signal, raw)
  } catch (cause) {
    commandError.value = message(cause)
    return
  }
  sending.value = true
  const version = generation
  try {
    const result = await sendCommand(String(route.params.id), {
      signal_id: signal.id,
      value,
      idempotency_key: crypto.randomUUID(),
    })
    if (version !== generation) return
    const labels: Record<string, string> = {
      success: 'Выполнено, устройство подтвердило изменение',
      failed: 'Команда не выполнена',
      timeout: 'Устройство не подтвердило изменение вовремя',
      pending: 'Команда принята',
    }
    commandMessage.value = labels[result.status] || result.status
    if (result.status !== 'success' && result.message) commandMessage.value += ': ' + result.message
    await refreshState()
  } catch (e) {
    if (version === generation) commandError.value = message(e)
  } finally {
    sending.value = false
  }
}
onMounted(() => {
  if (auth.user?.role === 'admin') {
    void load()
    timer = setInterval(() => {
      if (!loading.value) void refreshState()
    }, 10000)
  }
})
watch(
  () => route.params.id,
  () => {
    if (auth.user?.role === 'admin') void load()
  },
)
onBeforeUnmount(() => {
  generation++
  if (timer) clearInterval(timer)
})
</script>
<template>
  <div class="space-y-6">
    <Button variant="outline" as-child><NuxtLink to="/devices">К устройствам</NuxtLink></Button>
    <p v-if="auth.user?.role !== 'admin'">Доступ предоставляется администратору.</p>
    <Skeleton v-if="loading" class="h-32 w-full" role="status" aria-label="Загрузка устройства" />
    <Alert v-if="error" variant="destructive">
      <AlertDescription>{{ error }}</AlertDescription>
    </Alert>
    <template v-if="device">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-2xl font-bold">{{ deviceName(device) }}</h1>
          <p class="text-muted-foreground">{{ deviceTypeLabel(device.device_type) }}</p>
        </div>
        <Badge :variant="(state?.status || device.status) === 'error' ? 'destructive' : 'outline'">
          {{ formatDeviceStatus(state?.status || device.status) }}
        </Badge>
      </div>
      <Tabs default-value="control">
        <TabsList class="mb-4">
          <TabsTrigger value="control">Показания и управление</TabsTrigger>
          <TabsTrigger value="history">История</TabsTrigger>
          <TabsTrigger value="settings">Настройки</TabsTrigger>
        </TabsList>
        <TabsContent value="control" force-mount class="space-y-4 data-[state=inactive]:hidden">
          <Card>
            <CardHeader><CardTitle>Текущее состояние</CardTitle></CardHeader>
            <CardContent class="space-y-3">
              <p class="text-sm text-muted-foreground">
                Последняя связь: {{ formatDateTime(state?.last_seen_at || device.last_seen_at) }}
              </p>
              <p class="text-sm text-muted-foreground">
                Данные: {{ displayLabel(state?.quality) }} · Обновляются каждые 10 секунд
              </p>
              <Alert v-if="stateError" variant="destructive">
                <AlertDescription>{{ stateError }}</AlertDescription>
              </Alert>
              <Button variant="outline" @click="refreshState">Обновить показания</Button>
            </CardContent>
          </Card>
          <Empty v-if="!device.signals.length">
            <EmptyHeader>
              <EmptyDescription>Показатели пока не зарегистрированы.</EmptyDescription>
            </EmptyHeader>
          </Empty>
          <div class="grid gap-4 md:grid-cols-2">
            <Card v-for="signal in device.signals" :key="signal.id">
              <CardHeader>
                <CardTitle class="text-base">{{ signalName(signal) }}</CardTitle>
              </CardHeader>
              <CardContent class="space-y-3">
                <p class="text-2xl font-semibold">
                  {{
                    signalValueLabel(
                      device.device_type,
                      signal,
                      state?.signals[signal.external_signal_id],
                    )
                  }}
                  <span class="text-base text-muted-foreground">{{ signal.unit }}</span>
                </p>
                <form
                  v-if="signal.is_writable"
                  class="flex flex-wrap gap-2"
                  @submit.prevent="command(signal)"
                >
                  <label :for="'command-' + signal.id" class="sr-only">
                    Новое значение: {{ signalName(signal) }}
                  </label>
                  <Select
                    v-if="signalOptions(device.device_type, signal).length"
                    :model-value="drafts[signal.id] || null"
                    :disabled="sending || !device.is_active"
                    @update:model-value="drafts[signal.id] = String($event)"
                  >
                    <SelectTrigger :id="'command-' + signal.id" class="w-full">
                      <SelectValue placeholder="Выберите действие" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem
                        v-for="option in signalOptions(device.device_type, signal)"
                        :key="option.value"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    v-else
                    :id="'command-' + signal.id"
                    v-model="drafts[signal.id]"
                    :type="signal.value_type === 'number' ? 'number' : 'text'"
                    :min="signal.min_value ?? undefined"
                    :max="signal.max_value ?? undefined"
                    step="any"
                    required
                    placeholder="Новое значение"
                    :disabled="sending || !device.is_active"
                  />
                  <Button
                    type="submit"
                    :disabled="
                      sending || !device.is_active || String(drafts[signal.id] ?? '').trim() === ''
                    "
                  >
                    {{ sending ? 'Ожидание подтверждения…' : 'Отправить' }}
                  </Button>
                </form>
                <p v-else class="text-xs text-muted-foreground">Только просмотр</p>
              </CardContent>
            </Card>
          </div>
          <Alert v-if="commandMessage" role="status">
            <AlertDescription>{{ commandMessage }}</AlertDescription>
          </Alert>
          <Alert v-if="commandError" variant="destructive">
            <AlertDescription>{{ commandError }}</AlertDescription>
          </Alert>
        </TabsContent>
        <TabsContent value="history" force-mount class="data-[state=inactive]:hidden">
          <Card>
            <CardHeader><CardTitle>История показаний</CardTitle></CardHeader>
            <CardContent class="space-y-4">
              <form class="flex flex-wrap gap-2" @submit.prevent="loadHistory">
                <label for="history-signal" class="sr-only">Показатель</label>
                <Select
                  v-model="selectedSignal"
                  name="selectedSignal"
                  @update:model-value="loadHistory"
                >
                  <SelectTrigger id="history-signal" class="w-full">
                    <SelectValue placeholder="Выберите показатель" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem
                      v-for="signal in device.signals.filter(
                        (item) => item.value_type !== 'string',
                      )"
                      :key="signal.id"
                      :value="signal.external_signal_id"
                    >
                      {{ signalName(signal) }}
                    </SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  type="submit"
                  :disabled="historyLoading || !selectedSignal"
                >
                  Обновить историю
                </Button>
              </form>
              <Skeleton
                v-if="historyLoading"
                class="h-24 w-full"
                role="status"
                aria-label="Загрузка истории"
              />
              <Alert v-else-if="historyError" variant="destructive">
                <AlertDescription>{{ historyError }}</AlertDescription>
              </Alert>
              <Empty v-else-if="!history.length">
                <EmptyHeader>
                  <EmptyDescription>
                    Записей пока нет. Числовые и логические показания появятся после обновления
                    устройств.
                  </EmptyDescription>
                </EmptyHeader>
              </Empty>
              <div v-else class="max-h-96 overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Время</TableHead>
                      <TableHead>Значение</TableHead>
                      <TableHead>Качество</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow v-for="(point, index) in history" :key="index">
                      <TableCell>{{ formatDateTime(point.time) }}</TableCell>
                      <TableCell>{{ formatNumber(point.value) }} {{ point.unit }}</TableCell>
                      <TableCell>{{ displayLabel(point.quality) }}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="settings" force-mount class="space-y-4 data-[state=inactive]:hidden">
          <DeviceDefinitionEditor :key="device.id" :device="device" @saved="device = $event" />
          <Collapsible class="rounded-lg border p-4">
            <CollapsibleTrigger class="text-sm font-medium underline">
              Технические сведения
            </CollapsibleTrigger>
            <CollapsibleContent class="space-y-2 break-all pt-4 text-xs text-muted-foreground">
              <p>UUID: {{ device.id }}</p>
              <p>Внешний код: {{ device.external_id }}</p>
              <p>Получены показания: {{ formatDateTime(state?.state_received_at) }}</p>
              <p v-for="signal in device.signals" :key="signal.id">
                {{ signalName(signal) }}: {{ signal.external_signal_id }} ·
                {{ signal.min_value ?? '—' }} … {{ signal.max_value ?? '—' }}
              </p>
            </CollapsibleContent>
          </Collapsible>
        </TabsContent>
      </Tabs>
    </template>
  </div>
</template>
