<script setup lang="ts">
import { Eye, EyeOff, House, LockKeyhole, Mail } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'auth' })
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const pending = ref(false)
const error = ref('')
const route = useRoute()
async function submit() {
  if (pending.value) return
  error.value = ''
  pending.value = true
  try {
    await auth.login({ email: email.value.trim(), password: password.value })
    password.value = ''
    await navigateTo('/dashboard')
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'Не удалось войти'
  } finally { pending.value = false }
}
</script>

<template>
  <Card class="mx-4 w-full max-w-sm">
    <CardHeader class="items-center text-center">
      <span class="mb-2 rounded-xl bg-primary p-3 text-primary-foreground"><House class="size-6" /></span>
      <CardTitle class="text-2xl">Вход в систему</CardTitle>
      <CardDescription>Управление объектами умного дома</CardDescription>
    </CardHeader>
    <CardContent>
      <form class="space-y-4" @submit.prevent="submit">
        <Alert v-if="route.query.registered"><AlertDescription>Учётная запись создана. Войдите с указанными данными.</AlertDescription></Alert>
        <Alert v-if="error || auth.sessionError" variant="destructive" role="alert"><AlertDescription>{{ error || auth.sessionError }}</AlertDescription></Alert>
        <div class="space-y-2">
          <Label for="email">Электронная почта</Label>
          <div class="relative"><Mail class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input id="email" v-model="email" required type="email" autocomplete="username" class="pl-9" placeholder="admin@example.com" :disabled="pending" /></div>
        </div>
        <div class="space-y-2">
          <Label for="password">Пароль</Label>
          <div class="relative">
            <LockKeyhole class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input id="password" v-model="password" required :type="showPassword ? 'text' : 'password'" autocomplete="current-password" class="pl-9 pr-10" :disabled="pending" />
            <Button type="button" variant="ghost" size="icon" class="absolute right-0 top-0" :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'" @click="showPassword = !showPassword"><EyeOff v-if="showPassword" class="size-4" /><Eye v-else class="size-4" /></Button>
          </div>
        </div>
        <Button type="submit" class="w-full" :disabled="pending">{{ pending ? 'Вход…' : 'Войти' }}</Button>
        <p class="text-center text-sm"><NuxtLink to="/register" class="underline">Создать учётную запись клиента</NuxtLink></p>
      </form>
    </CardContent>
  </Card>
</template>
