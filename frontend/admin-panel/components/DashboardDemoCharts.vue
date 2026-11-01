<script setup lang="ts">
import { VisAxis, VisGroupedBar, VisLine, VisXYContainer } from '@unovis/vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import SmartIcon from '~/components/SmartIcon.vue'

const climate = [
  { hour: 0, temperature: 21.2 },
  { hour: 3, temperature: 20.8 },
  { hour: 6, temperature: 21.1 },
  { hour: 9, temperature: 22.5 },
  { hour: 12, temperature: 23.6 },
  { hour: 15, temperature: 23.1 },
  { hour: 18, temperature: 22.4 },
  { hour: 21, temperature: 21.8 },
  { hour: 24, temperature: 21.4 },
]
const energy = [
  { day: 'Пн', value: 11.2 },
  { day: 'Вт', value: 12.5 },
  { day: 'Ср', value: 10.8 },
  { day: 'Чт', value: 13.7 },
  { day: 'Пт', value: 12.1 },
  { day: 'Сб', value: 15.3 },
  { day: 'Вс', value: 13.4 },
]
const hourLabel = (value: number) => `${String(Math.round(value)).padStart(2, '0')}:00`
const dayLabel = (value: number) => energy[Math.round(value)]?.day || ''
const energyLabel = (value: number) => String(value).replace('.', ',')
</script>

<template>
  <Card class="min-w-0 xl:col-span-7">
    <CardHeader class="flex flex-row items-start justify-between gap-3">
      <div class="flex items-center gap-3">
        <SmartIcon name="climate" :size="48" />
        <div>
          <CardTitle>Температура в доме</CardTitle>
          <CardDescription class="mt-1">Пример изменения за сутки · °C</CardDescription>
        </div>
      </div>
      <Badge variant="secondary">Демо</Badge>
    </CardHeader>
    <CardContent>
      <figure aria-label="Демонстрационный график температуры: от 20,8 до 23,6 градуса за сутки">
        <ClientOnly>
          <VisXYContainer
            :data="climate"
            :height="230"
            :y-domain="[18, 26]"
            :margin="{ top: 8, right: 10, bottom: 0, left: 0 }"
          >
            <VisLine
              :x="(point: (typeof climate)[number]) => point.hour"
              :y="(point: (typeof climate)[number]) => point.temperature"
              color="#14b8a6"
              :line-width="3"
            />
            <VisAxis
              type="x"
              :num-ticks="5"
              :tick-format="hourLabel"
              :grid-line="false"
              :tick-line="false"
              :domain-line="false"
            />
            <VisAxis type="y" :num-ticks="4" :tick-line="false" :domain-line="false" />
          </VisXYContainer>
          <template #fallback><Skeleton class="h-[230px] w-full" /></template>
        </ClientOnly>
        <figcaption class="mt-3 text-xs text-muted-foreground">
          Иллюстративные данные для демонстрации интерфейса.
        </figcaption>
      </figure>
    </CardContent>
  </Card>
  <Card class="min-w-0 xl:col-span-5">
    <CardHeader class="flex flex-row items-start justify-between gap-3">
      <div class="flex items-center gap-3">
        <SmartIcon name="energy" :size="48" />
        <div>
          <CardTitle>Энергопотребление</CardTitle>
          <CardDescription class="mt-1">Пример за неделю · кВт·ч</CardDescription>
        </div>
      </div>
      <Badge variant="secondary">Демо</Badge>
    </CardHeader>
    <CardContent>
      <figure
        aria-label="Демонстрационный график энергопотребления по дням недели: от 10,8 до 15,3 киловатт-часа"
      >
        <ClientOnly>
          <VisXYContainer
            :data="energy"
            :height="230"
            :margin="{ top: 8, right: 10, bottom: 0, left: 0 }"
          >
            <VisGroupedBar
              :x="(_point: (typeof energy)[number], index: number) => index"
              :y="(point: (typeof energy)[number]) => point.value"
              color="#3b82f6"
              :rounded-corners="5"
              :bar-padding="0.3"
            />
            <VisAxis
              type="x"
              :tick-values="[0, 1, 2, 3, 4, 5, 6]"
              :tick-format="dayLabel"
              :grid-line="false"
              :tick-line="false"
              :domain-line="false"
            />
            <VisAxis
              type="y"
              :num-ticks="4"
              :tick-format="energyLabel"
              :tick-line="false"
              :domain-line="false"
            />
          </VisXYContainer>
          <template #fallback><Skeleton class="h-[230px] w-full" /></template>
        </ClientOnly>
        <figcaption class="mt-3 text-xs text-muted-foreground">
          Иллюстративные данные для демонстрации интерфейса.
        </figcaption>
      </figure>
    </CardContent>
  </Card>
</template>
