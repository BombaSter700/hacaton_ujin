<script setup lang="ts">
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { buttonVariants } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
definePageMeta({ path: '/scenarios', name: 'scenarios' })
import { useAuthStore } from '~/stores/auth'
import { getDeviceObjects, getDevices } from '~/utils/api/integration'
import {
  getScenarios,
  getScenario,
  createScenario,
  updateScenario,
  toggleScenario,
  deleteScenario,
} from '~/utils/api/scenarios'
import { parseSignalValue } from '~/utils/signal-values'
import type { Device, DeviceObject } from '~/types/integration'
import type { Scenario, ScenarioInput, Operator } from '~/types/scenario'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
const auth = useAuthStore()
const route = useRoute()
const objects = ref<DeviceObject[]>([])
const objectId = ref(typeof route.query.object_id === 'string' ? route.query.object_id : '')
const devices = ref<Device[]>([])
const items = ref<Scenario[]>([])
const total = ref(0)
const skip = ref(0)
const pending = ref(false)
const saving = ref(false)
const error = ref('')
const formError = ref('')
const notice = ref('')
const editorOpen = ref(false)
const editing = ref<Scenario | null>(null)
const deletingId = ref('')
const name = ref('')
const description = ref('')
const enabled = ref(false)
const matchMode = ref<'all' | 'any'>('all')
type ConditionDraft = {
  key: number
  kind: 'signal' | 'time'
  device_id: string
  signal_id: string
  operator: Operator
  value: string
  start_time: string
  end_time: string
  timezone: string
}
type ActionDraft = { key: number; device_id: string; signal_id: string; value: string }
const conditions = ref<ConditionDraft[]>([])
const actions = ref<ActionDraft[]>([])
let nextKey = 0
let generation = 0
const message = (cause: unknown) =>
  cause instanceof Error ? cause.message : 'Не удалось выполнить запрос'
const signalFor = (deviceId: string, signalId: string) =>
  devices.value.find((d) => d.id === deviceId)?.signals.find((s) => s.id === signalId)
const signalsFor = (deviceId: string, writable = false) =>
  devices.value.find((d) => d.id === deviceId)?.signals.filter((s) => !writable || s.is_writable) ||
  []
