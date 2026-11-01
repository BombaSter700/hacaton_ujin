<script setup lang="ts">
import { computed, ref } from 'vue'
import { AlertTriangle, Bell, Check, RotateCcw } from 'lucide-vue-next'
import { useWorkspaceStore } from '~/stores/workspace'
import { formatDateTime } from '~/utils/format'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'

const workspace = useWorkspaceStore()
const open = ref(false)
const unread = ref(true)
const occurredAt = ref(new Date())
const elevator = computed(() =>
  workspace.devices.find((device) => device.device_type.replace(/^emul_/, '') === 'elevator'),
)
const target = computed(() => (elevator.value ? '/devices/' + elevator.value.id : '/devices'))

function repeatDemo() {
  occurredAt.value = new Date()
  unread.value = true
}
function openDevice() {
  unread.value = false
  open.value = false
}
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button
        variant="ghost"
        size="icon"
        class="relative"
        :aria-label="unread ? 'Уведомления: 1 непрочитанное демо-событие' : 'Уведомления'"
      >
        <Bell class="size-5" />
        <span
          v-if="unread"
          class="absolute right-0 top-0 flex size-4 items-center justify-center rounded-full bg-destructive text-[10px] font-semibold text-white"
          aria-hidden="true"
        >
          1
        </span>
      </Button>
    </PopoverTrigger>
    <PopoverContent align="end" class="w-[calc(100vw-2rem)] max-w-sm p-0">
      <div class="flex items-center justify-between gap-2 border-b p-4">
        <div>
          <h2 class="font-semibold">Уведомления</h2>
          <p class="text-xs text-muted-foreground">
            {{ unread ? '1 непрочитанное' : 'Все прочитаны' }}
          </p>
        </div>
        <Button variant="ghost" size="sm" @click="repeatDemo">
          <RotateCcw class="mr-1 size-3.5" />
          Повторить демо
        </Button>
      </div>
      <article class="space-y-4 p-4">
        <div class="flex items-start gap-3">
          <span class="rounded-lg bg-destructive/10 p-2 text-destructive">
            <AlertTriangle class="size-5" />
          </span>
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap gap-1.5">
              <Badge variant="destructive">Аварийное событие</Badge>
              <Badge variant="secondary">Демо</Badge>
            </div>
            <h3 class="font-semibold">Аварийная остановка лифта</h3>
            <p class="mt-1 text-sm text-muted-foreground">
              {{
                workspace.selectedName === 'Выберите объект'
                  ? 'Демонстрационный дом'
                  : workspace.selectedName
              }}
              · Лифт
            </p>
            <time
              class="mt-1 block text-xs text-muted-foreground"
              :datetime="occurredAt.toISOString()"
            >
              {{ formatDateTime(occurredAt) }}
            </time>
          </div>
        </div>
        <dl class="grid grid-cols-2 gap-3 rounded-lg border bg-muted/30 p-3 text-sm">
          <div>
            <dt class="text-xs text-muted-foreground">Аварийный сигнал</dt>
            <dd class="mt-1 font-medium text-destructive">Активен</dd>
          </div>
          <div>
            <dt class="text-xs text-muted-foreground">Движение</dt>
            <dd class="mt-1 font-medium">Остановлен</dd>
          </div>
          <div>
            <dt class="text-xs text-muted-foreground">Скорость</dt>
            <dd class="mt-1 font-medium">0 м/с</dd>
          </div>
          <div>
            <dt class="text-xs text-muted-foreground">Этаж</dt>
            <dd class="mt-1 font-medium">3</dd>
          </div>
        </dl>
        <p class="text-xs text-muted-foreground">
          Пример уведомления для презентации. Показатели вымышлены: событие не получено от
          устройства и не меняет его состояние.
        </p>
        <div class="flex flex-wrap gap-2">
          <Button size="sm" as-child>
            <NuxtLink :to="target" @click="openDevice">
              {{ elevator ? 'Открыть лифт' : 'Перейти к устройствам' }}
            </NuxtLink>
          </Button>
          <Button v-if="unread" variant="outline" size="sm" @click="unread = false">
            <Check class="mr-1 size-4" />
            Прочитано
          </Button>
          <span v-else class="inline-flex items-center gap-1 text-xs text-muted-foreground">
            <Check class="size-4" />
            Прочитано
          </span>
        </div>
      </article>
    </PopoverContent>
  </Popover>
</template>
