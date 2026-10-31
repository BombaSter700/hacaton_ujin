<script setup lang="ts">
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
  pending.value = true; error.value = ''
  try { sessions.value = (await getSessions()).sessions }
  catch (cause) { error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить сессии' }
  finally { pending.value = false }
}
async function revoke(session: UserSession) {
  if (pending.value) return
  pending.value = true; error.value = ''
  try {
    await revokeSession(session.id)
    if (session.is_current) { auth.reset(); await navigateTo('/login') }
    else sessions.value = sessions.value.filter(item => item.id !== session.id)
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Не удалось завершить сессию' }
  finally { pending.value = false }
}
onMounted(load)
</script>
<template>
  <Card><CardHeader><CardTitle>Мои сессии</CardTitle><CardDescription>Активные входы в учётную запись. Завершение текущей сессии выполнит выход.</CardDescription></CardHeader><CardContent>
    <p v-if="error" role="alert" class="mb-4 text-destructive">{{ error }}</p>
    <Button variant="outline" class="mb-4" :disabled="pending" @click="load">Обновить</Button>
    <p v-if="pending" class="text-muted-foreground">Загрузка…</p>
    <ul class="divide-y"><li v-for="session in sessions" :key="session.id" class="flex flex-wrap items-center justify-between gap-4 py-4"><div><p>Сессия #{{ session.id }} {{ session.is_current ? '(текущая)' : '' }}</p><p class="text-sm text-muted-foreground">Создана: {{ session.created_at }} · Действует до: {{ session.expires_at }}</p></div><Button variant="outline" :disabled="pending" @click="revoke(session)">Завершить</Button></li></ul>
    <p v-if="!pending && !sessions.length">Нет активных сессий</p>
  </CardContent></Card>
</template>
