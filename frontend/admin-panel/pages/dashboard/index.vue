<script setup lang="ts">
import { useWorkspaceStore } from '~/stores/workspace'
import { useAuthStore } from '~/stores/auth'
import { deviceName, deviceTypeLabel, primaryReading } from '~/utils/device-labels'
import { formatDeviceStatus } from '~/utils/format'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ArrowRight, RefreshCw } from 'lucide-vue-next'
import SmartIcon from '~/components/SmartIcon.vue'
import DashboardDemoCharts from '~/components/DashboardDemoCharts.vue'

const workspace = useWorkspaceStore()
const auth = useAuthStore()
onMounted(() => {
  if (auth.user?.role === 'admin') void workspace.refresh()
})

type IconName = 'climate' | 'smart-lock' | 'energy' | 'sensors' | 'telemetry'
const deviceIcon = (type: string): IconName => {
  const icons: Record<string, IconName> = {
    thermostat: 'climate',
    ventilation: 'climate',
    light: 'energy',
    counter: 'energy',
    barrier: 'smart-lock',
    elevator: 'telemetry',
    leak: 'sensors',
    fire: 'sensors',
    hub: 'sensors',
  }
  return icons[type.replace(/^emul_/, '')] || 'sensors'
}
const links = [
  {
    to: '/devices',
    title: 'Устройства',
    description: 'Показания и управление',
    icon: 'telemetry' as const,
  },
  {
    to: '/scenarios',
    title: 'Сценарии',
    description: 'Правила и готовые шаблоны',
    icon: 'automation' as const,
  },
  {
    to: '/objects',
    title: 'Объекты',
    description: 'Дома и подключения',
    icon: 'smart-home' as const,
  },
]
</script>
<template>
  <div class="space-y-5">
    <div class="flex items-center gap-3">
      <SmartIcon name="smart-home" :size="52" />
      <div>
        <h1 class="text-2xl font-bold">Обзор дома</h1>
        <p class="text-sm text-muted-foreground">
          Показания, устройства и управление в одном месте.
        </p>
      </div>
    </div>
    <p v-if="auth.user?.role !== 'admin'">Доступ к устройствам предоставляется администратору.</p>
    <template v-else>
      <div class="flex flex-wrap items-end justify-between gap-4 rounded-xl border bg-card p-4">
        <WorkspacePicker />
        <div class="flex flex-wrap items-center gap-2">
          <Badge variant="outline">Устройств: {{ workspace.devices.length }}</Badge>
          <Badge variant="outline">В сети: {{ workspace.online }}</Badge>
          <Badge v-if="workspace.attention" variant="destructive">
            Требуют внимания: {{ workspace.attention }}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            :disabled="workspace.loading || workspace.preparing"
            @click="workspace.refresh()"
          >
            <RefreshCw class="mr-1 size-4" :class="{ 'animate-spin': workspace.loading }" />
            Обновить
          </Button>
        </div>
      </div>
      <Alert v-if="workspace.error" variant="destructive">
        <AlertDescription>{{ workspace.error }}</AlertDescription>
      </Alert>
      <DemoSetup v-if="!workspace.loading && !workspace.objects.length" />
      <div class="grid grid-cols-1 items-start gap-5 xl:grid-cols-12">
        <DashboardDemoCharts />
        <Card class="min-w-0 xl:col-span-8">
          <CardHeader class="flex flex-row items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <SmartIcon name="telemetry" :size="44" />
              <div>
                <CardTitle>Устройства дома</CardTitle>
                <CardDescription class="mt-1">Данные подключённых устройств</CardDescription>
              </div>
            </div>
            <Button variant="ghost" size="sm" as-child>
              <NuxtLink to="/devices">
                Все
                <ArrowRight class="ml-1 size-4" />
              </NuxtLink>
            </Button>
          </CardHeader>
          <CardContent>
            <div v-if="workspace.loading" class="space-y-3" role="status">
              <span class="sr-only">Загрузка устройств</span>
              <Skeleton v-for="index in 3" :key="index" class="h-14 w-full" />
            </div>
            <p
              v-else-if="!workspace.devices.length"
              class="py-6 text-center text-sm text-muted-foreground"
            >
              Подготовьте демонстрацию, чтобы здесь появились устройства и их показания.
            </p>
            <div v-else class="grid divide-y sm:grid-cols-2 sm:gap-x-6">
              <NuxtLink
                v-for="device in workspace.devices"
                :key="device.id"
                :to="'/devices/' + device.id"
                class="group flex min-w-0 items-center gap-3 rounded-md py-3 transition-colors hover:bg-muted/50 focus-visible:outline-2 focus-visible:outline-ring"
              >
                <SmartIcon :name="deviceIcon(device.device_type)" :size="40" />
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="font-medium">{{ deviceName(device) }}</p>
                    <Badge
                      :variant="device.status === 'error' ? 'destructive' : 'outline'"
                      class="text-[10px]"
                    >
                      {{ formatDeviceStatus(device.status) }}
                    </Badge>
                  </div>
                  <p
                    class="mt-1 truncate text-xs text-muted-foreground"
                    :title="primaryReading(device, workspace.states[device.id])"
                  >
                    {{
                      workspace.states[device.id]
                        ? primaryReading(device, workspace.states[device.id])
                        : deviceTypeLabel(device.device_type)
                    }}
                  </p>
                </div>
                <ArrowRight
                  class="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5"
                />
              </NuxtLink>
            </div>
          </CardContent>
        </Card>
        <Card class="min-w-0 xl:col-span-4">
          <CardHeader>
            <CardTitle>Быстрый переход</CardTitle>
            <CardDescription>Основные разделы панели</CardDescription>
          </CardHeader>
          <CardContent class="space-y-2">
            <Button
              v-for="link in links"
              :key="link.to"
              variant="ghost"
              as-child
              class="h-auto w-full justify-start gap-3 px-2 py-3 text-left"
            >
              <NuxtLink :to="link.to">
                <SmartIcon :name="link.icon" :size="40" />
                <span class="flex-1">
                  <span class="block font-medium">{{ link.title }}</span>
                  <span class="mt-0.5 block text-xs font-normal text-muted-foreground">
                    {{ link.description }}
                  </span>
                </span>
                <ArrowRight class="size-4 text-muted-foreground" />
              </NuxtLink>
            </Button>
            <Button variant="outline" class="mt-3 w-full" as-child>
              <NuxtLink to="/integrations">Настроить подключения</NuxtLink>
            </Button>
          </CardContent>
        </Card>
      </div>
    </template>
  </div>
</template>
