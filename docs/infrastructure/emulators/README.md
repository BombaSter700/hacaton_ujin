# Эмуляторы IoT: контракт для integration

Контейнер `programmisto_emulators` запускает девять независимых устройств.
Integration читает их HTTP API и отправляет команды. Это локальная симуляция:
публикации Ujin работают в dry-run; записи в Redis/ClickHouse пока нет.

## Запуск и доступ

Из корня репозитория:

```powershell
docker compose up -d --build --wait
curl.exe --fail http://localhost:8098/health
```

Из integration используйте `http://programmisto_emulators:<порт>`, с хоста —
`http://localhost:<порт>`. Токены не нужны. API не имеет аутентификации,
опубликованные порты привязаны к localhost хоста.

Состав устройств, серийные номера и порты задаются в
[`fleet.json`](../../../backend/emulators/fleet.json). Для применения изменений
пересоберите контейнер. Корневой `.env`: `EMULATOR_INTERVAL=1` — пауза между
шагами в секундах. Каждый шаг равен условной секунде модели. Состояние находится
в памяти и сбрасывается при рестарте. При завершении одного процесса supervisor
завершает весь флот с ошибкой для перезапуска контейнера.

| Устройство | family | serial | Порт |
| --- | --- | --- | --- |
| Термостат | `thermostat` | `local-thermostat-001` | 8099 |
| Протечка | `leak` | `local-leak-001` | 8100 |
| Хаб датчиков | `hub` | `local-hub-001` | 8101 |
| Электросчётчик | `counter` | `local-counter-001` | 8102 |
| Свет | `light` | `local-light-001` | 8103 |
| Вентиляция | `ventilation` | `local-ventilation-001` | 8104 |
| Пожарный датчик | `fire` | `local-fire-001` | 8105 |
| Шлагбаум | `barrier` | `local-barrier-001` | 8106 |
| Лифт | `elevator` | `local-elevator-001` | 8107 |

## HTTP API

| Метод и путь | Результат |
| --- | --- |
| `GET :8098/health` или `/devices` | `{"status":"healthy","devices":[...]}`; HTTP 200, если все устройства отвечают, иначе 503 |
| `GET :<порт>/state` | Объект `имя сигнала → значение`, полный снимок |
| `GET :<порт>/declaration` | Описания сигналов, `management`, `kind`, единицы, диапазоны и `layout` |
| `POST :<порт>/command` | Форма `signal=имя&value=значение` |
| `POST :<порт>/` | Команды в JSON-обёртке `recv` |
| `GET :<порт>/` | Веб-панель |

```powershell
curl.exe --fail http://localhost:8099/state
curl.exe --fail http://localhost:8099/declaration
curl.exe --fail -X POST http://localhost:8099/command -d "signal=target_temp&value=25"
curl.exe --fail -X POST http://localhost:8103/command -d "signal=lamp&value=1"
curl.exe --fail -X POST http://localhost:8106/command -d "signal=open_cmd&value=1"
curl.exe --fail -X POST http://localhost:8107/command -d "signal=call_requested&value=3"
```

POST JSON на корень порта устройства, `Content-Type: application/json`:

```json
{"recv":[{"command":"management","id":"local-light-001","lamp":1,"brightness":60}]}
```

В JSON передавайте числа числами. Форма `/command` сама преобразует числовые
строки. **Устройство выбирается портом; `id` сейчас не проверяется.**
Ответ `{"error":0}` означает обработку запроса, а не завершение действия.
При исключении может прийти HTTP 200 с `{"error":2,"message":"..."}`.
Неизвестные и недоступные для записи сигналы игнорируются, тоже с `error:0`.
Проверяйте декларацию, права, диапазон и повторно читайте состояние.
Общей проверки диапазонов на стороне эмулятора нет. Служебный `/shutdown`
не используйте в integration: он завершает устройство.

## Поля устройств

`r` — показание; `rw` — чтение и команда; `w` — действие. `/state` содержит
также `w`-поля, но они не являются подтверждением выполнения команды.
У всех устройств есть `fw`: строка `emul-1.0`. Ниже — начальные значения моделей;
в работающем стенде они меняются. JSON-примеры также показаны на старте модели.

