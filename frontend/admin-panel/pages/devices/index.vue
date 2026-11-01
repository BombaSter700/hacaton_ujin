<script setup lang="ts">
import { useWorkspaceStore } from '~/stores/workspace'
import { useAuthStore } from '~/stores/auth'
import { deviceName, deviceTypeLabel, primaryReading } from '~/utils/device-labels'
import { formatDateTime, formatDeviceStatus } from '~/utils/format'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
const workspace = useWorkspaceStore()
const auth = useAuthStore()
const route = useRoute()
const query = ref('')
const filtered = computed(() =>
  workspace.devices.filter((device) =>
    (deviceName(device) + ' ' + deviceTypeLabel(device.device_type))
      .toLocaleLowerCase('ru-RU')
      .includes(query.value.trim().toLocaleLowerCase('ru-RU')),
  ),
)
onMounted(() => {
  if (auth.user?.role === 'admin')
    void workspace.refresh(typeof route.query.object_id === 'string' ? route.query.object_id : '')
})
</script>
<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">Устройства</h1>
      <p class="text-muted-foreground">
        Выберите устройство, посмотрите показания и отправьте команду.
      </p>
    </div>
    <p v-if="auth.user?.role !== 'admin'">Доступ предоставляется администратору.</p>
    <template v-else>
      <div class="flex flex-wrap items-end gap-3">
        <WorkspacePicker />
        <div class="flex-1 sm:min-w-64">
          <label for="device-search" class="sr-only">Поиск устройств</label>
          <Input id="device-search" v-model="query" placeholder="Найти лифт, датчик, термостат…" />
        </div>
        <Button
          variant="outline"
          :disabled="workspace.loading || workspace.preparing"
          @click="workspace.refresh()"
        >
          Обновить
        </Button>
      </div>
      <Alert v-if="workspace.error" variant="destructive">
        <AlertDescription>{{ workspace.error }}</AlertDescription>
      </Alert>
      <div v-if="workspace.loading" class="grid gap-4 md:grid-cols-3" role="status">
        <span class="sr-only">Загрузка устройств</span>
        <Skeleton v-for="n in 3" :key="n" class="h-48 w-full" />
      </div>
      <DemoSetup v-else-if="!workspace.objects.length" />
      <Empty v-else-if="!filtered.length">
        <EmptyHeader>
          <EmptyDescription>
            {{
              query
                ? 'По запросу ничего не найдено. Попробуйте другое название.'
                : 'Устройства пока не подключены.'
            }}
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
      <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <Card v-for="device in filtered" :key="device.id" class="flex flex-col">
          <CardHeader>
            <div class="flex items-start justify-between gap-3">
              <CardTitle>{{ deviceName(device) }}</CardTitle>
              <Badge :variant="device.status === 'error' ? 'destructive' : 'outline'">
                {{ formatDeviceStatus(device.status) }}
              </Badge>
            </div>
            <CardDescription>{{ deviceTypeLabel(device.device_type) }}</CardDescription>
          </CardHeader>
          <CardContent class="flex-1 space-y-3">
            <p class="text-lg font-medium">
              {{ primaryReading(device, workspace.states[device.id]) }}
            </p>
            <p class="text-sm text-muted-foreground">
              Последняя связь: {{ formatDateTime(device.last_seen_at) }}
            </p>
            <p class="text-sm">Доступно показателей: {{ device.signals.length }}</p>
            <Collapsible>
              <CollapsibleTrigger class="text-xs text-muted-foreground underline">
                Технические сведения
              </CollapsibleTrigger>
              <CollapsibleContent class="break-all pt-2 text-xs text-muted-foreground">
                UUID: {{ device.id }}
                <br />
                Внешний код: {{ device.external_id }}
              </CollapsibleContent>
            </Collapsible>
          </CardContent>
          <CardFooter>
            <Button as-child class="w-full">
              <NuxtLink :to="'/devices/' + device.id">Показания и управление</NuxtLink>
            </Button>
          </CardFooter>
        </Card>
      </div>
    </template>
  </div>
</template>
