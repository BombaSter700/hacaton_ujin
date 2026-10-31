import { useAuthStore } from '~/stores/auth'
import { configureApiClients } from '~/utils/api/httpClient'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  configureApiClients(String(config.public.apiUrl || ''))
  const auth = useAuthStore()
  const onUnauthorized = () => {
    auth.reset()
    void nuxtApp.runWithContext(() => navigateTo('/login'))
  }
  window.addEventListener('programmisto:unauthorized', onUnauthorized)
  nuxtApp.vueApp.onUnmount(() => window.removeEventListener('programmisto:unauthorized', onUnauthorized))
})
