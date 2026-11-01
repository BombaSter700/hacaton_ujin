<script setup lang="ts">
import { useWorkspaceStore } from '~/stores/workspace'
import { useAuthStore } from '~/stores/auth'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
const workspace = useWorkspaceStore()
const auth = useAuthStore()
onMounted(() => {
  if (auth.user?.role === 'admin') void workspace.refresh()
})
async function openObject(id: string) {
  await workspace.select(id)
  await navigateTo('/devices')
}
</script>
<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">Объекты</h1>
      <p class="text-muted-foreground">Дома с подключёнными устройствами.</p>
    </div>
    <p v-if="auth.user?.role !== 'admin'">Доступ к объектам предоставляется администратору.</p>
    <template v-else>
      <Skeleton v-if="workspace.loading" class="h-32 w-full" />
      <Alert v-if="workspace.error" variant="destructive">
        <AlertDescription>{{ workspace.error }}</AlertDescription>
      </Alert>
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <Card v-for="item in workspace.objects" :key="item.object_id">
          <CardHeader>
            <CardTitle>{{ item.name }}</CardTitle>
            <CardDescription>Подключено устройств: {{ item.devices_count }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-3">
            <Button :disabled="workspace.loading" @click="openObject(item.object_id)">
              Открыть устройства
            </Button>
            <Collapsible>
              <CollapsibleTrigger class="text-sm text-muted-foreground underline">
                Технические сведения
              </CollapsibleTrigger>
              <CollapsibleContent class="break-all pt-2 text-xs text-muted-foreground">
                UUID: {{ item.object_id }}
              </CollapsibleContent>
            </Collapsible>
          </CardContent>
        </Card>
      </div>
      <DemoSetup v-if="!workspace.loading && !workspace.objects.length" />
    </template>
  </div>
</template>
