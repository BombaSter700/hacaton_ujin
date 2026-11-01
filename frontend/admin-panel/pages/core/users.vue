<script setup lang="ts">
import { formatFullName, formatUserRole } from '~/utils/format'
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
definePageMeta({ path: '/users', name: 'users' })
import { getUsers } from '~/utils/api/auth'
import type { User } from '~/types/auth'
import { useAuthStore } from '~/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
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
const query = ref('')
const users = ref<User[]>([])
const pending = ref(false)
const error = ref('')
const skip = ref(0)
const limit = 50
const filtered = computed(() =>
  users.value.filter((user) =>
    [user.email, user.first_name, user.last_name]
      .join(' ')
      .toLowerCase()
      .includes(query.value.toLowerCase()),
  ),
)
async function load(offset = skip.value) {
  if (pending.value) return
  pending.value = true
  error.value = ''
  try {
    users.value = await getUsers(offset, limit)
    skip.value = offset
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить пользователей'
  } finally {
    pending.value = false
  }
}
onMounted(() => {
  if (auth.user?.role === 'admin') void load()
})
</script>
<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Пользователи</h1>
    <Card>
      <CardHeader>
        <CardTitle>Учётные записи</CardTitle>
        <CardDescription>
          Данные сервиса авторизации. Поиск выполняется по загруженной странице.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Alert v-if="auth.user?.role !== 'admin'" variant="destructive">
          <AlertDescription>Список пользователей доступен только администратору.</AlertDescription>
        </Alert>
        <template v-else>
          <div class="mb-4 flex gap-3">
            <Input v-model="query" placeholder="Поиск на странице" class="max-w-sm" />
            <Button variant="outline" :disabled="pending" @click="load()">Обновить</Button>
          </div>
          <Alert v-if="error" variant="destructive">
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
          <div v-if="pending" role="status" class="space-y-2 py-4">
            <span class="sr-only">Загрузка…</span>
            <Skeleton class="h-5 w-48" />
            <Skeleton class="h-16 w-full" />
          </div>
          <div class="overflow-x-auto rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Пользователь</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Роль</TableHead>
                  <TableHead>Статус</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="user in filtered" :key="user.id">
                  <TableCell>
                    {{ formatFullName(user.first_name, user.last_name) }}
                  </TableCell>
                  <TableCell>{{ user.email }}</TableCell>
                  <TableCell>{{ formatUserRole(user.role) }}</TableCell>
                  <TableCell>{{ user.is_active ? 'Активен' : 'Отключён' }}</TableCell>
                </TableRow>
                <TableEmpty v-if="!pending && !filtered.length" :colspan="4">
                  <Empty>
                    <EmptyHeader>
                      <EmptyDescription>Нет пользователей</EmptyDescription>
                    </EmptyHeader>
                  </Empty>
                </TableEmpty>
              </TableBody>
            </Table>
          </div>
          <div class="mt-4 flex items-center gap-3">
            <Button
              variant="outline"
              :disabled="pending || skip === 0"
              @click="load(Math.max(0, skip - limit))"
            >
              Назад
            </Button>
            <span class="text-sm">Страница {{ Math.floor(skip / limit) + 1 }}</span>
            <Button
              variant="outline"
              :disabled="pending || users.length < limit"
              @click="load(skip + limit)"
            >
              Далее
            </Button>
          </div>
        </template>
      </CardContent>
    </Card>
  </div>
</template>
