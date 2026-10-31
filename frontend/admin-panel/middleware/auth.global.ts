import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return
  const auth = useAuthStore()
  await auth.initialize()
  if (!auth.user && !['/login', '/register'].includes(to.path)) return navigateTo('/login')
  if (auth.user && ['/login', '/register'].includes(to.path)) return navigateTo('/dashboard')
})
