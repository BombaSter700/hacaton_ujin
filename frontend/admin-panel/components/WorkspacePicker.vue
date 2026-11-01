<script setup lang="ts">
import { useWorkspaceStore } from '~/stores/workspace'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
defineProps<{ disabled?: boolean }>()
const workspace = useWorkspaceStore()
const pickerId = useId()
const choices = computed(() =>
  workspace.objects.length
    ? workspace.objects
    : workspace.context
      ? [{ object_id: workspace.context.object_id, name: workspace.context.name, devices_count: 0 }]
      : [],
)
</script>
<template>
  <div class="w-full space-y-2 sm:max-w-sm">
    <Label :for="pickerId">Объект</Label>
    <Select
      :model-value="workspace.selectedId || null"
      :disabled="disabled || workspace.loading || workspace.preparing"
      @update:model-value="workspace.select(String($event))"
    >
      <SelectTrigger :id="pickerId" class="w-full">
        <SelectValue placeholder="Выберите объект" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem v-for="item in choices" :key="item.object_id" :value="item.object_id">
          {{ item.name }} · {{ item.devices_count }} устр.
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
