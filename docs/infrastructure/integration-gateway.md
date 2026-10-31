# Подключение integration к панели

Панель использует один API-адрес KrakenD: FRONTEND_API_URL.
Пути сохраняются: /api/v1/integrations/... и /api/v1/devices/...
Отдельный браузерный адрес integration больше не требуется.

## Опубликованные маршруты

- GET /api/v1/integrations/?organization_id=<UUID>
- GET /api/v1/integrations/{integration_id}
- GET /api/v1/devices/?object_id=<UUID>&room_id=<UUID>
- GET /api/v1/devices/{device_id}
- GET /api/integration/health/live
- GET /api/integration/health/ready

Передаётся Authorization: Bearer <access_token>, query-фильтры разрешены явно.
Режим no-op сохраняет статусы и тело ответа backend.
Шаблон: infra/krakend/templates/integration_story.tmpl.
INTEGRATION_SERVICE_URL по умолчанию http://programmisto_integration:8000.

## Доступ

Integration проверяет текущую сессию запросом GET /api/v1/auth/me к auth.
AUTH_SERVICE_URL по умолчанию http://programmisto_auth:8000.
AUTH_TIMEOUT_SECONDS по умолчанию 3 секунды.
При недоступности auth — 503, без обхода проверки.
x-auth-id/x-auth-role от клиента не являются авторизацией.
До реализации назначений на объекты доступ к IoT API разрешён только admin.
Client получает 403; отзыв сессии и изменение роли учитываются auth при запросе.

## Экраны

/admin/integrations — подключения по UUID организации.
/admin/devices — устройства по UUID объекта, необязательный фильтр помещения.
/admin/devices/{UUID} — метаданные и описание сигналов.

Пустая БД даёт пустые списки. Автоматический импорт 9 эмуляторов пока не сделан.
UUID нужно брать из реестра проекта; API списка организаций/объектов отсутствует.
Обзор и объекты в панели пока остаются демонстрационными.
Показания и история в DeviceResponse отсутствуют и не имитируются на фронте.

## Что пока не публикуется

POST/PATCH/DELETE подключений, PATCH устройства и отправка команд не добавлены
в шлюз. Типы и клиентские helpers для существующих backend-методов сохранены
для дальнейшей доработки, но UI их не вызывает.
Для команд остаются несовместимость integer user_id с UUID журнала, сигнатура
адаптера и неподтверждённое исполнение. Права на отдельные объекты тоже не готовы.
Нельзя выдавать HTTP 200 за подтверждённое управление устройством.

## Локальная проверка

Из корня:

```bash
docker compose up -d --build --wait programmisto_integration programmisto_admin_panel
docker compose up -d --no-deps --force-recreate --wait programmisto_krakend
```

Шаблоны не перечитываются автоматически при изменении файлов: шлюз нужно
перезапустить. Панель: http://localhost:3000/admin/.

## Обновление VPS

После коммита изменений и git pull:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml --parallel 1 build programmisto_integration programmisto_admin_panel
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build --pull never --wait --wait-timeout 180 programmisto_integration programmisto_admin_panel
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --no-build --pull never --force-recreate --wait programmisto_krakend
```

FRONTEND_API_URL=https://webzooms.ru либо пусто для same-origin.
Секреты и данные существующих томов менять не нужно.

В ранее установленном Nginx был блок:
location ~ ^/api/v1/(integrations|devices|commands)(/|$) { ... return 503 ... }

После обновления integration удалите ТОЛЬКО этот старый блок запрета:
общий location /api/ уже направляет запросы в KrakenD.
Не перезаписывайте весь конфиг домена: Certbot добавил туда TLS-настройки.
Сначала сохраните копию /etc/nginx/sites-available/webzooms.ru, затем:

```bash
nginx -t && systemctl reload nginx
```

Команды и записи останутся недоступны через шлюз (404/405), поскольку для них
не опубликованы маршруты. Порты backend по-прежнему привязаны к localhost.
Защитную проверку Bearer выполняет integration, а не клиент или Nginx.
