<script setup lang="ts">
import { deviceName, signalName } from '~/utils/device-labels'
import { sanitizeName } from '~/utils/sanitize'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import type { Device, Signal } from '~/types/integration'
import { saveDeviceDefinition } from '~/utils/api/integration'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
const props = defineProps<{ device: Device }>()
const emit = defineEmits<{ saved: [device: Device] }>()
type Draft = {
  id: string
  name: string
  value_type: Signal['value_type']
  unit: string
  is_writable: boolean
  source_is_writable: boolean
  min: string
  max: string
}
const open = ref(false)
const name = ref('')
const signals = ref<Draft[]>([])
const pending = ref(false)
const error = ref('')
const success = ref('')
function edit() {
  name.value = deviceName(props.device)
  signals.value = props.device.signals.map((s) => ({
    id: s.id,
    name: signalName(s),
    value_type: s.value_type,
    unit: s.unit || '',
    is_writable: s.is_writable,
    source_is_writable: s.source_is_writable,
    min: s.min_value === null ? '' : String(s.min_value),
    max: s.max_value === null ? '' : String(s.max_value),
  }))
  error.value = ''
  success.value = ''
  open.value = true
}
function range(value: string | number) {
  if (!String(value).trim()) return null
  const result = Number(value)
  if (!Number.isFinite(result)) throw new Error('Границы диапазона должны быть числами')
  return result
}
async function save() {
  if (pending.value) return
  pending.value = true
  error.value = ''
  try {
    const result = await saveDeviceDefinition(props.device.id, {
      name: sanitizeName(name.value),
      signals: signals.value.map((s) => ({
        id: s.id,
        name: sanitizeName(s.name),
        value_type: s.value_type,
        unit: s.unit.trim() || null,
        is_writable: s.is_writable,
        min_value: s.value_type === 'number' ? range(s.min) : null,
        max_value: s.value_type === 'number' ? range(s.max) : null,
      })),
    })
    emit('saved', result)
    open.value = false
    success.value = 'Описание сохранено'
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось сохранить описание'
  } finally {
    pending.value = false
  }
}
</script>
<template>
  <section class="rounded-lg border p-4 space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h2 class="font-semibold">Конструктор описания устройства</h2>
      <Button v-if="!open" variant="outline" @click="edit">Настроить описание</Button>
    </div>
    <Alert v-if="success" role="status">
      <AlertDescription>{{ success }}</AlertDescription>
    </Alert>
    <form v-if="open" class="space-y-5" @submit.prevent="save">
      <p class="text-sm text-muted-foreground">
        Настройте существующие сигналы. Названия и параметры сохраняются при повторном импорте.
        Команду можно разрешить только для сигнала, который поддерживает запись.
      </p>
      <div class="space-y-2">
        <label for="definition-name">Название устройства</label>
        <Input id="definition-name" v-model="name" required maxlength="120" :disabled="pending" />
      </div>
      <fieldset
        v-for="(signal, index) in signals"
        :key="signal.id"
        class="rounded border p-4 space-y-3"
        :disabled="pending"
      >
        <legend class="px-2 text-sm">Сигнал {{ index + 1 }}</legend>
        <div class="grid gap-3 md:grid-cols-3">
          <label class="space-y-1">
            <span class="text-sm">Название</span>
            <Input v-model="signal.name" required maxlength="120" />
          </label>
          <label class="space-y-1">
            <span class="text-sm">Тип значения</span>
            <Select v-model="signal.value_type" name="signal.value_type" :disabled="pending">
              <SelectTrigger class="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="number">Число</SelectItem>
                <SelectItem value="boolean">Да / нет</SelectItem>
                <SelectItem value="string">Текст</SelectItem>
              </SelectContent>
            </Select>
          </label>
          <label class="space-y-1">
            <span class="text-sm">Единица измерения</span>
            <Input v-model="signal.unit" maxlength="30" placeholder="°C, %, ppm" />
          </label>
          <template v-if="signal.value_type === 'number'">
            <label class="space-y-1">
              <span class="text-sm">Минимум для команды</span>
              <Input v-model="signal.min" type="number" step="any" placeholder="Без ограничения" />
            </label>
            <label class="space-y-1">
              <span class="text-sm">Максимум для команды</span>
              <Input v-model="signal.max" type="number" step="any" placeholder="Без ограничения" />
            </label>
          </template>
        </div>
        <label class="flex items-center gap-2 text-sm">
          <Checkbox
            v-model="signal.is_writable"
            :disabled="pending || !signal.source_is_writable"
          />
          Разрешить команды
        </label>
        <p v-if="!signal.source_is_writable" class="text-xs text-muted-foreground">
          Устройство предоставляет этот сигнал только для чтения.
        </p>
      </fieldset>
      <Alert v-if="error" variant="destructive">
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>
      <div class="flex gap-2">
        <Button type="submit" :disabled="pending">
          {{ pending ? 'Сохранение…' : 'Сохранить описание' }}
        </Button>
        <Button type="button" variant="outline" :disabled="pending" @click="open = false">
          Отмена
        </Button>
      </div>
    </form>
  </section>
</template>
