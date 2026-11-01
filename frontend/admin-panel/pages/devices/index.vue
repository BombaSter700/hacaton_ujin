<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getDevices, getDeviceObjects } from '~/utils/api/integration'
import type { Device, DeviceObject } from '~/types/integration'
import { useAuthStore } from '~/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableEmpty,
} from '@/components/ui/table'

const auth = useAuthStore()
const route = useRoute()
const objectId = ref(typeof route.query.object_id === 'string' ? route.query.object_id : '')
const roomId = ref(typeof route.query.room_id === 'string' ? route.query.room_id : '')
const devices = ref<Device[]>([])
const pending = ref(false)
const loaded = ref(false)
const error = ref('')
const objects = ref<DeviceObject[]>([])
const discovering = ref(false)
const statusNames = {
  unknown: 'Нет данных',
  online: 'В сети',
  offline: 'Нет связи',
  error: 'Ошибка',
}
async function load() {
  if (pending.value || !objectId.value.trim()) return
  pending.value = true
  error.value = ''
  loaded.value = false
  devices.value = []
  try {
    await navigateTo(
      {
        path: '/devices',
        query: {
          object_id: objectId.value.trim(),
          ...(roomId.value.trim() ? { room_id: roomId.value.trim() } : {}),
        },
      },
      { replace: true },
    )
    devices.value = await getDevices(objectId.value.trim(), roomId.value.trim() || undefined)
    loaded.value = true
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить устройства'
  } finally {
    pending.value = false
  }
}
onMounted(async () => {
  if (auth.user?.role !== 'admin') return
  discovering.value = true
  try {
    objects.value = await getDeviceObjects()
    if (!objectId.value && objects.value.length === 1) objectId.value = objects.value[0]!.object_id
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить объекты'
  } finally {
    discovering.value = false
  }
  if (objectId.value) await load()
})
</script>
<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Устройства</h1>
    <Card>
      <CardHeader>
        <CardTitle>Реестр устройств</CardTitle>
        <CardDescription>
          Выберите объект и откройте устройство для просмотра показаний, истории и управления.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p v-if="auth.user?.role !== 'admin'">Доступ пока предоставляется только администратору.</p>
        <template v-else>
          <div v-if="discovering" role="status" class="space-y-2 py-4">
            <span class="sr-only">Загрузка объектов…</span>
            <Skeleton class="h-5 w-48" />
            <Skeleton class="h-16 w-full" />
          </div>
          <div v-if="objects.length" class="mb-4 space-y-2">
            <Label for="device-object">Объект с зарегистрированными устройствами</Label>
            <Select
              v-model="objectId"
              :disabled="pending"
              name="objectId"
              @update:model-value="
                ($event) => {
                  roomId = ''
                  load()
                }
              "
            >
              <SelectTrigger id="device-object" class="w-full">
                <SelectValue placeholder="Выберите объект" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="item in objects" :key="item.object_id" :value="item.object_id">
                  {{ item.object_id }} · устройств: {{ item.devices_count }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <form class="mb-6 flex flex-wrap items-end gap-3" @submit.prevent="load">
            <div class="min-w-64 flex-1 space-y-2">
              <Label for="object-id">UUID объекта</Label>
              <Input
                id="object-id"
                v-model="objectId"
                required
                placeholder="Идентификатор объекта из реестра"
              />
            </div>
            <div class="min-w-64 flex-1 space-y-2">
              <Label for="room-id">UUID помещения (необязательно)</Label>
              <Input id="room-id" v-model="roomId" />
            </div>
            <Button type="submit" :disabled="pending">
              {{ pending ? 'Загрузка…' : 'Загрузить' }}
            </Button>
          </form>
          <Alert v-if="error" variant="destructive">
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
          <Empty v-if="!loaded && !pending && !discovering && !error">
            <EmptyHeader>
              <EmptyDescription>
                {{
                  objects.length
                    ? 'Выберите объект из списка или укажите его UUID.'
                    : 'Устройств пока нет. Сначала импортируйте эмуляторы в разделе «Подключения».'
                }}
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
          <div v-if="loaded" class="overflow-x-auto rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Устройство</TableHead>
                  <TableHead>Тип</TableHead>
                  <TableHead>Доступность</TableHead>
                  <TableHead>Последняя связь</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="device in devices" :key="device.id">
                  <TableCell>
                    <p class="font-medium">{{ device.name }}</p>
                    <p class="text-xs text-muted-foreground">{{ device.external_id }}</p>
                  </TableCell>
                  <TableCell>{{ device.device_type }}</TableCell>
                  <TableCell>
                    <Badge :variant="device.status === 'error' ? 'destructive' : 'outline'">
                      {{ statusNames[device.status] || device.status }}
                    </Badge>
                  </TableCell>
                  <TableCell>{{ device.last_seen_at || 'Нет данных' }}</TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm" as-child>
                      <NuxtLink
                        :to="{
                          path: '/devices/' + device.id,
                          query: { object_id: objectId, ...(roomId ? { room_id: roomId } : {}) },
                        }"
                      >
                        Подробнее
                      </NuxtLink>
                    </Button>
                  </TableCell>
                </TableRow>
                <TableEmpty v-if="!devices.length" :colspan="5">
                  <Empty>
                    <EmptyHeader>
                      <EmptyDescription>Устройства не зарегистрированы</EmptyDescription>
                    </EmptyHeader>
                  </Empty>
                </TableEmpty>
              </TableBody>
            </Table>
          </div>
        </template>
      </CardContent>
    </Card>
  </div>
</template>
