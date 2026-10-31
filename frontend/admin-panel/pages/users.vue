<script setup lang="ts">
import { Search, ShieldCheck, UserRound, Users } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
const query = ref('')
const users = [
  { id: 1, name: 'Иван Петров', email: 'ivan@example.test', role: 'Администратор УК', status: 'Активен' },
  { id: 2, name: 'Мария Соколова', email: 'maria@example.test', role: 'Диспетчер', status: 'Активен' },
  { id: 3, name: 'Алексей Смирнов', email: 'alex@example.test', role: 'Оператор', status: 'Приглашён' },
]
const filtered = computed(() => users.filter(u => `${u.name} ${u.email} ${u.role}`.toLowerCase().includes(query.value.toLowerCase())))
</script>
<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center gap-3"><h1 class="text-2xl font-bold">Пользователи</h1><Badge variant="secondary">Демо</Badge>
    </div>
    <Card><CardHeader><CardTitle class="flex items-center gap-2 text-base">
      <Users class="size-5" />Сотрудники УК</CardTitle>
      <CardDescription>Пользователи и роли приведены в качестве примера; управление доступом подключается через backend.</CardDescription></CardHeader><CardContent>
        <div class="relative mb-4 max-w-sm"><Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input v-model="query" placeholder="Поиск сотрудника" class="pl-9" />
        </div>
        <div class="overflow-x-auto rounded-lg border"><Table><TableHeader><TableRow><TableHead>Сотрудник</TableHead><TableHead>Email</TableHead><TableHead>Роль</TableHead><TableHead>Статус</TableHead></TableRow></TableHeader><TableBody><TableRow v-for="u in filtered" :key="u.id">
          <TableCell class="font-medium">
          <div class="flex items-center gap-2"><UserRound class="size-4 text-muted-foreground" />{{ u.name }}
          </div></TableCell>
          <TableCell>{{ u.email }}</TableCell>
          <TableCell><span class="inline-flex items-center gap-1"><ShieldCheck class="size-4 text-muted-foreground" />{{ u.role }}</span></TableCell>
          <TableCell><Badge variant="outline">{{ u.status }}</Badge></TableCell></TableRow>
          <TableRow v-if="!filtered.length"><TableCell colspan="4" class="py-10 text-center text-muted-foreground">Сотрудники не найдены</TableCell></TableRow></TableBody></Table>
        </div></CardContent></Card>
  </div>
</template>
