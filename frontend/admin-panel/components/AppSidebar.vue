<script setup lang="ts">
import { useMediaQuery } from '@vueuse/core'
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '@/components/ui/sheet'

withDefaults(defineProps<{ mobileOpen?: boolean }>(), { mobileOpen: false })
const emit = defineEmits<{ close: [] }>()
const isDesktop = useMediaQuery('(min-width: 1024px)')
watch(isDesktop, (desktop) => {
  if (desktop) emit('close')
})
</script>

<template>
  <aside class="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r bg-card lg:flex">
    <AppSidebarNavigation @close="emit('close')" />
  </aside>
  <Sheet :open="mobileOpen && !isDesktop" @update:open="!$event && emit('close')">
    <SheetContent side="left" class="w-64 gap-0 bg-card p-0">
      <SheetTitle class="sr-only">Основная навигация</SheetTitle>
      <SheetDescription class="sr-only">
        Разделы панели управления объектами и IoT-устройствами
      </SheetDescription>
      <AppSidebarNavigation @close="emit('close')" />
    </SheetContent>
  </Sheet>
</template>
