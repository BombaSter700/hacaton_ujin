<script setup lang="ts">
type SmartIconName =
  | 'smart-home'
  | 'sensors'
  | 'climate'
  | 'smart-lock'
  | 'camera'
  | 'energy'
  | 'automation'
  | 'telemetry'

const props = withDefaults(
  defineProps<{
    name: SmartIconName
    size?: number
  }>(),
  {
    size: 24,
  },
)

const config = useRuntimeConfig()

const src = computed(() => {
  const base = config.app.baseURL.replace(/\/$/, '')
  return `${base}/images/${props.name}.png`
})
</script>

<template>
  <img
    :src="src"
    :width="size"
    :height="size"
    :alt="name"
    class="shrink-0 object-contain"
    loading="lazy"
  />
</template>
