#!/bin/bash
# Скрипт для создания символических ссылок модулей в admin-panel/pages/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PAGES_DIR="$PROJECT_ROOT/pages"
MODULES_DIR="$PROJECT_ROOT/modules"

mkdir -p "$PAGES_DIR"

echo "🔗 Creating symbolic links for admin panel module pages..."

# Удаляем существующие ссылки (если есть)
find "$PAGES_DIR" -type l -delete 2>/dev/null || true

# Создаем ссылки для каждого модуля
for module_dir in "$MODULES_DIR"/*/; do
  module_name=$(basename "$module_dir")
  
  # Пропускаем шаблон (скрытая папка) и README
  if [[ "$module_name" == ".template" ]] || [[ "$module_name" == "README.md" ]] || [[ "$module_name" == "ARCHITECTURE.md" ]] || [[ "$module_name" == "MIGRATION.md" ]] || [[ "$module_name" == "SETTINGS.md" ]]; then
    continue
  fi
  
  module_pages_dir="$module_dir/pages"
  
  if [ -d "$module_pages_dir" ]; then
    # Рекурсивно находим все .vue файлы в pages директории модуля
    find "$module_pages_dir" -type f -name "*.vue" | while read -r page; do
      # Получаем относительный путь от module_pages_dir
      rel_path="${page#$module_pages_dir/}"
      rel_dir=$(dirname "$rel_path")
      page_name=$(basename "$page")
      
      # Определяем путь для ссылки
      if [[ "$module_name" == "core" ]]; then
        # Core модуль: некоторые страницы создаем в корне pages/
        if [[ "$rel_path" =~ ^(index|login|register|forgot-password)\.vue$ ]]; then
          # Файлы в корне
          link_path="$PAGES_DIR/$page_name"
          link_dir="$PAGES_DIR"
        elif [[ "$rel_dir" == "." ]] && [[ "$page_name" =~ ^(dashboard|profile|notifications|settings)$ ]]; then
          # Директории в корне (если это директория с index.vue)
          link_path="$PAGES_DIR/$page_name"
          link_dir="$PAGES_DIR"
        elif [[ "$rel_dir" == "." ]]; then
          # Остальные файлы в поддиректории core/
          link_path="$PAGES_DIR/core/$page_name"
          link_dir=$(dirname "$link_path")
        else
          # Вложенные директории
          link_path="$PAGES_DIR/$rel_path"
          link_dir=$(dirname "$link_path")
        fi
      elif [[ "$module_name" == "feed" ]] && [[ "$rel_path" == "news/index.vue" ]] || [[ "$rel_path" == "news.vue" ]]; then
        # Feed модуль: news создаем в корне pages/
        if [[ "$rel_path" == "news/index.vue" ]]; then
          link_path="$PAGES_DIR/news/index.vue"
        else
          link_path="$PAGES_DIR/news.vue"
        fi
        link_dir=$(dirname "$link_path")
      else
        # Остальные модули: помещаем все страницы в подпапку с именем модуля
        # Это предотвращает конфликты имён (index.vue, create.vue, [id]/...) и
        # гарантирует корректную генерацию динамических подстраниц, например
        # pages/<module>/[id]/edit.vue
        # Если модуль уже содержит вложенную директорию, сохраняем её внутри папки модуля
        link_path="$PAGES_DIR/$module_name/$rel_path"
        link_dir=$(dirname "$link_path")
      fi
      
      # Создаем директорию если нужно
      mkdir -p "$link_dir"
      
      # Создаем символическую ссылку
      # Используем относительный путь для совместимости с macOS и Linux
      # Пробуем python3 (macOS/Linux), затем node (гарантирован в Docker)
      relative_path=$(python3 -c "import os; print(os.path.relpath('$page', '$link_dir'))" 2>/dev/null || node -e "console.log(require('path').relative('$link_dir', '$page'))" 2>/dev/null)
      ln -sf "$relative_path" "$link_path"
      echo "✅ Linked: $link_path -> $relative_path"
    done
  else
    echo "⚠️  No pages directory found in module: $module_name"
  fi
done

# Удаляем пустые директории, которые могли остаться
find "$PAGES_DIR" -type d -empty -delete 2>/dev/null || true

echo "✨ Module links created successfully!"
