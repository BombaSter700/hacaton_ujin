<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
const auth = useAuthStore()
const form = reactive({ first_name: auth.user?.first_name || '', last_name: auth.user?.last_name || '', phone: auth.user?.phone || '' })
const pending = ref(false)
const error = ref('')
const saved = ref(false)
async function save() {
  if (pending.value) return
  pending.value = true; error.value = ''; saved.value = false
  try {
    await auth.saveProfile({ first_name: form.first_name.trim() || null, last_name: form.last_name.trim() || null, phone: form.phone.trim() || null })
    saved.value = true
  } catch (cause) { error.value = cause instanceof Error ? cause.message : 'Не удалось сохранить профиль' }
  finally { pending.value = false }
}
</script>
<template>
  <Card class="max-w-xl"><CardHeader><CardTitle>Мой профиль</CardTitle></CardHeader><CardContent>
    <p class="mb-4 text-sm text-muted-foreground">{{ auth.user?.email }} · {{ auth.roleName }}</p>
    <form class="space-y-4" @submit.prevent="save">
      <p v-if="error" role="alert" class="text-destructive">{{ error }}</p><p v-if="saved" role="status">Профиль сохранён</p>
      <div class="space-y-2"><Label for="profile-first">Имя</Label><Input id="profile-first" v-model="form.first_name" maxlength="50" /></div>
      <div class="space-y-2"><Label for="profile-last">Фамилия</Label><Input id="profile-last" v-model="form.last_name" maxlength="50" /></div>
      <div class="space-y-2"><Label for="profile-phone">Телефон</Label><Input id="profile-phone" v-model="form.phone" type="tel" maxlength="20" /></div>
      <Button :disabled="pending" type="submit">{{ pending ? 'Сохранение…' : 'Сохранить' }}</Button>
    </form>
  </CardContent></Card>
</template>
