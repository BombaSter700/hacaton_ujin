<script setup lang="ts">
import { register } from '~/utils/api/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

definePageMeta({ layout: 'auth' })
const form = reactive({ email: '', password: '', first_name: '', last_name: '', phone: '' })
const pending = ref(false)
const error = ref('')
async function submit() {
  if (pending.value) return
  pending.value = true
  error.value = ''
  try {
    await register({
      email: form.email.trim(), password: form.password,
      first_name: form.first_name.trim() || null,
      last_name: form.last_name.trim() || null, phone: form.phone.trim() || null,
    })
    form.password = ''
    await navigateTo('/login?registered=1')
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Не удалось зарегистрироваться' }
  finally { pending.value = false }
}
</script>
<template>
  <Card class="mx-4 w-full max-w-md">
    <CardHeader><CardTitle>Регистрация</CardTitle><CardDescription>Будет создана учётная запись клиента. Права администратора через регистрацию не выдаются.</CardDescription></CardHeader>
    <CardContent><form class="space-y-4" @submit.prevent="submit">
      <p v-if="error" role="alert" class="text-sm text-destructive">{{ error }}</p>
      <div class="space-y-2"><Label for="register-email">Email</Label><Input id="register-email" v-model="form.email" type="email" autocomplete="username" required maxlength="254" /></div>
      <div class="space-y-2"><Label for="register-password">Пароль</Label><Input id="register-password" v-model="form.password" type="password" autocomplete="new-password" required minlength="8" /><p class="text-xs text-muted-foreground">Минимум 8 символов, максимум 72 байта UTF-8.</p></div>
      <div class="space-y-2"><Label for="first-name">Имя</Label><Input id="first-name" v-model="form.first_name" autocomplete="given-name" maxlength="50" /></div>
      <div class="space-y-2"><Label for="last-name">Фамилия</Label><Input id="last-name" v-model="form.last_name" autocomplete="family-name" maxlength="50" /></div>
      <div class="space-y-2"><Label for="phone">Телефон</Label><Input id="phone" v-model="form.phone" type="tel" autocomplete="tel" maxlength="20" /></div>
      <Button type="submit" class="w-full" :disabled="pending">{{ pending ? 'Регистрация…' : 'Создать учётную запись' }}</Button>
      <p class="text-center text-sm"><NuxtLink to="/login" class="underline">Уже есть учётная запись</NuxtLink></p>
    </form></CardContent>
  </Card>
</template>