const actionDevices = computed(() =>
  devices.value.filter((d) => d.signals.some((s) => s.is_writable)),
)
const operators = [
  { value: 'eq', label: 'Равно' },
  { value: 'ne', label: 'Не равно' },
  { value: 'gt', label: 'Больше' },
  { value: 'gte', label: 'Больше или равно' },
  { value: 'lt', label: 'Меньше' },
  { value: 'lte', label: 'Меньше или равно' },
]
function conditionDraft(): ConditionDraft {
  return {
    key: nextKey++,
    kind: 'signal',
    device_id: '',
    signal_id: '',
    operator: 'eq',
    value: '',
    start_time: '08:00',
    end_time: '22:00',
    timezone: 'Europe/Moscow',
  }
}
function actionDraft(): ActionDraft {
  return { key: nextKey++, device_id: '', signal_id: '', value: '' }
}
async function load() {
  if (!objectId.value) return
  const version = ++generation
  pending.value = true
  error.value = ''
  deletingId.value = ''
  try {
    const [catalogue, page] = await Promise.all([
      getDevices(objectId.value),
      getScenarios(objectId.value, skip.value),
    ])
    if (version !== generation) return
    devices.value = catalogue
    items.value = page.items
    total.value = page.total
    await navigateTo(
      { path: '/scenarios', query: { object_id: objectId.value } },
      { replace: true },
    )
  } catch (cause) {
    if (version === generation) error.value = message(cause)
  } finally {
    if (version === generation) pending.value = false
  }
}
function newScenario() {
  editing.value = null
  name.value = ''
  description.value = ''
  enabled.value = false
  matchMode.value = 'all'
  conditions.value = [conditionDraft()]
  actions.value = [actionDraft()]
  formError.value = ''
  notice.value = ''
  editorOpen.value = true
}
async function editScenario(item: Scenario) {
  pending.value = true
  error.value = ''
  try {
    const fresh = await getScenario(item.id)
    editing.value = fresh
    name.value = fresh.name
    description.value = fresh.description
    enabled.value = fresh.enabled
    matchMode.value = fresh.match_mode
    conditions.value = fresh.conditions.map((c) =>
      c.kind === 'time'
        ? {
            ...conditionDraft(),
            kind: 'time',
            start_time: c.start_time,
            end_time: c.end_time,
            timezone: c.timezone,
          }
        : {
            ...conditionDraft(),
            device_id: c.device_id,
            signal_id: c.signal_id,
            operator: c.operator,
            value: String(c.value),
          },
    )
    actions.value = fresh.actions.map((a) => ({
      ...actionDraft(),
      device_id: a.device_id,
      signal_id: a.signal_id,
      value: String(a.value),
    }))
    formError.value = ''
    notice.value = ''
    editorOpen.value = true
  } catch (cause) {
    error.value = message(cause)
  } finally {
    pending.value = false
  }
}
function valueFor(row: ActionDraft | ConditionDraft, checkRange: boolean) {
  const signal = signalFor(row.device_id, row.signal_id)
  if (!signal) throw new Error('Выберите устройство и сигнал')
  return parseSignalValue(signal, row.value, checkRange)
}
async function save() {
  if (saving.value) return
  saving.value = true
  formError.value = ''
  try {
    const payload: ScenarioInput = {
      object_id: objectId.value,
      name: name.value.trim(),
      description: description.value.trim(),
      enabled: enabled.value,
      match_mode: matchMode.value,
      conditions: conditions.value.map((c) =>
        c.kind === 'time'
          ? { kind: 'time', start_time: c.start_time, end_time: c.end_time, timezone: c.timezone }
          : {
              kind: 'signal',
              device_id: c.device_id,
              signal_id: c.signal_id,
              operator: c.operator,
              value: valueFor(c, false),
            },
      ),
      actions: actions.value.map((a) => ({
        device_id: a.device_id,
        signal_id: a.signal_id,
        value: valueFor(a, true),
      })),
    }
    if (editing.value) await updateScenario(editing.value.id, payload, editing.value.revision)
    else await createScenario(payload)
    editorOpen.value = false
    skip.value = 0
    notice.value =
      'Сценарий сохранён. Автоматическое выполнение будет подключено на следующем этапе.'
    await load()
  } catch (cause) {
    formError.value = message(cause)
  } finally {
    saving.value = false
  }
}
async function toggle(item: Scenario) {
  saving.value = true
  error.value = ''
  try {
    await toggleScenario(item)
    await load()
  } catch (cause) {
    error.value = message(cause)
  } finally {
    saving.value = false
  }
}
async function remove(item: Scenario) {
  saving.value = true
  error.value = ''
  try {
    await deleteScenario(item)
    deletingId.value = ''
    skip.value = 0
    await load()
  } catch (cause) {
    error.value = message(cause)
  } finally {
    saving.value = false
  }
}
async function page(delta: number) {
  skip.value = Math.max(0, skip.value + delta)
  await load()
}
onMounted(async () => {
  if (auth.user?.role !== 'admin') return
  pending.value = true
  try {
    objects.value = await getDeviceObjects()
    if (!objectId.value && objects.value.length === 1) objectId.value = objects.value[0]!.object_id
    if (objectId.value) await load()
  } catch (cause) {
    error.value = message(cause)
  } finally {
    pending.value = false
  }
})
onBeforeUnmount(() => {
  generation++
})
</script>
<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Сценарии</h1>
    <p v-if="auth.user?.role !== 'admin'">Редактор доступен администратору.</p>
    <template v-else>
      <Alert>
        <AlertDescription>
          Редактор сохраняет правила. Автоматический запуск по показаниям и времени пока не
          подключён. Переключатель «Активен» сохраняет настройку для будущего исполнения.
        </AlertDescription>
      </Alert>
      <label class="block space-y-2">
        <span>Объект</span>
        <Select
          v-model="objectId"
          :disabled="pending || editorOpen || saving"
          name="objectId"
          @update:model-value="
            ($event) => {
              skip = 0
              load()
            }
          "
        >
          <SelectTrigger class="w-full">
            <SelectValue placeholder="Выберите объект" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="item in objects" :key="item.object_id" :value="item.object_id">
              {{ item.object_id }} · устройств: {{ item.devices_count }}
            </SelectItem>
          </SelectContent>
        </Select>
      </label>
      <Empty v-if="!pending && !objects.length">
        <EmptyHeader>
          <EmptyDescription>
            Сначала подключите устройства в разделе «Подключения».
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
      <div v-if="pending" role="status" class="space-y-2 py-4">
        <span class="sr-only">Загрузка…</span>
        <Skeleton class="h-5 w-48" />
        <Skeleton class="h-16 w-full" />
      </div>
      <Alert v-if="error" variant="destructive">
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>
      <Alert v-if="notice" role="status">
        <AlertDescription>{{ notice }}</AlertDescription>
      </Alert>
      <Button
        v-if="objectId && !editorOpen"
        :disabled="pending || saving || !devices.length"
        @click="newScenario"
      >
        Создать сценарий
      </Button>
      <Card v-if="editorOpen">
        <CardHeader>
          <CardTitle>{{ editing ? 'Редактирование сценария' : 'Новый сценарий' }}</CardTitle>
        </CardHeader>
        <CardContent>
          <form class="space-y-6" @submit.prevent="save">
            <fieldset class="space-y-5" :disabled="saving">
              <label class="block space-y-1">
                <span>Название</span>
                <Input v-model="name" required maxlength="120" placeholder="Дневной микроклимат" />
              </label>
              <label class="block space-y-1">
                <span>Описание</span>
                <Textarea v-model="description" maxlength="2000" rows="2" />
              </label>
              <label class="flex gap-2 items-center">
                <Switch v-model="enabled" :disabled="saving" />
                Активен (настройка, без автоматического запуска)
              </label>
              <div class="flex flex-wrap items-center gap-3">
                <h2 class="font-semibold">Если</h2>
                <Select v-model="matchMode" name="matchMode" :disabled="saving">
                  <SelectTrigger class="w-full"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Выполнены все условия</SelectItem>
                    <SelectItem value="any">Выполнено хотя бы одно условие</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <fieldset
                v-for="(condition, index) in conditions"
                :key="condition.key"
                class="rounded border p-4 space-y-3"
              >
                <legend class="px-2">Условие {{ index + 1 }}</legend>
                <label class="block space-y-1">
                  <span class="text-sm">Тип условия</span>
                  <Select
                    v-model="condition.kind"
                    :name="'condition-' + condition.key + '-kind'"
                    :disabled="saving"
                  >
                    <SelectTrigger class="w-full"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="signal">Показание устройства</SelectItem>
                      <SelectItem value="time">Время суток</SelectItem>
                    </SelectContent>
                  </Select>
                </label>
                <template v-if="condition.kind === 'signal'">
                  <div class="grid gap-3 md:grid-cols-2">
                    <label class="space-y-1">
                      <span class="text-sm">Устройство</span>
                      <Select
                        :model-value="condition.device_id || null"
                        required
                        :name="'condition-' + condition.key + '-device_id'"
                        :disabled="saving"
                        @update:model-value="
                          ($event) => {
                            condition.device_id = String($event ?? '')
                            condition.signal_id = ''
                            condition.value = ''
                          }
                        "
                      >
                        <SelectTrigger class="w-full">
                          <SelectValue placeholder="Выберите устройство" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem v-for="device in devices" :key="device.id" :value="device.id">
                            {{ device.name }}
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </label>
                    <label class="space-y-1">
                      <span class="text-sm">Сигнал</span>
                      <Select
                        :model-value="condition.signal_id || null"
                        required
                        :name="'condition-' + condition.key + '-signal_id'"
                        :disabled="saving"
                        @update:model-value="
                          ($event) => {
                            condition.signal_id = String($event ?? '')
                            condition.operator = 'eq'
                            condition.value = ''
                          }
                        "
                      >
                        <SelectTrigger class="w-full">
                          <SelectValue placeholder="Выберите сигнал" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem
                            v-for="signal in signalsFor(condition.device_id)"
                            :key="signal.id"
                            :value="signal.id"
                          >
                            {{ signal.name }} ({{ signal.unit || signal.value_type }})
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </label>
                    <label class="space-y-1">
                      <span class="text-sm">Сравнение</span>
                      <Select
                        v-model="condition.operator"
                        :name="'condition-' + condition.key + '-operator'"
                        :disabled="saving"
                      >
                        <SelectTrigger class="w-full"><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem
                            v-for="operator in operators.filter(
                              (o) =>
                                signalFor(condition.device_id, condition.signal_id)?.value_type ===
                                  'number' || ['eq', 'ne'].includes(o.value),
                            )"
                            :key="operator.value"
                            :value="operator.value"
                          >
                            {{ operator.label }}
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </label>
                    <label class="space-y-1">
                      <span class="text-sm">Значение</span>
                      <Select
                        v-if="
                          signalFor(condition.device_id, condition.signal_id)?.value_type ===
                          'boolean'
                        "
                        :model-value="condition.value || null"
                        required
                        :name="'condition-' + condition.key + '-value'"
                        :disabled="saving"
                        @update:model-value="condition.value = String($event ?? '')"
                      >
                        <SelectTrigger class="w-full">
                          <SelectValue placeholder="Выберите значение" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="true">Да (true)</SelectItem>
                          <SelectItem value="false">Нет (false)</SelectItem>
                        </SelectContent>
                      </Select>
                      <Input
                        v-else
                        v-model="condition.value"
                        required
                        :type="
                          signalFor(condition.device_id, condition.signal_id)?.value_type ===
                          'number'
                            ? 'number'
                            : 'text'
                        "
                        step="any"
                      />
                    </label>
                  </div>
                </template>
                <template v-else>
                  <div class="grid gap-3 md:grid-cols-3">
                    <label class="space-y-1">
                      <span class="text-sm">Начало</span>
                      <Input v-model="condition.start_time" required type="time" />
                    </label>
                    <label class="space-y-1">
                      <span class="text-sm">Конец</span>
                      <Input v-model="condition.end_time" required type="time" />
                    </label>
                    <label class="space-y-1">
                      <span class="text-sm">Часовой пояс IANA</span>
                      <Input v-model="condition.timezone" required placeholder="Europe/Moscow" />
                    </label>
                  </div>
                  <p class="text-xs text-muted-foreground">
                    Интервал может проходить через полночь. Одинаковые начало и конец означают весь
                    день.
                  </p>
                </template>
                <Button
                  type="button"
                  variant="outline"
                  :disabled="conditions.length === 1"
                  @click="conditions.splice(index, 1)"
                >
                  Убрать условие
                </Button>
              </fieldset>
              <Button
                type="button"
                variant="outline"
                :disabled="conditions.length >= 10"
                @click="conditions.push(conditionDraft())"
              >
                Добавить условие
              </Button>
              <h2 class="font-semibold">Тогда</h2>
              <fieldset
                v-for="(action, index) in actions"
                :key="action.key"
                class="rounded border p-4 space-y-3"
              >
                <legend class="px-2">Действие {{ index + 1 }}</legend>
                <div class="grid gap-3 md:grid-cols-3">
                  <label class="space-y-1">
                    <span class="text-sm">Устройство</span>
                    <Select
                      :model-value="action.device_id || null"
                      required
                      :name="'action-' + action.key + '-device_id'"
                      :disabled="saving"
                      @update:model-value="
                        ($event) => {
                          action.device_id = String($event ?? '')
                          action.signal_id = ''
                          action.value = ''
                        }
                      "
                    >
                      <SelectTrigger class="w-full">
                        <SelectValue placeholder="Выберите устройство" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem
                          v-for="device in actionDevices"
                          :key="device.id"
                          :value="device.id"
                        >
                          {{ device.name }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </label>
                  <label class="space-y-1">
                    <span class="text-sm">Команда / сигнал</span>
                    <Select
                      :model-value="action.signal_id || null"
                      required
                      :name="'action-' + action.key + '-signal_id'"
                      :disabled="saving"
                      @update:model-value="
                        ($event) => {
                          action.signal_id = String($event ?? '')
                          action.value = ''
                        }
                      "
                    >
                      <SelectTrigger class="w-full">
                        <SelectValue placeholder="Выберите доступный сигнал" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem
                          v-for="signal in signalsFor(action.device_id, true)"
                          :key="signal.id"
                          :value="signal.id"
                        >
                          {{ signal.name }} ({{ signal.unit || signal.value_type }})
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </label>
                  <label class="space-y-1">
                    <span class="text-sm">Установить значение</span>
                    <Select
                      v-if="signalFor(action.device_id, action.signal_id)?.value_type === 'boolean'"
                      :model-value="action.value || null"
                      required
                      :name="'action-' + action.key + '-value'"
                      :disabled="saving"
                      @update:model-value="action.value = String($event ?? '')"
                    >
                      <SelectTrigger class="w-full">
                        <SelectValue placeholder="Выберите значение" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="true">Да (true)</SelectItem>
                        <SelectItem value="false">Нет (false)</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input
                      v-else
                      v-model="action.value"
                      required
                      :type="
                        signalFor(action.device_id, action.signal_id)?.value_type === 'number'
                          ? 'number'
                          : 'text'
                      "
                      step="any"
                      :min="signalFor(action.device_id, action.signal_id)?.min_value ?? undefined"
                      :max="signalFor(action.device_id, action.signal_id)?.max_value ?? undefined"
                    />
                  </label>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  :disabled="actions.length === 1"
                  @click="actions.splice(index, 1)"
                >
                  Убрать действие
                </Button>
              </fieldset>
              <Button
                type="button"
                variant="outline"
                :disabled="actions.length >= 10"
                @click="actions.push(actionDraft())"
              >
                Добавить действие
              </Button>
            </fieldset>
            <Alert v-if="formError" variant="destructive">
              <AlertDescription>{{ formError }}</AlertDescription>
            </Alert>
            <div class="flex gap-3">
              <Button type="submit" :disabled="saving">
                {{ saving ? 'Сохранение…' : 'Сохранить сценарий' }}
              </Button>
              <Button
                type="button"
                variant="outline"
                :disabled="saving"
                @click="editorOpen = false"
              >
                Отмена
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
      <div v-if="!editorOpen" class="space-y-4">
        <Empty v-if="objectId && !pending && !items.length">
          <EmptyHeader>
            <EmptyDescription>Сохранённых сценариев пока нет.</EmptyDescription>
          </EmptyHeader>
        </Empty>
        <Card v-for="item in items" :key="item.id">
          <CardHeader>
            <CardTitle>{{ item.name }}</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <p>{{ item.description }}</p>
            <p class="text-sm">
              {{ item.enabled ? 'Активен' : 'Выключен' }} · условий: {{ item.conditions.length }} ·
              действий: {{ item.actions.length }} · версия {{ item.revision }}
            </p>
            <div class="flex flex-wrap gap-2">
              <Button variant="outline" :disabled="pending || saving" @click="editScenario(item)">
                Редактировать
              </Button>
              <Button variant="outline" :disabled="pending || saving" @click="toggle(item)">
                {{ item.enabled ? 'Выключить' : 'Включить' }}
              </Button>
              <Button variant="outline" :disabled="pending || saving" @click="deletingId = item.id">
                Удалить
              </Button>
            </div>
            <AlertDialog
              :open="deletingId === item.id"
              @update:open="!$event && !saving && (deletingId = '')"
            >
              <AlertDialogContent @escape-key-down="saving && $event.preventDefault()">
                <AlertDialogHeader>
                  <AlertDialogTitle>Удалить сценарий?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Сценарий «{{ item.name }}» будет удалён. Это действие нельзя отменить.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <Alert v-if="error" variant="destructive">
                  <AlertDescription>{{ error }}</AlertDescription>
                </Alert>
                <AlertDialogFooter>
                  <AlertDialogCancel :disabled="saving">Отмена</AlertDialogCancel>
                  <AlertDialogAction
                    :class="buttonVariants({ variant: 'destructive' })"
                    :disabled="saving"
                    @click.prevent="remove(item)"
                  >
                    {{ saving ? 'Удаление…' : 'Да, удалить' }}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </CardContent>
        </Card>
        <div v-if="total > 50" class="flex gap-3 items-center">
          <Button variant="outline" :disabled="pending || saving || skip === 0" @click="page(-50)">
            Назад
          </Button>
          <span>{{ skip + 1 }}–{{ Math.min(skip + 50, total) }} из {{ total }}</span>
          <Button
            variant="outline"
            :disabled="pending || saving || skip + 50 >= total"
            @click="page(50)"
          >
            Далее
          </Button>
        </div>
      </div>
    </template>
  </div>
</template>
