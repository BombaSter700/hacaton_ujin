<script setup lang="ts" generic="T extends Record<string, any>">
import { computed } from 'vue'
import { Scale } from '@unovis/ts'
import { VisXYContainer, VisLine, VisAxis } from '@unovis/vue'
import { cn } from '@/lib/utils'

type Accessor<T, R = unknown> = keyof T | ((item: T, index?: number) => R)

type MultiLineSeries<T extends Record<string, any>> = {
  key: keyof T | string
  y: Accessor<T, number>
  label?: string
}

type BaseMultiLineChartProps<T extends Record<string, any>> = {
  data: T[]
  x: Accessor<T>
  series: MultiLineSeries<T>[]
  colors?: string[]
  height?: number
  showLegend?: boolean
  numTicks?: number
  xTickFormat?: (value: any) => string
  yLabel?: string
}

const defaultColors = (length: number): string[] => {
  const palette = [
    '#3B82F6',
    '#10B981',
    '#F59E0B',
    '#EF4444',
    '#8B5CF6',
    '#EC4899',
    '#14B8A6',
    '#F97316',
  ]

  return Array.from({ length }, (_, i) => palette[i % palette.length])
}

const props = withDefaults(defineProps<BaseMultiLineChartProps<T>>(), {
  height: 300,
  showLegend: true,
  numTicks: 6,
})

const resolveAccessor = <R,>(accessor: Accessor<T, R>) => {
  if (typeof accessor === 'function') return accessor
  return (item: T) => item[accessor] as R
}

const safeNumber = (value: unknown): number | null => {
  if (value === null || value === undefined) return null
  const n = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(n) ? n : null
}

const normalizedData = computed(() => {
  const xGetter = resolveAccessor(props.x)

  return props.data.map((item, index) => {
    const rawX = xGetter(item, index)

    const xDate = rawX instanceof Date ? rawX : new Date(rawX as string | number)

    const normalized: Record<string, any> = {
      ...item,
      __x: xDate,
    }

    for (const s of props.series) {
      const yGetter = resolveAccessor(s.y)
      const rawY = yGetter(item, index)
      normalized[s.key as string] = safeNumber(rawY)
    }

    return normalized
  })
})

const xScale = Scale.scaleTime()

const colors = computed(() =>
  props.colors?.length ? props.colors : defaultColors(props.series.length),
)

const legendItems = computed(() =>
  props.series.map((s, i) => ({
    name: s.label ?? String(s.key),
    color: colors.value[i],
  })),
)

const xGetter = (d: any) => d.__x

const yGetters = computed(() => props.series.map((s) => (d: any) => d[s.key as string]))
</script>

<template>
  <div :class="cn('w-full flex flex-col gap-2', $attrs.class ?? '')">
    <ul v-if="showLegend" class="mb-1 flex flex-wrap items-center gap-x-4 gap-y-2">
      <li
        v-for="item in legendItems"
        :key="item.name"
        class="flex items-center gap-2 text-sm text-muted-foreground"
      >
        <span class="size-2 rounded-full" :style="{ backgroundColor: item.color }" />
        <span>{{ item.name }}</span>
      </li>
    </ul>

    <div v-if="!normalizedData.length" class="text-sm text-muted-foreground py-8 text-center">
      Нет данных
    </div>

    <VisXYContainer v-else :data="normalizedData" :height="height" :x-scale="xScale">
      <VisLine :x="xGetter" :y="yGetters" :color="colors" />

      <VisAxis
        type="x"
        label="Дата"
        :num-ticks="numTicks"
        :tick-format="xTickFormat ?? ((v: any) => new Date(v).toLocaleDateString())"
      />

      <VisAxis type="y" :label="yLabel" />
    </VisXYContainer>
  </div>
</template>
