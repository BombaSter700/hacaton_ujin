<script setup lang="ts">
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Building2, MapPin, Plus, Search } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableEmpty,
} from '@/components/ui/table'

const search = ref('')
const dialogOpen = ref(false)
const name = ref('')
const address = ref('')
const objects = ref([
  {
    id: 1,
    name: 'ЖК Северный · Корпус 1',
    address: 'ул. Северная, 12',
    devices: 32,
    status: 'Активен',
  },
  {
    id: 2,
    name: 'ЖК Северный · Корпус 2',
    address: 'ул. Северная, 14',
    devices: 24,
    status: 'Активен',
  },
  {
    id: 3,
    name: 'ЖК Центральный · Корпус 1',
    address: 'ул. Центральная, 8',
    devices: 31,
    status: 'Активен',
  },
])
const filtered = computed(() =>
  objects.value.filter((o) =>
    `${o.name} ${o.address}`.toLowerCase().includes(search.value.toLowerCase()),
  ),
)

function addObject() {
  if (!name.value.trim() || !address.value.trim()) return
  objects.value.push({
    id: Date.now(),
    name: name.value.trim(),
    address: address.value.trim(),
    devices: 0,
    status: 'Новый',
  })
  name.value = ''
  address.value = ''
  dialogOpen.value = false
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-2xl font-bold">Объекты</h1>
          <Badge variant="secondary">Демо</Badge>
        </div>
        <p class="mt-1 text-sm text-muted-foreground">Список зданий под управлением УК.</p>
      </div>

      <Dialog v-model:open="dialogOpen">
        <DialogTrigger as-child>
          <Button>
            <Plus class="mr-2 h-4 w-4" />
            Добавить объект
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Новый объект</DialogTitle>
            <DialogDescription>
              Объект добавится только в локальный демонстрационный список.
            </DialogDescription>
          </DialogHeader>
          <form class="flex flex-col gap-4" @submit.prevent="addObject">
            <div class="flex flex-col gap-2">
              <Label for="object-name">Название</Label>
              <Input id="object-name" v-model="name" required placeholder="Например, ЖК Северный" />
            </div>
            <div class="flex flex-col gap-2">
              <Label for="object-address">Адрес</Label>
              <Input id="object-address" v-model="address" required placeholder="Адрес объекта" />
            </div>
            <DialogFooter>
              <Button type="submit" :disabled="!name.trim() || !address.trim()">Добавить</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>

    <Card>
      <CardHeader>
        <CardTitle class="text-base">Реестр объектов</CardTitle>
        <CardDescription>Данные представлены для демонстрации интерфейса</CardDescription>
      </CardHeader>
      <CardContent>
        <div class="relative mb-4 max-w-sm flex items-center">
          <Search class="absolute left-3 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input v-model="search" class="pl-9" placeholder="Поиск по названию или адресу" />
        </div>

        <div class="overflow-x-auto rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Объект</TableHead>
                <TableHead>Адрес</TableHead>
                <TableHead>Устройств</TableHead>
                <TableHead>Статус</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="object in filtered" :key="object.id">
                <TableCell class="font-medium">
                  <div class="flex items-center gap-2">
                    <Building2 class="h-4 w-4 text-muted-foreground" />
                    {{ object.name }}
                  </div>
                </TableCell>
                <TableCell>
                  <div class="flex items-center gap-1 text-muted-foreground">
                    <MapPin class="h-3.5 w-3.5" />
                    {{ object.address }}
                  </div>
                </TableCell>
                <TableCell>{{ object.devices }}</TableCell>
                <TableCell>
                  <Badge variant="secondary">{{ object.status }}</Badge>
                </TableCell>
              </TableRow>

              <TableEmpty v-if="!filtered.length" :colspan="4">
                <Empty>
                  <EmptyHeader><EmptyDescription>Объекты не найдены</EmptyDescription></EmptyHeader>
                </Empty>
              </TableEmpty>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
