<script setup lang="ts">
import { Empty, EmptyHeader, EmptyDescription } from '@/components/ui/empty'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getIntegrations, syncEmulators } from '~/utils/api/integration'
import type { Integration } from '~/types/integration'
import { useAuthStore } from '~/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
const auth = useAuthStore()
const route = useRoute()
const organizationId = ref(
  typeof route.query.organization_id === 'string' ? route.query.organization_id : '',
)
const items = ref<Integration[]>([])
const pending = ref(false)
const loaded = ref(false)
const error = ref('')
const objectId = ref('')
const syncing = ref(false)
const syncMessage = ref('')
async function sync() {
  if (syncing.value) return
  syncing.value = true
  error.value = ''
  syncMessage.value = ''
  try {
    const result = await syncEmulators(organizationId.value.trim(), objectId.value.trim())
    syncMessage.value = `Синхронизировано устройств: ${result.devices_count}`
    await load()
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Ошибка синхронизации'
  } finally {
    syncing.value = false
  }
}
async function load() {
  if (pending.value || !organizationId.value.trim()) return
  pending.value = true
  error.value = ''
  loaded.value = false
  items.value = []
  try {
    await navigateTo(
      { path: '/integrations', query: { organization_id: organizationId.value.trim() } },
      { replace: true },
    )
    items.value = await getIntegrations(organizationId.value.trim())
    loaded.value = true
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить подключения'
  } finally {
    pending.value = false
  }
}
onMounted(() => {
  if (auth.user?.role === 'admin' && organizationId.value) void load()
})
</script>
<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">Подключения IoT</h1>
    <Card>
      <CardHeader>
        <CardTitle>Подключения организации</CardTitle>
        <CardDescription>
          Зарегистрированные подключения к платформам. Секреты доступа не отображаются.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p v-if="auth.user?.role !== 'admin'">Доступ пока предоставляется только администратору.</p>
        <template v-else>
          <form class="mb-6 space-y-3 rounded border p-4" @submit.prevent="sync">
            <p class="font-medium">Подключить эмуляторы к объекту</p>
            <p class="text-sm text-muted-foreground">
              Укажите организацию в поле ниже и UUID объекта. Повторный импорт обновляет описания
              существующих устройств.
            </p>
            <Label for="sync-object">UUID объекта</Label>
            <Input id="sync-object" v-model="objectId" required />
            <Button type="submit" :disabled="syncing || !organizationId.trim()">
              {{ syncing ? 'Синхронизация…' : 'Синхронизировать эмуляторы' }}
            </Button>
            <Alert v-if="syncMessage" role="status">
              <AlertDescription>{{ syncMessage }}</AlertDescription>
            </Alert>
            <NuxtLink
              v-if="syncMessage"
              :to="{ path: '/devices', query: { object_id: objectId } }"
              class="block underline"
            >
              Открыть устройства объекта
            </NuxtLink>
          </form>
          <form class="mb-6 flex flex-wrap items-end gap-3" @submit.prevent="load">
            <div class="min-w-64 flex-1 space-y-2">
              <Label for="organization-id">UUID организации</Label>
              <Input id="organization-id" v-model="organizationId" required />
            </div>
            <Button type="submit" :disabled="pending">
              {{ pending ? 'Загрузка…' : 'Загрузить' }}
            </Button>
          </form>
          <Alert v-if="error" variant="destructive">
            <AlertDescription>{{ error }}</AlertDescription>
          </Alert>
          <Empty v-if="loaded && !items.length">
            <EmptyHeader>
              <EmptyDescription>Подключения не зарегистрированы</EmptyDescription>
            </EmptyHeader>
          </Empty>
          <ul class="divide-y">
            <li v-for="item in items" :key="item.id" class="space-y-1 py-4">
              <h2 class="font-semibold">{{ item.name }}</h2>
              <p class="text-sm">{{ item.platform_type }} · {{ item.status }}</p>
              <p class="break-all text-sm text-muted-foreground">{{ item.base_url }}</p>
              <p class="text-xs text-muted-foreground">UUID: {{ item.id }}</p>
              <p class="text-xs text-muted-foreground">
                Последняя синхронизация: {{ item.last_sync_at || 'Нет данных' }}
              </p>
            </li>
          </ul>
        </template>
      </CardContent>
    </Card>
  </div>
</template>
