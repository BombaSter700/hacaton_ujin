<script setup lang="ts">
import { useWorkspaceStore } from '~/stores/workspace'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
const workspace = useWorkspaceStore()
const ready = ref(false)
async function prepare() {
  ready.value = await workspace.prepare()
}
</script>
<template>
  <Card>
    <CardHeader>
      <CardTitle>Демонстрационный дом</CardTitle>
      <CardDescription>
        Подключите лифт, освещение, климат и датчики одной кнопкой. Повторная подготовка обновит
        существующие устройства.
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <Button :disabled="workspace.preparing || workspace.loading" @click="prepare">
        {{
          workspace.preparing
            ? 'Подключаем устройства…'
            : workspace.objects.length
              ? 'Обновить демонстрацию'
              : 'Подготовить демонстрацию'
        }}
      </Button>
      <Alert v-if="ready" role="status">
        <AlertDescription>
          Устройства подключены. Откройте каталог, выберите устройство и отправьте команду.
        </AlertDescription>
      </Alert>
      <Button v-if="ready" variant="outline" class="ml-2" as-child>
        <NuxtLink to="/devices">Открыть устройства</NuxtLink>
      </Button>
      <Alert v-if="workspace.error" variant="destructive">
        <AlertDescription>{{ workspace.error }}</AlertDescription>
      </Alert>
    </CardContent>
  </Card>
</template>
