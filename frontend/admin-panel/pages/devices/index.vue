<script setup lang="ts">
import { Cpu, Search, SlidersHorizontal, Wifi, WifiOff } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
const search = ref('')
const status = ref('all')
const devices = [
  { id: '101', name: 'Реле освещения', model: 'Ujin Relay 1', object: 'ЖК Северный · Корпус 1', online: true, updated: 'Демо · 2 мин назад' },
  { id: '102', name: 'Датчик температуры', model: 'Temperature Sensor', object: 'ЖК Северный · Корпус 1', online: true, updated: 'Демо · 4 мин назад' },
  { id: '103', name: 'Контроллер освещения', model: 'Lighting Controller', object: 'ЖК Северный · Корпус 2', online: false, updated: 'Демо · 2 ч назад' },
  { id: '104', name: 'Датчик протечки', model: 'Leak Sensor', object: 'ЖК Центральный · Корпус 1', online: true, updated: 'Демо · 8 мин назад' },
]
const filtered = computed(() => devices.filter(d => (`${d.name} ${d.model} ${d.object}`).toLowerCase().includes(search.value.toLowerCase()) && (status.value === 'all' || (status.value === 'online' ? d.online : !d.online))))
</script>
<template>
  <div class="space-y-6"><div><div class="flex items-center gap-2"><h1 class="text-2xl font-bold">Устройства</h1><Badge variant="secondary">Демо-данные</Badge></div>
  <p class="mt-1 text-sm text-muted-foreground">Мониторинг подключённых IoT-устройств.</p></div>
    <Card><CardHeader><CardTitle class="text-base">Каталог устройств</CardTitle><CardDescription>Показаны образцы состояний, не показания в реальном времени</CardDescription></CardHeader><CardContent><div class="mb-4 flex flex-wrap gap-3"><div class="relative min-w-56 flex-1 sm:max-w-sm"><Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input v-model="search" placeholder="Поиск устройства или объекта" class="pl-9" /></div><Select v-model="status"><SelectTrigger class="w-44"><SlidersHorizontal class="mr-2 size-4" /><SelectValue placeholder="Все статусы" /></SelectTrigger><SelectContent><SelectItem value="all">Все статусы</SelectItem><SelectItem value="online">В сети</SelectItem><SelectItem value="offline">Нет связи</SelectItem></SelectContent></Select></div><div class="overflow-x-auto rounded-lg border"><Table><TableHeader><TableRow><TableHead>Устройство</TableHead><TableHead>Объект</TableHead><TableHead>Доступность</TableHead><TableHead>Последние данные</TableHead><TableHead class="text-right">Действия</TableHead></TableRow></TableHeader><TableBody><TableRow v-for="device in filtered" :key="device.id"><TableCell><div class="flex items-center gap-2"><Cpu class="size-4 text-muted-foreground" /><div><p class="font-medium">{{ device.name }}</p><p class="text-xs text-muted-foreground">{{ device.model }} · #{{ device.id }}</p></div></div></TableCell><TableCell>{{ device.object }}</TableCell><TableCell><Badge :variant="device.online ? 'secondary' : 'destructive'"><component :is="device.online ? Wifi : WifiOff" class="mr-1 size-3" />{{ device.online ? 'В сети' : 'Нет связи' }}</Badge></TableCell><TableCell class="text-muted-foreground">{{ device.updated }}</TableCell><TableCell class="text-right"><Button variant="outline" size="sm" as-child><NuxtLink :to="`/devices/${device.id}`">Подробнее</NuxtLink></Button></TableCell></TableRow><TableRow v-if="!filtered.length"><TableCell colspan="5" class="py-10 text-center text-muted-foreground">Устройства не найдены</TableCell></TableRow></TableBody></Table></div></CardContent></Card>
  </div>
</template>
