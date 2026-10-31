<script setup lang="ts">
import { ArrowLeft, Activity, CircleAlert, Cpu, Power, Wifi, WifiOff } from 'lucide-vue-next'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
const route = useRoute()
const samples: Record<string, { name: string; model: string; online: boolean; object: string }> = {
  '101': { name: 'Реле освещения', model: 'Ujin Relay 1', online: true, object: 'ЖК Северный · Корпус 1' },
  '102': { name: 'Датчик температуры', model: 'Temperature Sensor', online: true, object: 'ЖК Северный · Корпус 1' },
  '103': { name: 'Контроллер освещения', model: 'Lighting Controller', online: false, object: 'ЖК Северный · Корпус 2' },
  '104': { name: 'Датчик протечки', model: 'Leak Sensor', online: true, object: 'ЖК Центральный · Корпус 1' },
}
const device = computed(() => samples[String(route.params.id)])
const message = ref('')
function simulateCommand() { message.value = 'Команда не отправлена: подключение к backend API пока отсутствует. Это демонстрационный экран.' }
</script>
<template>
  <div class="space-y-6"><Button variant="ghost" as-child class="-ml-3"><NuxtLink to="/devices"><ArrowLeft class="mr-2 size-4" />Назад к устройствам</NuxtLink></Button>
    <template v-if="device"><div class="flex flex-wrap items-center gap-3"><h1 class="text-2xl font-bold">{{ device.name }} <span class="font-normal text-muted-foreground">#{{ route.params.id }}</span></h1><Badge :variant="device.online ? 'secondary' : 'destructive'"><component :is="device.online ? Wifi : WifiOff" class="mr-1 size-3" />{{ device.online ? 'В сети (демо)' : 'Нет связи (демо)' }}</Badge></div>
      <Alert v-if="message"><CircleAlert class="size-4" /><AlertTitle>Информация</AlertTitle><AlertDescription>{{ message }}</AlertDescription></Alert>
      <div class="grid gap-4 lg:grid-cols-3"><Card><CardHeader><CardTitle class="flex items-center gap-2"><Power class="size-5" />Управление</CardTitle><CardDescription>Карточка IoT-устройства</CardDescription></CardHeader><CardContent class="space-y-4"><div><p class="text-xs text-muted-foreground">Модель</p><p class="font-medium">{{ device.model }}</p></div><Separator /><div><p class="text-xs text-muted-foreground">Объект</p><p class="font-medium">{{ device.object }}</p></div><Separator /><div><p class="text-xs text-muted-foreground">Статус телеметрии</p><p class="text-sm">Демонстрационное значение, не обновляется с сервера</p></div><AlertDialog><AlertDialogTrigger as-child><Button class="w-full" :disabled="!device.online"><Power class="mr-2 size-4" />Подготовить команду</Button></AlertDialogTrigger><AlertDialogContent><AlertDialogHeader><AlertDialogTitle>Подтверждение команды</AlertDialogTitle><AlertDialogDescription>В этом прототипе отправка IoT-команд недоступна. После подключения API потребуется выбрать конкретное действие и получить подтверждённый ответ сервера.</AlertDialogDescription></AlertDialogHeader><AlertDialogFooter><AlertDialogCancel>Отмена</AlertDialogCancel><AlertDialogAction @click="simulateCommand">Понятно</AlertDialogAction></AlertDialogFooter></AlertDialogContent></AlertDialog></CardContent></Card>
        <Card class="lg:col-span-2"><CardHeader><CardTitle class="flex items-center gap-2"><Activity class="size-5" />История сигналов</CardTitle><CardDescription>График появится после подключения API истории телеметрии</CardDescription></CardHeader><CardContent><div class="flex min-h-64 flex-col items-center justify-center rounded-lg border border-dashed p-6 text-center"><Activity class="mb-3 size-9 text-muted-foreground" /><p class="font-medium">История пока недоступна</p><p class="mt-1 max-w-md text-sm text-muted-foreground">Здесь можно разместить график Unovis с временным диапазоном, единицами измерения и временем последнего обновления.</p></div></CardContent></Card>
      </div>
    </template><Card v-else><CardContent class="flex flex-col items-center gap-3 py-12"><Cpu class="size-8 text-muted-foreground" /><p class="font-semibold">Устройство не найдено</p><p class="text-sm text-muted-foreground">Для указанного ID нет демонстрационных данных.</p><Button as-child variant="outline"><NuxtLink to="/devices">К списку устройств</NuxtLink></Button></CardContent></Card>
  </div>
</template>
