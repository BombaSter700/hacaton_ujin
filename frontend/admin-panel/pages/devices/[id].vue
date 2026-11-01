<script setup lang="ts">
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
const drafts = reactive<Record<string, string>>({})
let generation = 0
let timer: ReturnType<typeof setInterval> | undefined
const message = (e: unknown) => (e instanceof Error ? e.message : 'Не удалось выполнить запрос')
const date = (v: string | null) => (v ? new Date(v).toLocaleString('ru-RU') : 'Нет данных')
const display = (v: unknown) =>
  v === undefined || v === null ? '—' : typeof v === 'boolean' ? (v ? 'Да' : 'Нет') : String(v)
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
    selectedSignal.value = result.signals[0]?.external_signal_id || ''
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
  const raw = drafts[signal.id]?.trim()
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
    <Button variant="outline" as-child>
      <NuxtLink :to="{ path: '/devices', query: route.query }">К списку устройств</NuxtLink>
    </Button>
    <p v-if="auth.user?.role !== 'admin'">Доступ предоставляется только администратору.</p>
    <div v-if="loading" role="status" class="space-y-2 py-4">
      <span class="sr-only">Загрузка…</span>
      <Skeleton class="h-5 w-48" />
      <Skeleton class="h-16 w-full" />
    </div>
    <Alert v-if="error" variant="destructive">
      <AlertDescription>{{ error }}</AlertDescription>
    </Alert>
    <template v-if="device">
      <DeviceDefinitionEditor :key="device.id" :device="device" @saved="device = $event" />
      <Card>
        <CardHeader>
          <CardTitle>{{ device.name }}</CardTitle>
        </CardHeader>
        <CardContent class="space-y-2">
          <p>{{ device.device_type }} · {{ device.external_id }}</p>
          <p>
            Статус: {{ state?.status || device.status }} · Качество данных:
            {{ state?.quality || 'unknown' }}
          </p>
          <p>Последняя связь: {{ date(state?.last_seen_at || device.last_seen_at) }}</p>
          <p>Показания получены: {{ date(state?.state_received_at || null) }}</p>
          <p class="text-sm text-muted-foreground">
            Показания обновляются каждые 10 секунд. При ошибке показано последнее полученное
            состояние.
          </p>
          <Alert v-if="stateError" variant="destructive">
            <AlertDescription>{{ stateError }}</AlertDescription>
          </Alert>
          <Button variant="outline" @click="refreshState">Обновить показания</Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Показания и управление</CardTitle></CardHeader>
        <CardContent>
          <Empty v-if="!device.signals.length">
            <EmptyHeader>
              <EmptyDescription>Сигналы не зарегистрированы</EmptyDescription>
            </EmptyHeader>
          </Empty>
          <div v-for="signal in device.signals" :key="signal.id" class="border-b py-4 space-y-2">
            <p class="font-medium">
              {{ signal.name }}: {{ display(state?.signals[signal.external_signal_id]) }}
              {{ signal.unit }}
            </p>
            <p class="text-xs text-muted-foreground">
              {{ signal.external_signal_id }} · {{ signal.min_value ?? '—' }} …
              {{ signal.max_value ?? '—' }}
            </p>
            <form
              v-if="signal.is_writable"
              class="flex flex-wrap gap-2"
              @submit.prevent="command(signal)"
            >
              <label :for="'command-' + signal.id" class="sr-only">
                Новое значение: {{ signal.name }}
              </label>
              <Input
                :id="'command-' + signal.id"
                v-model="drafts[signal.id]"
                class="max-w-64"
                placeholder="Новое значение"
                required
                :disabled="sending || !device.is_active"
              />
              <Button type="submit" :disabled="sending || !device.is_active">
                {{ sending ? 'Ожидание подтверждения…' : 'Отправить' }}
              </Button>
            </form>
            <p v-else class="text-xs text-muted-foreground">Только чтение</p>
          </div>
          <Alert v-if="commandMessage" role="status">
            <AlertDescription>{{ commandMessage }}</AlertDescription>
          </Alert>
          <Alert v-if="commandError" variant="destructive">
            <AlertDescription>{{ commandError }}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>История числовых показаний</CardTitle></CardHeader>
        <CardContent class="space-y-4">
          <form class="flex flex-wrap gap-2" @submit.prevent="loadHistory">
            <label for="history-signal" class="sr-only">Сигнал для истории</label>
            <Select
              v-model="selectedSignal"
              name="selectedSignal"
              @update:model-value="loadHistory"
            >
              <SelectTrigger id="history-signal" class="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="signal in device.signals"
                  :key="signal.id"
                  :value="signal.external_signal_id"
                >
                  {{ signal.name }}
                </SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" type="submit" :disabled="historyLoading || !selectedSignal">
              Обновить историю
            </Button>
          </form>
          <div v-if="historyLoading" role="status" class="space-y-2 py-4">
            <span class="sr-only">Загрузка истории…</span>
            <Skeleton class="h-5 w-48" />
            <Skeleton class="h-16 w-full" />
          </div>
          <Alert v-else-if="historyError" variant="destructive">
            <AlertDescription>{{ historyError }}</AlertDescription>
          </Alert>
          <Empty v-else-if="!history.length">
            <EmptyHeader>
              <EmptyDescription>
                Записей пока нет. Сохраняются числовые и логические показания.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
          <div v-else class="max-h-96 overflow-auto">
            <Table class="w-full text-left text-sm">
              <TableHeader>
                <TableRow>
                  <TableHead>Время</TableHead>
                  <TableHead>Значение</TableHead>
                  <TableHead>Качество</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="(point, index) in history" :key="index" class="border-b">
                  <TableCell class="py-2">{{ date(point.time) }}</TableCell>
                  <TableCell>{{ point.value }} {{ point.unit }}</TableCell>
                  <TableCell>{{ point.quality }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
