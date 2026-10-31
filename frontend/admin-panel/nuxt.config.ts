
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2026-10-31',

  experimental: {
    appManifest: false,
  },

  app: {
    baseURL: '/admin'
  },
  runtimeConfig: {
    public: {
      apiUrl: '',
      wsPort: ''
    }
  },
  css: [
    '~/assets/css/tailwind.css'
  ],
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
  modules: [
    'shadcn-nuxt', 
    '@pinia/nuxt'

  ],
  shadcn: {
    /**
     * Prefix for all the imported component
     */
    prefix: '',
    /**
     * Directory that the component lives in.
     * @default "./components/ui"
     */
    componentDir: './components/ui'
  }
})