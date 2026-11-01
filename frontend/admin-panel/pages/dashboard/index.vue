<script setup lang="ts">
import { Activity, ArrowRight, Building2, Cpu } from 'lucide-vue-next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
const stats = [
  {
    name: 'Всего объектов',
    count: 12,
    iconName: 'smart-home',
    detail: 'Объекты под управлением',
  },
  {
    name: 'Устройства в сети',
    count: 84,
    iconName: 'sensors',
    detail: 'Доступны для мониторинга',
  },
  {
    name: 'Требуют внимания',
    count: 3,
    iconName: 'telemetry',
    detail: 'Отключены или есть ошибки',
  },
]
const activity = [
  { name: 'Датчик температуры', object: 'ЖК Северный · Корпус 1', status: 'В сети', ok: true },
  {
    name: 'Контроллер освещения',
    object: 'ЖК Северный · Корпус 2',
    status: 'Нет связи',
    ok: false,
  },
  { name: 'Умное реле', object: 'ЖК Центральный · Корпус 1', status: 'В сети', ok: true },
]
</script>
<template>
  <div class="flex flex-col gap-6">
    <div>
      <div class="mb-2 flex items-center gap-2">
        <h1 class="text-2xl font-bold tracking-tight">Обзор</h1>
        <Badge variant="secondary">Демо-данные</Badge>
      </div>
      <p class="text-sm text-muted-foreground">
        Сводка по объектам и подключённым устройствам управляющей компании.
      </p>
    </div>

    <environment />

    <div class="grid gap-4 md:grid-cols-3">
      <Card v-for="stat in stats" :key="stat.name">
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">{{ stat.name }}</CardTitle>
          <SmartIcon :name="stat.iconName" :size="70" />
        </CardHeader>
        <CardContent>
          <div class="text-3xl font-bold">{{ stat.count }}</div>
          <p class="mt-1 text-xs text-muted-foreground">{{ stat.detail }}</p>
        </CardContent>
      </Card>
    </div>
    <div class="grid gap-4 xl:grid-cols-3">
      <Card class="xl:col-span-2">
        <CardHeader class="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Состояние устройств</CardTitle>
            <CardDescription>
              Примеры последних состояний для демонстрации интерфейса
            </CardDescription>
          </div>
          <Activity class="size-5 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="divide-y">
            <div
              v-for="item in activity"
              :key="item.name"
              class="flex items-center justify-between gap-3 py-3"
            >
              <div class="flex items-center gap-3">
                <span class="rounded-lg bg-muted p-2"><Cpu class="size-4" /></span>
                <div>
                  <p class="text-sm font-medium">{{ item.name }}</p>
                  <p class="text-xs text-muted-foreground">{{ item.object }}</p>
                </div>
              </div>
              <Badge :variant="item.ok ? 'secondary' : 'destructive'">{{ item.status }}</Badge>
            </div>
          </div>
          <Button variant="outline" class="mt-4" as-child>
            <NuxtLink to="/devices">
              Все устройства
              <ArrowRight class="ml-2 size-4" />
            </NuxtLink>
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Быстрые действия</CardTitle>
          <CardDescription>Переходы к основным разделам</CardDescription>
        </CardHeader>
        <CardContent class="grid gap-3">
          <Button variant="outline" as-child class="justify-start">
            <NuxtLink to="/objects">
              <Building2 class="mr-2 size-4" />
              Просмотреть объекты
            </NuxtLink>
          </Button>
          <Button variant="outline" as-child class="justify-start">
            <NuxtLink to="/devices">
              <Cpu class="mr-2 size-4" />
              Каталог устройств
            </NuxtLink>
          </Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
