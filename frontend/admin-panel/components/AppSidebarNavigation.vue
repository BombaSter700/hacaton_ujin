<script setup lang="ts">
import { Building2, Cpu, LayoutDashboard, Users, Plug, Workflow } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()

const emit = defineEmits<{ close: [] }>()
const links = [
  { to: '/dashboard', label: 'Обзор', icon: LayoutDashboard },
  { to: '/objects', label: 'Объекты', icon: Building2 },
  { to: '/devices', label: 'Устройства', icon: Cpu },
  { to: '/integrations', label: 'Подключения', icon: Plug },
  { to: '/scenarios', label: 'Сценарии', icon: Workflow },
  { to: '/users', label: 'Пользователи', icon: Users },
]
const visibleLinks = computed(() =>
  links.filter(
    (link) =>
      !['/users', '/devices', '/integrations', '/scenarios'].includes(link.to) ||
      auth.user?.role === 'admin',
  ),
)
</script>

<template>
  <div class="flex h-16 items-center justify-between border-b px-5">
    <NuxtLink to="/dashboard" class="flex items-center gap-2 font-semibold" @click="emit('close')">
      <span class="rounded-lg bg-slate-100 p-2 text-primary-foreground">
        <SmartIcon name="smart-home" :size="45" />
      </span>
      Умный дом
      <span class="text-xs text-muted-foreground">УК</span>
    </NuxtLink>
  </div>
  <div class="px-5 pt-5 pb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
    Навигация
  </div>
  <nav class="flex-1 space-y-1 px-3" aria-label="Основная навигация">
    <NuxtLink
      v-for="link in visibleLinks"
      :key="link.to"
      :to="link.to"
      class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
      active-class="!bg-primary/10 !text-primary"
      @click="emit('close')"
    >
      <component :is="link.icon" class="size-4" />
      {{ link.label }}
    </NuxtLink>
  </nav>
  <div class="border-t px-5 py-4 text-xs text-muted-foreground">
    Устройства из API · Обзор и объекты — демо
  </div>
</template>
