<script setup lang="ts">
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
definePageMeta({ path: '/sessions', name: 'sessions' })
import { getSessions, revokeSession } from '~/utils/api/auth'
import type { UserSession } from '~/types/auth'
import { useAuthStore } from '~/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
const auth = useAuthStore()
const sessions = ref<UserSession[]>([])
const pending = ref(false)
const error = ref('')
async function load() {
  pending.value = true
  error.value = ''
  try {
    sessions.value = (await getSessions()).sessions
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить сессии'
  } finally {
    pending.value = false
  }
}
async function revoke(session: UserSession) {
  if (pending.value) return
  pending.value = true
  error.value = ''
  try {
    await revokeSession(session.id)
    if (session.is_current) {
      auth.reset()
      await navigateTo('/login')
    } else sessions.value = sessions.value.filter((item) => item.id !== session.id)
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось завершить сессию'
  } finally {
    pending.value = false
  }
}
onMounted(load)
</script>
<template>
  <Card>
    <CardHeader>
      <CardTitle>Мои сессии</CardTitle>
      <CardDescription>
        Активные входы в учётную запись. Завершение текущей сессии выполнит выход.
      </CardDescription>
    </CardHeader>
    <CardContent>
      <Alert v-if="error" variant="destructive">
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>
      <Button variant="outline" class="mb-4" :disabled="pending" @click="load">Обновить</Button>
      <div v-if="pending" role="status" class="space-y-2 py-4">
        <span class="sr-only">Загрузка…</span>
        <Skeleton class="h-5 w-48" />
        <Skeleton class="h-16 w-full" />
      </div>
      <ul class="divide-y">
        <li
          v-for="session in sessions"
          :key="session.id"
          class="flex flex-wrap items-center justify-between gap-4 py-4"
        >
          <div>
            <p>Сессия #{{ session.id }} {{ session.is_current ? '(текущая)' : '' }}</p>
            <p class="text-sm text-muted-foreground">
              Создана: {{ session.created_at }} · Действует до: {{ session.expires_at }}
            </p>
          </div>
          <Button variant="outline" :disabled="pending" @click="revoke(session)">Завершить</Button>
        </li>
      </ul>
      <Empty v-if="!pending && !sessions.length">
        <EmptyHeader><EmptyDescription>Нет активных сессий</EmptyDescription></EmptyHeader>
      </Empty>
    </CardContent>
  </Card>
</template>
