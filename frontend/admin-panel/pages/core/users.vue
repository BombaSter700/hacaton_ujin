<script setup lang="ts">
definePageMeta({ path: '/users', name: 'users' })
import { getUsers } from '~/utils/api/auth'
import type { User } from '~/types/auth'
import { useAuthStore } from '~/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
const auth = useAuthStore()
const query = ref('')
const users = ref<User[]>([])
const pending = ref(false)
const error = ref('')
const skip = ref(0)
const limit = 50
const filtered = computed(() => users.value.filter(user => [user.email, user.first_name, user.last_name].join(' ').toLowerCase().includes(query.value.toLowerCase())))
async function load(offset = skip.value) {
  if (pending.value) return
  pending.value = true
  error.value = ''
  try { users.value = await getUsers(offset, limit); skip.value = offset }
  catch (cause) { error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить пользователей' }
  finally { pending.value = false }
}
onMounted(() => { if (auth.user?.role === 'admin') void load() })
</script>
<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Пользователи</h1>
    <Card><CardHeader><CardTitle>Учётные записи</CardTitle><CardDescription>Данные сервиса авторизации. Поиск выполняется по загруженной странице.</CardDescription></CardHeader>
      <CardContent>
        <p v-if="auth.user?.role !== 'admin'" role="alert">Список пользователей доступен только администратору.</p>
        <template v-else>
          <div class="mb-4 flex gap-3"><Input v-model="query" placeholder="Поиск на странице" class="max-w-sm" /><Button variant="outline" :disabled="pending" @click="load()">Обновить</Button></div>
          <p v-if="error" role="alert" class="mb-4 text-destructive">{{ error }}</p>
          <p v-if="pending" class="mb-4 text-muted-foreground">Загрузка…</p>
          <div class="overflow-x-auto rounded-lg border"><Table><TableHeader><TableRow><TableHead>Пользователь</TableHead><TableHead>Email</TableHead><TableHead>Роль</TableHead><TableHead>Статус</TableHead></TableRow></TableHeader>
            <TableBody><TableRow v-for="user in filtered" :key="user.id"><TableCell>{{ [user.first_name, user.last_name].filter(Boolean).join(' ') || 'Без имени' }}</TableCell><TableCell>{{ user.email }}</TableCell><TableCell>{{ user.role === 'admin' ? 'Администратор' : 'Клиент' }}</TableCell><TableCell>{{ user.is_active ? 'Активен' : 'Отключён' }}</TableCell></TableRow><TableRow v-if="!pending && !filtered.length"><TableCell colspan="4" class="py-8 text-center">Нет пользователей</TableCell></TableRow></TableBody>
          </Table></div>
          <div class="mt-4 flex items-center gap-3"><Button variant="outline" :disabled="pending || skip === 0" @click="load(Math.max(0, skip - limit))">Назад</Button><span class="text-sm">Страница {{ Math.floor(skip / limit) + 1 }}</span><Button variant="outline" :disabled="pending || users.length < limit" @click="load(skip + limit)">Далее</Button></div>
        </template>
      </CardContent>
    </Card>
  </div>
</template>
