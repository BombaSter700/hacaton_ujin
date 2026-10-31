import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
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
    '@pinia/nuxt',
    '~/modules/core/module',        // Core модуль: auth, notifications, profile
    '~/modules/dashboard/module', // Dashboard модуль: analytics, reports, widgets
    '~/modules/certificates/module', // Certificates модуль: certificate management, templates
    '~/modules/events/module', // Events модуль: event management, calendar
    '~/modules/integrations/module', // Integrations модуль: third-party service integrations
    '~/modules/payslips/module',      // Payroll модуль: payroll management
    '~/modules/news/module',           // News модуль: company news, announcements
    '~/modules/users/module',          // User management модуль: user profiles, permissions

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