### Термостат (`thermostat`, :8099)

`model=emul_thermostat`

| signal | management | value | description |
| --- | --- | --- | --- |
| `temperature` | `r` | `20.0` | Температура; °C |
| `target_temp` | `rw` | `22.0` | Цель; °C; 5..35 |
| `mode` | `rw` | `3` | Режим; 0=выкл, 1=нагрев, 2=охлаждение, 3=авто |
| `output` | `r` | `0` | Нагрев/охлаждение; 0=нет, 1=нагрев, 2=охлаждение |
| `humidity` | `r` | `45` | Влажность; % |
| `fault` | `r` | `0` | Авария датчика; 0=нет, 1=нет данных |

```json
{"fw":"emul-1.0","temperature":20.0,"target_temp":22.0,"mode":3,"output":0,"humidity":45,"fault":0}
```

### Датчик протечки (`leak`, :8100)

`model=emul_leak_sensor`

| signal | management | value | description |
| --- | --- | --- | --- |
| `leak` | `r` | `0` | Протечка; 0=нет, 1=протечка |
| `battery` | `r` | `100` | Батарея; %; 0..100 |
| `tamper` | `r` | `0` | Вскрытие; 0=закрыт, 1=вскрыт |
| `self_test` | `w` | `0` | Самотест |

```json
{"fw":"emul-1.0","leak":0,"battery":100,"tamper":0,"self_test":0}
```

### Хаб протечки (`hub`, :8101)

`model=emul_leak_hub`

| signal | management | value | description |
| --- | --- | --- | --- |
| `leak` | `r` | `0` | Протечка (агрегат); 0=нет, 1=протечка |
| `leak_sensors` | `r` | `"0"` | Датчики (битовая маска) |
| `sensors_online` | `r` | `3` | Датчиков онлайн; 0..3 |
| `sensors_total` | `r` | `3` | Датчиков всего |
| `mute` | `rw` | `0` | Заглушить сирену |
| `siren` | `r` | `0` | Сирена; 0=выкл, 1=звучит |

```json
{"fw":"emul-1.0","leak":0,"leak_sensors":"0","sensors_online":3,"sensors_total":3,"mute":0,"siren":0}
```

### Счётчик: Электроэнергия (`counter`, :8102)

`model=emul_counter`

| signal | management | value | description |
| --- | --- | --- | --- |
| `total` | `r` | `1000.0` | Показание, кВт·ч; кВт·ч |
| `kvh_t1` | `r` | `400.0` | Тариф 1 (пик); кВт·ч |
| `kvh_t2` | `r` | `250.0` | Тариф 2 (ночь); кВт·ч |
| `power_w` | `r` | `350.0` | Мощность сейчас; Вт |
| `voltage` | `r` | `231.0` | Напряжение; В |
| `battery` | `r` | `98` | Батарея; % |
| `online` | `r` | `1` | Связь; 0=нет, 1=есть |
| `report_period` | `rw` | `60` | Период отчёта, с; с; 10..3600 |
| `load_relay` | `rw` | `1` | Реле нагрузки; 0=отключено, 1=включено |

```json
{"fw":"emul-1.0","total":1000.0,"kvh_t1":400.0,"kvh_t2":250.0,"power_w":350.0,"voltage":231.0,"battery":98,"online":1,"report_period":60,"load_relay":1}
```

### Светильник (`light`, :8103)

`model=emul_light`

| signal | management | value | description |
| --- | --- | --- | --- |
| `lamp` | `rw` | `0` | Свет; 0=выкл, 1=вкл |
| `brightness` | `rw` | `100` | Яркость; %; 1..100 |
| `power_w` | `r` | `0.0` | Мощность; Вт |
| `energy_kwh` | `r` | `0.0` | Энергия; кВт·ч |
| `offline_timeout` | `rw` | `0` | Авто-выкл через, с (0=выкл); с; 0..3600 |

