import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2026-10-31',
  app: { baseURL: '/admin/' },
  runtimeConfig: {
    public: {
      apiUrl: 'http://localhost:8080',
      integrationApiUrl: 'http://localhost:8002',
      wsPort: '',
    },
  },
  css: ['~/assets/css/tailwind.css'],
  vite: { plugins: [tailwindcss()] },
  modules: ['@pinia/nuxt'],
  nitro: { preset: 'node-server' },
})
