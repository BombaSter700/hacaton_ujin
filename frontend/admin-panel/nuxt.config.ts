import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2026-10-31',

  experimental: {
    appManifest: false,
  },

  app: {
    baseURL: '/admin',
    head: {
      htmlAttrs: { lang: 'ru' },
      link: [
        { rel: 'manifest', href: '/admin/manifest.json' },
        {
          rel: 'icon',
          type: 'image/x-icon',
          sizes: '16x16 32x32 48x48',
          href: '/admin/favicon.ico',
        },
        { rel: 'apple-touch-icon', sizes: '192x192', href: '/admin/icons/icon-192x192.png' },
      ],
      meta: [{ name: 'theme-color', content: '#171717' }],
    },
  },
  runtimeConfig: {
    public: {
      apiUrl: '',
      wsPort: '',
    },
  },
  css: ['~/assets/css/tailwind.css'],
  vite: {
    plugins: [tailwindcss()],
  },
  modules: ['shadcn-nuxt', '@pinia/nuxt'],
  shadcn: {
    prefix: '',
    componentDir: './components/ui',
  },
})
