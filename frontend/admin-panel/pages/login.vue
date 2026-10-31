<script setup lang="ts">
import { Eye, EyeOff, House, LockKeyhole, Mail } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
definePageMeta({ layout: 'auth' })
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const notice = ref(false)
function submit() { notice.value = true }
</script>
<template><Card class="mx-4 w-full max-w-sm"><CardHeader class="items-center text-center"><span class="mb-2 rounded-xl bg-primary p-3 text-primary-foreground"><House class="size-6" /></span><CardTitle class="text-2xl">Вход в систему</CardTitle><CardDescription>Управление объектами умного дома</CardDescription></CardHeader><CardContent><form class="space-y-4" @submit.prevent="submit"><div class="space-y-2"><Label for="email">Электронная почта</Label><div class="relative"><Mail class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input id="email" v-model="email" required type="email" autocomplete="username" class="pl-9" placeholder="admin@example.com" /></div></div><div class="space-y-2"><Label for="password">Пароль</Label><div class="relative"><LockKeyhole class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input id="password" v-model="password" required :type="showPassword ? 'text' : 'password'" autocomplete="current-password" class="pl-9 pr-10" placeholder="Введите пароль" /><Button type="button" variant="ghost" size="icon" class="absolute right-0 top-0" :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'" @click="showPassword = !showPassword"><EyeOff v-if="showPassword" class="size-4" /><Eye v-else class="size-4" /></Button></div></div><Button type="submit" class="w-full">Войти</Button><Alert v-if="notice"><AlertDescription>Авторизация ещё не подключена к API. В прототипе доступен <NuxtLink to="/dashboard" class="font-medium underline">просмотр демо-панели</NuxtLink>.</AlertDescription></Alert><p class="text-center text-xs text-muted-foreground">Демонстрационный интерфейс · без проверки учётных данных</p></form></CardContent></Card></template>
