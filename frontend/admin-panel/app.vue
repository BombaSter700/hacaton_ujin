<template>
  <ClientOnly>
    <NuxtLayout><NuxtPage /></NuxtLayout>
    <template #fallback><p class="p-6">Загрузка панели…</p></template>
  </ClientOnly>
</template>
