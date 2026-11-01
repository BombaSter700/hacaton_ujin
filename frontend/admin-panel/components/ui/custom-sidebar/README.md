# Custom Sidebar Components

Это **кастомная копия** оригинальных sidebar компонентов из `shadcn-vue`.

## ⚠️ Важно

**НЕ обновляйте эту папку через shadcn-vue CLI!**

Эта папка содержит кастомизированные компоненты, которые не должны перезаписываться при обновлении UI библиотеки.

## Отличия от оригинала

### `index.ts` - строка 51:

```typescript
// Оригинал (components/ui/sidebar/):
lg: "h-12 text-sm group-data-[collapsible=icon]:p-0!"

// Custom (components/ui/custom-sidebar/):
lg: "h-12 text-sm group-data-[collapsible=icon]:p-0! group-data-[collapsible=icon]:h-12!"
```

**Причина:**

- Сохраняет высоту `h-12` при сворачивании sidebar
- Предотвращает "прыгание" высоты header
- Критично для блока с логотипом компании

## Использование

### В компонентах приложения:

```vue
<script setup>
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/custom-sidebar'
</script>
```

### НЕ используйте:

```vue
// ❌ НЕ ДЕЛАЙТЕ ТАК
import { Sidebar } from '@/components/ui/sidebar' // Оригинальный компонент
```

## Обновление компонентов

### Обновление оригинальных компонентов sidebar:

```bash
# Это безопасно - обновятся только оригинальные компоненты
npx shadcn-vue@latest add sidebar
```

### Обновление custom-sidebar:

1. **Обновите оригинальные компоненты** (см. выше)
2. **Вручную синхронизируйте изменения** из `sidebar/` в `custom-sidebar/`
3. **Сохраните кастомизацию** в `index.ts` (строка 51)
4. **Протестируйте** сворачивание/разворачивание sidebar

## Структура

```
components/ui/
├── sidebar/           ← Оригинальные компоненты (можно обновлять)
│   └── index.ts       ← НЕ содержит кастомизации
│
└── custom-sidebar/    ← КАСТОМНЫЕ компоненты (НЕ обновлять автоматически!)
    ├── README.md      ← Этот файл
    ├── index.ts       ← СОДЕРЖИТ кастомизации (строка 51)
    └── ...            ← Все остальные компоненты
```

## Зачем это нужно?

Без custom-sidebar при каждом обновлении shadcn-vue компонентов:

- ❌ Терялись бы кастомизации
- ❌ Снова "прыгала" бы высота header
- ❌ Нужно было бы каждый раз вручную патчить

С custom-sidebar:

- ✅ Кастомизации защищены
- ✅ Можно безопасно обновлять оригинальные компоненты
- ✅ Легко синхронизировать изменения вручную

## Файлы, использующие custom-sidebar

- `components/AppSidebar.vue`
- `components/AppHeader.vue`
- `components/UserMenu.vue`
- `components/NavMain.vue`
- `components/NavProjects.vue`
- Все страницы в `pages/`