```json
{"fw":"emul-1.0","lamp":0,"brightness":100,"power_w":0.0,"energy_kwh":0.0,"offline_timeout":0}
```

### Вентиляция (`ventilation`, :8104)

`model=emul_ventilation`

| signal | management | value | description |
| --- | --- | --- | --- |
| `supply_temp` | `r` | `21.0` | Температура притока; °C |
| `pm25` | `r` | `12.0` | PM2.5 на входе; мкг/м³ |
| `co2` | `r` | `420.0` | CO2 в помещении; ppm |
| `fan_speed` | `rw` | `1` | Скорость вентилятора; 0..6 |
| `mode` | `rw` | `1` | Режим; 0=выкл, 1=авто, 2=ручной |
| `co2_target` | `rw` | `800` | Целевой CO2; ppm; 400..1400 |
| `heat_pct` | `r` | `30` | Нагрев; % |

```json
{"fw":"emul-1.0","supply_temp":21.0,"pm25":12.0,"co2":420.0,"fan_speed":1,"mode":1,"co2_target":800,"heat_pct":30}
```

### Пожарный датчик (`fire`, :8105)

`model=emul_fire_detector`

| signal | management | value | description |
| --- | --- | --- | --- |
| `smoke` | `r` | `5` | Задымлённость; % |
| `alarm` | `r` | `0` | Пожар; 0=нет, 1=ЕСТЬ |
| `duty` | `r` | `1` | Дежурный режим; 0=нет, 1=есть |
| `tamper` | `r` | `0` | Вскрытие корпуса; 0=нет, 1=есть |
| `battery` | `r` | `100` | Батарея; % |
| `fault` | `r` | `0` | Неисправность; 0=нет, 1=есть |
| `threshold` | `rw` | `60` | Порог срабатывания; %; 10..95 |
| `self_test` | `w` | `0` | Самотест |

```json
{"fw":"emul-1.0","smoke":5,"alarm":0,"duty":1,"tamper":0,"battery":100,"fault":0,"threshold":60,"self_test":0}
```

### Шлагбаум (`barrier`, :8106)

`model=emul_barrier`

| signal | management | value | description |
| --- | --- | --- | --- |
| `open_cmd` | `rw` | `0` | Открыть |
| `close_cmd` | `w` | `0` | Закрыть |
| `hold_time` | `rw` | `10` | Держать открытым, c; c; 0..300 |
| `state` | `r` | `0` | Состояние стрелы; 0=закрыто, 1=открывается, 2=открыто, 3=закрывается, 4=удержание |
| `obstacle` | `r` | `0` | Предмет под стрелой; 0=нет, 1=есть |
| `alarm` | `r` | `0` | Авария; 0=нет, 1=застревание |
| `cycles` | `r` | `0` | Циклов открытий |

```json
{"fw":"emul-1.0","open_cmd":0,"close_cmd":0,"hold_time":10,"state":0,"obstacle":0,"alarm":0,"cycles":0}
```

### Лифт (`elevator`, :8107)

`model=emul_elevator`

| signal | management | value | description |
| --- | --- | --- | --- |
| `call_requested` | `w` | `0` | Вызвать (этаж); 0=нет |
| `floor_current` | `r` | `1` | Текущий этаж; 1..5 |
| `floor_destination` | `r` | `0` | Этаж назначения; 0..5 |
| `direction` | `r` | `0` | Направление; 0=стоит, 1=вверх, 2=вниз |
| `speed` | `r` | `0.0` | Скорость; м/с |
| `door` | `r` | `0` | Двери; 0=закрыты, 1=открыты |
| `floor_changed` | `r` | `0` | Событие: этаж пройден |
| `emergency` | `r` | `0` | Авария; 0=норма, 1=авария |
| `emergency_btn` | `w` | `0` | Кнопка аварии |
| `floors_total` | `r` | `5` | Этажей в шахте |

```json
{"fw":"emul-1.0","call_requested":0,"floor_current":1,"floor_destination":0,"direction":0,"speed":0.0,"door":0,"floor_changed":0,"emergency":0,"emergency_btn":0,"floors_total":5}
```


