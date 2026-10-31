<script setup lang="ts">
const mobileOpen = ref(false)
</script>
<template>
  <div class="flex min-h-screen bg-background">
    <AppSidebar :mobile-open="mobileOpen" @close="mobileOpen = false" />
    <div class="flex min-w-0 flex-1 flex-col">
      <AppHeader @toggle-sidebar="mobileOpen = !mobileOpen" />
      <main class="w-full flex-1 p-4 md:p-6 lg:p-8"><slot /></main>
    </div>
  </div>
</template>
