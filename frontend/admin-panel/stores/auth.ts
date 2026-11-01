import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as api from '~/utils/api/auth'
import { ApiError, tokenStore } from '~/utils/api/httpClient'
import type { LoginRequest, User } from '~/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const initialized = ref(false)
  const sessionError = ref('')
  let initializing: Promise<void> | null = null
  const displayName = computed(
    () =>
      [user.value?.first_name, user.value?.last_name].filter(Boolean).join(' ') ||
      user.value?.email ||
      '',
  )
  const roleName = computed(() => (user.value?.role === 'admin' ? 'Администратор' : 'Клиент'))
  function reset() {
    tokenStore.clear()
    user.value = null
    initialized.value = true
  }
  async function initialize() {
    if (initialized.value) return
    if (initializing) return initializing
    initializing = (async () => {
      sessionError.value = ''
      if (tokenStore.get()) {
        try {
          user.value = await api.getProfile()
        } catch (error) {
          if (error instanceof ApiError && error.status === 401) reset()
          else
            sessionError.value =
              error instanceof Error ? error.message : 'Сервис авторизации недоступен'
        }
      }
      initialized.value = true
    })()
    try {
      await initializing
    } finally {
      initializing = null
    }
  }
  async function completeLogin(tokens: Awaited<ReturnType<typeof api.login>>) {
    tokenStore.set(tokens)
    try {
      user.value = await api.getProfile()
      initialized.value = true
      sessionError.value = ''
    } catch (error) {
      reset()
      throw error
    }
  }
  async function login(data: LoginRequest) {
    await completeLogin(await api.login(data))
  }
  async function demoLogin() {
    await completeLogin(await api.demoLogin())
  }
  async function logout() {
    try {
      await api.logout()
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 401)) throw error
    }
    reset()
  }
  async function saveProfile(data: Parameters<typeof api.updateProfile>[0]) {
    user.value = await api.updateProfile(data)
  }
  return {
    user,
    initialized,
    sessionError,
    displayName,
    roleName,
    initialize,
    login,
    demoLogin,
    logout,
    saveProfile,
    reset,
  }
})
