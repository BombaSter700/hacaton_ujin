<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Thermometer, Wind, Sunrise, Sun, Sunset, Moon } from 'lucide-vue-next'
import { Card } from '@/components/ui/card'

const currentTime = ref(new Date())
let timer: NodeJS.Timeout

onMounted(() => {
  timer = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})

const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
})

const hour = computed(() => currentTime.value.getHours())

const timeOfDay = computed(() => {
  if (hour.value >= 5 && hour.value < 12)
    return { text: 'Доброе утро', icon: Sunrise, color: 'text-amber-500' }
  if (hour.value >= 12 && hour.value < 18)
    return { text: 'Добрый день', icon: Sun, color: 'text-amber-500' }
  if (hour.value >= 18 && hour.value < 23)
    return { text: 'Добрый вечер', icon: Sunset, color: 'text-orange-500' }
  return { text: 'Доброй ночи', icon: Moon, color: 'text-indigo-500' }
})

const temperature = ref(22.4)
const co2Level = ref(650)
</script>

<template>
  <Card class="flex flex-wrap items-center justify-between gap-6 p-6 shadow-sm bg-card">
    <div class="flex items-center gap-4">
      <div class="rounded-full bg-muted p-3">
        <component :is="timeOfDay.icon" :class="['h-8 w-8', timeOfDay.color]" />
      </div>
      <div>
        <p class="text-3xl font-bold tracking-tight">{{ formattedTime }}</p>
        <p class="text-sm text-muted-foreground">{{ timeOfDay.text }}. Демо-показатели.</p>
      </div>
    </div>

    <div class="flex items-center gap-8 sm:gap-12">
      <div class="flex items-center gap-3">
        <div class="rounded-lg bg-orange-100 dark:bg-orange-950/50 p-2">
          <Thermometer class="h-5 w-5 text-orange-600 dark:text-orange-400" />
        </div>
        <div>
          <p class="text-xs font-medium text-muted-foreground">Температура</p>
          <p class="text-xl font-bold">{{ temperature }} °C</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="rounded-lg bg-emerald-100 dark:bg-emerald-950/50 p-2">
          <Wind class="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
        </div>
        <div>
          <p class="text-xs font-medium text-muted-foreground">Уровень CO₂</p>
          <p class="text-xl font-bold">
            {{ co2Level }}
            <span class="text-sm font-normal text-muted-foreground">ppm</span>
          </p>
        </div>
      </div>
    </div>
  </Card>
</template>
