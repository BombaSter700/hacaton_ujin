
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref({
    name: 'Иван Петров',
    role: 'Администратор УК',
  })

  return { user }
})