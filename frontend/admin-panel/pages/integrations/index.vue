<script setup lang="ts">
import { useWorkspaceStore } from '~/stores/workspace'
import { useAuthStore } from '~/stores/auth'
import { getIntegrations } from '~/utils/api/integration'
import type { Integration } from '~/types/integration'
import { formatDateTime, formatIntegrationStatus } from '~/utils/format'
import { displayLabel } from '~/utils/device-labels'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
const workspace = useWorkspaceStore()
const auth = useAuthStore()
const items = ref<Integration[]>([])
const error = ref('')
async function load() {
  if (!workspace.context) return
  try {
    items.value = await getIntegrations(workspace.context.organization_id)
    error.value = ''
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось загрузить подключения'
  }
}
onMounted(async () => {
  if (auth.user?.role === 'admin') {
    await workspace.initialize()
    await load()
  }
})
watch(
  () => workspace.preparing,
  (preparing) => {
    if (!preparing) void load()
  },
)
</script>
<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">Подключения</h1>
      <p class="text-muted-foreground">Подготовьте стенд и переходите к управлению устройствами.</p>
    </div>
    <p v-if="auth.user?.role !== 'admin'">Подключения доступны администратору.</p>
    <template v-else>
      <DemoSetup />
      <Alert v-if="error" variant="destructive">
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>
      <Card v-for="item in items" :key="item.id">
        <CardHeader>
          <div class="flex items-center justify-between gap-3">
            <CardTitle>{{ displayLabel(item.name) }}</CardTitle>
            <Badge variant="outline">{{ formatIntegrationStatus(item.status) }}</Badge>
          </div>
        </CardHeader>
        <CardContent class="space-y-3">
          <p class="text-sm">Последнее обновление: {{ formatDateTime(item.last_sync_at) }}</p>
          <Collapsible>
            <CollapsibleTrigger class="text-sm text-muted-foreground underline">
              Технические сведения
            </CollapsibleTrigger>
            <CollapsibleContent class="space-y-1 break-all pt-3 text-xs text-muted-foreground">
              <p>UUID подключения: {{ item.id }}</p>
              <p>Организация: {{ item.organization_id }}</p>
              <p>Адрес: {{ item.base_url }}</p>
            </CollapsibleContent>
          </Collapsible>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
