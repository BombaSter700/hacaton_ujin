# Admin panel Programmisto

Nuxt 3 / Vue 3, Node.js 24. Панель доступна на /admin/.
Health: /admin/api/health.

## Что подключено к backend

- Вход по email/password и регистрация клиента.
- Восстановление входа после перезагрузки текущей вкладки через /auth/me.
- Автоматическая ротация токенов при 401, один refresh для параллельных запросов.
- Выход с отзывом серверной сессии.
- Мой профиль и редактирование имени, фамилии, телефона.
- Свои сессии и их отзыв, включая текущую.
- Список пользователей с серверной пагинацией для роли admin.
- Настройка описаний подключённых устройств и их сигналов в карточке устройства.
- Редактор сохранённых сценариев по показаниям и времени: условия, действия, включение и выключение.

Автоматическое выполнение сценариев пока не подключено. Инструкция:
[scenario-editor.md](../../docs/infrastructure/scenario-editor.md).

Учётная запись клиента создаётся публичной регистрацией. Администратора
этим способом создать нельзя. Проверка прав остаётся на backend.
Токены хранятся в sessionStorage текущей вкладки, не в SSR-состоянии.
Это не HttpOnly cookie: доступ к токенам имеет клиентский JavaScript.
Закрытие вкладки очищает локальное хранилище, но не отзывает серверную сессию;
для отзыва используйте выход или список сессий.

Корневой ClientOnly исключает серверный рендер персональных данных:
guard и восстановление сессии выполняются на клиенте.
Если auth временно недоступен, показывается ошибка; не требуется отключать
валидацию токенов или подставлять identity-заголовки.

## Что остаётся демонстрационным

Обзор и объекты используют помеченные демо-данные.
Устройства и подключения читаются из integration через общий KrakenD:

- /admin/integrations — фильтр UUID организации;
- /admin/devices — выбор объекта из API, автоматическая загрузка единственного объекта, фильтр помещения;
- /admin/devices/{UUID} — метаданные, показания, история и отправка команд с подтверждением.

Пока доступны только администратору: права клиентов на объекты ещё не созданы.
Пустые списки не заменяются моками. В «Подключениях» доступен импорт девяти
эмуляторов по UUID организации и объекта. Показания обновляются каждые 10 секунд;
история хранит числовые и логические сигналы. Команды доступны для сигналов на запись.
Подробности и обновление VPS: [integration-gateway.md](../../docs/infrastructure/integration-gateway.md).

## Настройки API

Один общий адрес:
FRONTEND_API_URL -> NUXT_PUBLIC_API_URL -> runtimeConfig.public.apiUrl.

Auth и integration используют один HTTP-клиент и один параллельный refresh.
Клиент дополняет базовый адрес до /api/v1. Допустимы https://webzooms.ru,
https://webzooms.ru/api или https://webzooms.ru/api/v1.
Пустой адрес означает same-origin /api/v1.

Локальный Compose задаёт http://localhost:8080.
Для npm run dev укажите в frontend/admin-panel/.env:
NUXT_PUBLIC_API_URL=http://localhost:8080

Для VPS: FRONTEND_API_URL=https://webzooms.ru либо пусто.
FRONTEND_INTEGRATION_API_URL больше не используется.
Nginx должен сохранять /api/v1/... и Authorization.
Для другого origin требуется CORS на KrakenD.
Секреты JWT и IoT-платформ нельзя помещать в public runtimeConfig.

## Запуск

Из корня:
docker compose up -d --build --wait programmisto_integration programmisto_admin_panel programmisto_emulators
docker compose up -d --no-deps --force-recreate --wait programmisto_krakend

На VPS после обновления кода:
docker compose --env-file .env.prod -f docker-compose.prod.yml build programmisto_admin_panel
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --no-build --pull never --wait programmisto_admin_panel

Пересоздайте контейнер после изменения runtime env; изменение исходников
требует пересборки. В runtime находятся только файлы .output, пользователь node.

## Проверки

Из frontend/admin-panel: npm ci, npm test, npm run build.
Обычные тесты используют моки HTTP и не создают пользователей.
Опциональный auth-live.test.ts включается только через AUTH_SMOKE_URL,
FRONTEND_SMOKE_EMAIL и FRONTEND_SMOKE_PASSWORD.
Он создаёт локальный тестовый аккаунт с префиксом frontend-smoke-;
вызывающая тест процедура должна удалить только этот аккаунт после проверки.

Дальнейшая работа: подключить реальные IoT-показания после готовности backend.
Скрипт setup-module-links.sh в запуске и сборке не используется.
