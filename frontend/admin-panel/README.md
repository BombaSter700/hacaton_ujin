# Admin panel Programmisto

Сейчас это запускаемый каркас Nuxt 3 / Vue 3. На /admin/ находится начальная
страница, на /admin/api/health — JSON healthcheck.
Вход, профиль, таблицы пользователей, устройства, телеметрия и команды ещё
не реализованы. API-клиента, хранилища токенов и route guards пока нет.

## Сборка и запуск

Добавлены production Dockerfile, npm lock-файл, healthcheck и сервис в Compose.
Удалены подключения отсутствующих модулей старого проекта.
Образ собирается на Node.js 24, запускает только .output от пользователя node.
UI-зависимости сохранены для дальнейшей разработки; готовых компонентов нет.
Vitest-конфиг пустой, тестов приложения пока нет.
Скрипт scripts/setup-module-links.sh не участвует в сборке и запуске.

Из корня проекта на VPS после обновления кода:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml build programmisto_admin_panel
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --no-build --pull never --wait --wait-timeout 120 programmisto_admin_panel
```

Панель: http://127.0.0.1:3000/admin/
Health: http://127.0.0.1:3000/admin/api/health
ADMIN_PANEL_PORT задаёт порт хоста, по умолчанию 3000, только localhost.
На VPS с 4 ГБ RAM собирайте сервисы последовательно.

Для доступа с компьютера:

```bash
ssh -N -L 3000:127.0.0.1:3000 -L 8080:127.0.0.1:8080 -L 8002:127.0.0.1:8002 root@185.39.206.41
```

Открыть http://localhost:3000/admin/.

## Настройки API

FRONTEND_API_URL -> NUXT_PUBLIC_API_URL -> runtimeConfig.public.apiUrl.
По умолчанию http://localhost:8080 (KrakenD, маршруты auth).

FRONTEND_INTEGRATION_API_URL -> NUXT_PUBLIC_INTEGRATION_API_URL ->
runtimeConfig.public.integrationApiUrl.
По умолчанию http://localhost:8002 (integration напрямую).

Это публичные адреса для браузера, а не Docker DNS-имена.
При доступе через домен нужны доступные браузеру HTTPS API и CORS
либо same-origin reverse proxy. После изменения env пересоздайте контейнер.
Секреты JWT и IoT-платформ в public runtimeConfig передавать нельзя.
wsPort оставлен для совместимости конфигурации; WebSocket API пока нет.

## Дальнейшая разработка

Контракт: [BACKEND_API_FOR_FRONTEND.txt](../../BACKEND_API_FOR_FRONTEND.txt).
Начать с входа, refresh, профиля и списка сессий auth.
Integration пока имеет незавершённый контракт авторизации и команд.
Не отправляйте поддельные x-auth-* из браузера как постоянное решение.

Локально с Node.js 24: npm ci, затем npm run dev.
Production-сборка: npm run build. Запуск: npm start.
Документация: https://nuxt.com/docs/3.x/getting-started/deployment