## Особенности поведения

- Термостат: `mode` 0 — выкл, 1 — нагрев, 2 — охлаждение, 3 — авто;
  `output` 0 — нет воздействия, 1 — нагрев, 2 — охлаждение.
- Протечка: `self_test=1` сбрасывает внутреннее состояние в «сухо» на следующем
  шаге. `leak` и `tamper` нельзя менять командой.
- Хаб: `leak_sensors` — строка `"010"` по символу на датчик. `mute=1`
  отключает сирену, но не сбрасывает протечку.
- Счётчик флота — электрический; значения синтетические, не для начислений.
  `report_period` сейчас не меняет период публикации. Одиночный CLI поддерживает
  воду/тепло через `--resource`, но флот эти параметры пока не передаёт.
- Свет: сначала задайте `offline_timeout`, затем `lamp=1`, чтобы активировать таймер.
- Вентиляция: `mode` 0 — выкл, 1 — авто, 2 — ручной. В авто модель сама меняет
  `fan_speed`; для ручной скорости сначала установите `mode=2`.
- Пожарный датчик: `alarm=1` при достижении `threshold`, `duty` становится 0.
  Самотест пишет результат только в лог, дым постепенно уменьшается.
- Шлагбаум: `state` 0 — закрыт, 1 — открывается, 2 — открыт, 3 — закрывается,
  4 — удержание. `open_cmd=1` сбрасывается в 0; проверяйте выполнение по `state`.
- Лифт: этажи 1–5, одна текущая цель. `direction` 0 — стоит, 1 — вверх,
  2 — вниз; `door` 0 — закрыты, 1 — открыты; `floor_destination=0` — нет цели.
  Каждый вызов `emergency_btn` переключает аварию, поэтому retry может её снять.
  `floor_changed` хранит последний пройденный этаж, не очередь событий.

Демо-инъекции протечки, дыма, препятствия и неисправности доступны методами Python
(`set_wet`, `set_smoke`, `set_obstacle`, `set_fault`); HTTP-ручек для них пока нет.

## Нормализация в integration

1. Получите экземпляры на `:8098/devices`, декларации по портам, затем опрашивайте
   `/state` с тайм-аутом, например раз в секунду. Это снимок: короткие события
   между опросами можно пропустить.
2. Сопоставьте строковый `serial` с UUID устройства, организацией и зданием из
   PostgreSQL. В `/state` идентификаторов tenant/устройства нет.
3. Числа и 0/1 направляйте в телеметрию, переходы аварий/доступности — в события.
   Строки `fw`, `leak_sensors` нельзя напрямую записать в `telemetry.value` Float64.
4. Снимок не содержит `event_id`, времени измерения и качества. Их формирование
   нужно согласовать в integration. Время опроса — время наблюдения, не известное
   время измерения датчика. Повторная доставка одной записи сохраняет её ID.
5. При сетевой ошибке отмечайте недоступность и время последнего успешного опроса;
   не выдавайте последнее известное показание за свежее.

При старте публикуются все `r/rw`-сигналы, дальше — изменившиеся. Сейчас это
только строки `JOURNAL` в stdout, например:

```json
{"call":"publish","path":"/api/import_device/update-device-signal/","data":[{"sn":"local-thermostat-001","s":"temperature","v":21.8,"c":"emul_thermostat"}]}
```

`sn` — serial, `s` — сигнал, `v` — значение, `c` — модель. Записи команд имеют
иной формат и не содержат serial; stdout нескольких процессов может смешиваться.
Не используйте его как транспорт integration.
В Ujin-публикации `wire_value` заменяет числовой ноль на `0.001` для большинства
сигналов. В `/state` остаётся настоящий `0`: эти форматы нужно различать.

Код: [`fleet.py`](../../../backend/emulators/fleet.py),
[`core.py`](../../../backend/emulators/core.py),
[`devices/`](../../../backend/emulators/devices/).
Общая инфраструктура: [README](../README.md).
