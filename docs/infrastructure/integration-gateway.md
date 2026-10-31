# IoT в административной панели

Доступ: http://localhost:3000/admin/ локально, https://webzooms.ru/admin/ на VPS.
Нужен пользователь с ролью admin. Клиенты пока не получают доступ к IoT: разграничение по объектам ещё не реализовано.

## Работа в интерфейсе

1. Откройте «Подключения». Укажите UUID организации и UUID объекта.
2. Нажмите «Синхронизировать эмуляторы». Создаётся подключение emulator и импортируются девять устройств с описаниями сигналов. Повторный импорт обновляет описания. Перенос уже импортированного парка на другой объект запрещён.
3. Откройте «Устройства». Если объект один, его устройства загрузятся автоматически. Если объектов несколько, выберите объект из списка. UUID можно указать вручную.
4. В карточке показания обновляются каждые 10 секунд. Показываются время получения, качество и статус. При ошибке обновления остаются последние показания с предупреждением.
5. Для доступного на запись сигнала введите значение и отправьте команду. Ответ различает подтверждённое выполнение, ошибку и таймаут подтверждения. После команды показания запрашиваются повторно.
6. Выберите сигнал для истории. Отображаются последние 100 числовых/логических показаний из ClickHouse. Строковые состояния не записываются в числовую историю.

Организация и объект задаются UUID; автоматического создания справочников организаций и объектов пока нет. Экраны общего обзора и объектов всё ещё содержат демонстрационные данные.

## Маршруты KrakenD

| Метод | Путь | Назначение |
|---|---|---|
| GET | /api/v1/integrations/?organization_id=UUID | Подключения организации |
| GET | /api/v1/integrations/{id} | Подключение |
| POST | /api/v1/integrations/emulators/sync | Импорт парка: organization_id, object_id |
| GET | /api/v1/devices/?object_id=UUID&room_id=UUID | Устройства объекта; room_id необязателен |
| GET | /api/v1/devices/objects | Объекты с зарегистрированными устройствами и их количество; только admin |
| GET | /api/v1/devices/{id} | Описание устройства и сигналов |
| GET | /api/v1/devices/{id}/state | Последнее состояние |
| GET | /api/v1/devices/{id}/history?signal_name=temperature&limit=100 | История; limit от 1 до 1000 |
| POST | /api/v1/commands/{id}/send | Команда: signal_id, value, idempotency_key |
| GET | /api/integration/health/live | Проверка процесса |
| GET | /api/integration/health/ready | Проверка готовности |

Все предметные маршруты проверяют Bearer-сессию через auth и требуют admin.
Заголовки x-auth-role/x-auth-user-id не используются для авторизации.
Команды получают UUID сигнала из карточки, а не произвольный адрес устройства.
Создание/изменение произвольных подключений и удаление устройств через шлюз не опубликованы.
Настройка описаний существующих устройств и CRUD сценариев опубликованы отдельно:
[контракт и инструкция редактора](scenario-editor.md). Автоматического исполнения сценариев пока нет.

## Данные и запуск

PostgreSQL хранит описания и журнал команд, Redis — последнее состояние (TTL 24 часа),
ClickHouse — числовую историю и события. Опрос активных устройств выполняется раз в 10 секунд.
organization_id в новых событиях берётся из подключения.

Compose передаёт интегратору AUTH_SERVICE_URL, REDIS_URL с паролем и CLICKHOUSE_*.
FRONTEND_API_URL задаёт единый адрес API; на VPS оставьте пустым для запросов к тому же домену.
Отдельный FRONTEND_INTEGRATION_API_URL не используется.

Миграция 002_iot_runtime применяется entrypoint автоматически. Она добавляет base_url,
целочисленный actor_user_id для auth, индекс идемпотентности на пользователя и статус ERROR.
Старые UUID user_id и записи команд сохраняются. Автоматического обратного преобразования нет;
для отката схемы используйте резервную копию БД.

Локально:

```bash
docker compose up -d --build --wait --wait-timeout 180 programmisto_integration programmisto_admin_panel programmisto_emulators
docker compose up -d --no-deps --force-recreate --wait programmisto_krakend
python backend/integration/tests/smoke_gateway.py
```

Последняя команда — только локальный тест: временный администратор и метаданные, изменение/восстановление
уставки термостата. Тест удаляет аккаунт и метаданные; его телеметрия остаётся до штатного TTL.

## Обновление VPS

Сначала закоммитьте и отправьте изменения в репозиторий. На VPS:

```bash
cd /srv/programmisto
git pull --ff-only
mkdir -p backups
chmod 700 backups
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T programmisto_postgres sh -c 'pg_dump -U "$POSTGRES_USER" "${INTEGRATION_DB_NAME:-integration_db}"' > "backups/integration-$(date +%Y%m%d-%H%M%S).sql"
chmod 600 backups/*.sql
docker compose --env-file .env.prod -f docker-compose.prod.yml --parallel 1 build programmisto_integration programmisto_admin_panel programmisto_emulators
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build --pull never --wait --wait-timeout 180 programmisto_integration programmisto_admin_panel programmisto_emulators
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --no-build --pull never --force-recreate --wait programmisto_krakend
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:8080/api/integration/health/ready
```

Проверяйте успешное создание резервной копии перед запуском миграции. Не выполняйте down -v:
тома и существующие секреты сохраняются.

Если в Nginx остался прежний блок location ~ ^/api/v1/(integrations|devices|commands)(/|$)
с return 503, удалите только этот блок после обновления. Общий location /api/ должен вести
на 127.0.0.1:8080. Сохраните копию конфига; не переписывайте TLS-настройки Certbot.

```bash
nginx -t && systemctl reload nginx
```

После обновления войдите администратором, синхронизируйте эмуляторы и проверьте карточку термостата.
Порты backend остаются доступны только через localhost.

## Ограничения

Это тестовая инфраструктура: очередь аналитики находится в памяти и пока не гарантирует доставку
при отказе ClickHouse или аварийном завершении процесса. Реальные устройства Ujin и правила автоматизации
этим обновлением не подключаются. Для большого потока IoT нужны отдельные нагрузочные проверки.
