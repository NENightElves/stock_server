// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/ui', '@nuxtjs/mdc'],
  ssr: false,
  css: ['~/assets/css/main.css'],
  ui: {
    fonts: false
  },
  mdc: {
    headings: {
      anchorLinks: false
    }
  },
  runtimeConfig: {
    public: {
      baseUrl: process.env.BASE_URL || ''
    }
  }
})