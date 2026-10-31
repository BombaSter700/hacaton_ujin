# API-шлюз Programmisto

KrakenD 2.13.11 запускается из `krakend.tmpl` через Flexible Configuration.
Go-шаблон `templates/auth_story.tmpl` содержит текущие маршруты auth,
пользователей и сессий. Итоговый JSON собирается в памяти при запуске.
Отдельный JSON-конфиг не хранится.
Адрес с компьютера: `http://127.0.0.1:8080` (переменная Compose `KRAKEND_PORT`).

## Маршруты

| Метод | Путь на шлюзе | Назначение |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Регистрация клиента |
| POST | `/api/v1/auth/login` | Получение access и refresh токенов |
| POST | `/api/v1/auth/refresh` | Ротация refresh токена |
| POST | `/api/v1/auth/logout` | Завершение текущей сессии |
| GET | `/api/v1/auth/me` | Текущий пользователь |
| GET | `/api/v1/users/` | Список пользователей для администратора; `skip`, `limit` |
| PATCH | `/api/v1/users/me` | Изменение своего профиля |
| GET | `/api/v1/sessions/` | Свои активные сессии |
| DELETE | `/api/v1/sessions/{session_id}` | Отзыв своей сессии |
| GET | `/api/auth/health/live` | Liveness auth (`/health/live`) |
| GET | `/api/auth/health/ready` | Readiness auth с проверкой БД (`/health/ready`) |
| GET | `/__health` | Встроенный health самого KrakenD |

Backend: `http://programmisto_auth:8000` в сети Docker. Пути `/api/v1/...`
совпадают с API сервиса, включая завершающий `/` у списков.
Auth нужно запустить отдельно: локально `docker compose up -d programmisto_auth`.
Health шлюза не означает доступность auth; проверяйте также readiness auth.

## Авторизация и передача данных

Клиент передаёт `Authorization: Bearer <access_token>`. Auth проверяет подпись,
срок действия, активность пользователя и сессии, права администратора и владение
сессией. На шлюзе нет копии JWT-секрета и JWK. Cookie и `X-Auth-*` не передаются.
Тело запроса передаётся в auth, ответы идут в режиме `no-op`: сохраняются тело,
HTTP-статус и заголовки, включая ошибки 401/403/422 и пустой ответ 204 logout.
Ответы пользователей, токены и health не кешируются шлюзом.

CORS настроен для `http://localhost:3000` и `http://localhost:3001`, без cookies.
Для другого frontend задайте `CORS_ALLOW_ORIGINS` как JSON-массив строк в .env
(например, `CORS_ALLOW_ORIGINS=["https://app.example.com"]`) и пересоздайте шлюз.
Переменная `CORS_ORIGINS` auth эту настройку не меняет.
В Compose включены `FC_ENABLE=1` и `FC_TEMPLATES=/etc/krakend/templates`;
адрес backend задаётся `AUTH_SERVICE_URL` (по умолчанию Docker-адрес auth).
Для нового сервиса добавьте его файл в `templates/` и вызов `template` в массив
`endpoints` корневого шаблона, разделяя непустые блоки запятой.
Таймаут запроса к backend — 10 секунд. curl и Python-клиенты разрешены.

Integration ещё не имеет готового API: маршруты для него появятся после
согласования контракта IoT. Управление эмуляторами, Swagger и метрики auth через
шлюз сейчас не опубликованы. Swagger при DEBUG доступен напрямую на порту 8001.
Старые маршруты групп, учебных журналов, сброса пароля и cookie-CSRF удалены.

## Проверка и применение

```bash
docker compose run --rm --no-deps programmisto_krakend check -c /etc/krakend/krakend.tmpl
docker compose up -d --no-deps --force-recreate programmisto_krakend
curl http://127.0.0.1:8080/__health
curl http://127.0.0.1:8080/api/auth/health/ready
curl -H 'Authorization: Bearer <access_token>' http://127.0.0.1:8080/api/v1/auth/me
```
