<script setup lang="ts">
import { Bell, ChevronDown, LogOut, Menu, Settings } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'

const auth = useAuthStore()
const emit = defineEmits<{ toggleSidebar: [] }>()
const logoutPending = ref(false)
const logoutError = ref('')
async function signOut() {
  if (logoutPending.value) return
  logoutPending.value = true
  logoutError.value = ''
  try { await auth.logout(); await navigateTo('/login') }
  catch (error) { logoutError.value = error instanceof Error ? error.message : 'Не удалось выйти' }
  finally { logoutPending.value = false }
}
</script>

<template>
  <header class="sticky top-0 z-20 flex h-16 items-center justify-between gap-3 border-b bg-card px-4 md:px-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" size="icon" class="lg:hidden" aria-label="Открыть меню" @click="emit('toggleSidebar')"><Menu class="size-5" /></Button>
      <div><p class="text-sm font-semibold">Панель управления</p><p class="hidden text-xs text-muted-foreground sm:block">Управление объектами и IoT-устройствами</p></div>
      <p v-if="logoutError" role="alert" class="text-xs text-destructive">{{ logoutError }}</p>
    </div>
    <div class="flex items-center gap-2">
      <Button variant="ghost" size="icon" disabled aria-label="Уведомления (скоро)" title="Уведомления пока не подключены"><Bell class="size-4" /></Button>
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" class="h-auto gap-2 px-2 py-1.5">
            <Avatar class="size-8"><AvatarFallback>{{ auth.displayName.charAt(0).toUpperCase() }}</AvatarFallback></Avatar>
            <span class="hidden text-left sm:block"><span class="block text-sm font-medium">{{ auth.displayName }}</span><span class="block text-xs text-muted-foreground">{{ auth.roleName }}</span></span>
            <ChevronDown class="size-4 text-muted-foreground" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-56">
          <DropdownMenuLabel>Учётная запись</DropdownMenuLabel><DropdownMenuSeparator />
          <DropdownMenuItem @select="navigateTo('/profile')"><Settings class="mr-2 size-4" /> Мой профиль</DropdownMenuItem>
          <DropdownMenuItem @select="navigateTo('/sessions')">Мои сессии</DropdownMenuItem>
          <DropdownMenuItem :disabled="logoutPending" @select="signOut"><LogOut class="mr-2 size-4" /> {{ logoutPending ? 'Выход…' : 'Выйти' }}</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </header>
</template>
