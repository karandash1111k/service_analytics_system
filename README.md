# Корпоративная система аналитики выездного сервиса и интеграций

Desktop-приложение уровня enterprise-дипломного проекта: **слой данных (MySQL + SQLAlchemy ORM)**, **репозитории**, **сервисная бизнес-логика**, **ETL pipeline**, **адаптеры интеграций** (Bitrix24 / 1С / Excel), **аналитический слой KPI и SLA**, **отчёты** (Excel / PDF), **GUI на PyQt6** с графиками **matplotlib**.

Стек фиксирован согласно заданию:

- Python **3.12+** (совместимо с более новыми patch/minor релизами интерпретатора).
- **SQLAlchemy 2.x**, **PyMySQL**, **MySQL**.
- **PyQt6**, **matplotlib**, **pandas**, **openpyxl**, **requests**, **python-dotenv**.

---

## Быстрый старт

### 1. Создайте базу MySQL

```sql
CREATE DATABASE service_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'svc_user'@'%' IDENTIFIED BY 'StrongPassword!';
GRANT ALL PRIVILEGES ON service_analytics.* TO 'svc_user'@'%';
FLUSH PRIVILEGES;
```

Для локальной разработки можно использовать пользователя `root` и пустой пароль — см. `.env.example`.

### 2. Настройте `.env`

Скопируйте `.env.example` → `.env` и заполните параметры:

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `APP_LOG_LEVEL` (`INFO` по умолчанию)

Пароль и логин автоматически **URL-кодируются** в строке подключения (`urllib.parse.quote_plus`), чтобы допускать спецсимволы.

### 3. Установите зависимости

```bash
cd service_analytics_system
python -m pip install -r requirements.txt
```

### 4. Заполните тестовыми данными

Скрипт создаёт таблицы (если их ещё нет), **≥20 клиентов**, **10 инженеров**, **58 заявок**, ремонты, запчасти, связи и снимок KPI:

```bash
python scripts/seed_data.py
```

Повторный прогон без очистки БД добавит ещё один объём данных — для чистого стенда выполните `DROP DATABASE` / пересоздайте схему.

### 5. Запустите приложение

```bash
python main.py
```

---

## Структура проекта

```text
service_analytics_system/
├── main.py                  # Точка входа GUI + bootstrap БД
├── config/                  # Конфигурация (.env → Settings)
├── database/                # Engine, sessionmaker, создание схемы
├── models/                  # Declarative ORM-модели и связи
├── repositories/            # Доступ к данным (Repository Pattern)
├── services/                # Бизнес-логика и оркестрация
├── analytics/               # Чистые расчёты KPI / SLA / прогноз
├── etl/                     # Extract → Transform → Load
├── integrations/
│   ├── bitrix24/
│   ├── onec/
│   └── excel/
├── reports/                 # Генераторы Excel / PDF
├── ui/                      # PyQt6 слой представления
├── utils/                   # Логирование, константы
├── scripts/
│   └── seed_data.py         # Демонстрационное наполнение
├── tests/                   # Юнит-тесты (SLA и др.)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Архитектура

### Слои

| Слой | Назначение |
|------|------------|
| **UI (PyQt6)** | Навигация, таблицы, диалоги ошибок, matplotlib-панели |
| **Services** | Правила работы с заявками/ремонтами, KPI snapshot, отчёты |
| **Repositories** | Инкапсуляция запросов SQLAlchemy |
| **Models** | Декларативная схема MySQL + relationships |
| **Analytics** | Чистые функции агрегации без побочных эффектов |
| **ETL** | Унифицированный поток загрузки из разных источников |
| **Integrations** | Адаптеры внешних систем + журналирование синхронизаций |

### Основные связи ORM

- `Client` **1:N** `ServiceOrder`
- `Engineer` **1:N** `ServiceOrder`
- `ServiceOrder` **1:N** `Repair`
- `Repair` **M:N** `SparePart` через таблицу `repair_parts` (+ `quantity_used`)
- `Engineer` **1:N** `KPIMetric`

### ETL

`etl/extractor.py` извлекает сырые записи (Bitrix mock REST JSON, 1С mock JSON/CSV, Excel через pandas).  
`etl/transformer.py` нормализует статусы, парсит даты, валидирует поля.  
`etl/loader.py` сохраняет данные через репозитории с учётом транзакций (`session_scope`).  
`etl/pipeline.py` составляет отчётность по количеству обработанных строк и пишет записи в `integration_logs`.

### Интеграции

- **Bitrix24**: `integrations/bitrix24/bitrix_client.py` — по умолчанию mock JSON; опционально `BITRIX_WEBHOOK_URL` для реального `requests.get`.
- **1С**: `integrations/onec/mock_repairs.json` + клиент с CSV fallback.
- **Excel**: импорт через `integrations/excel/excel_importer.py`; экспорт аналитики через `excel_exporter.py` / `ReportingService`.

Требуемые **колонки Excel для импорта заявок** (заголовки первой строки):

| Колонка | Описание |
|---------|-----------|
| `external_id` | Внешний идентификатор |
| `title` | Заголовок |
| `description` | Описание |
| `priority` | `low` / `medium` / `high` / `critical` |
| `status` | Статус обращения |
| `client_name` | ФИО / название |
| `client_phone` | Телефон |
| `client_email` | Email |

Пример генерации файла:

```bash
python scripts/create_sample_orders_workbook.py
```

### KPI и SLA

Реализованы показатели:

- среднее время разрешения заявки и средняя длительность ремонта;
- доля SLA-соблюдений и просрочек (настраиваемые цели по приоритетам — `utils/constants.py`);
- загрузка инженеров (индекс нагрузки и распределение заявок);
- успешность ремонтов;
- простой прогноз объёма заявок (`analytics/forecast_module.py`, скользящее среднее).

`snapshot_engineer_kpis()` сохраняет метрики в таблицу `kpi_metrics`.

### Отчёты

- **Excel**: несколько листов KPI / SLA / помесячные ряды / загрузка инженеров (`reports/excel_report.py`).
- **PDF**: многостраничный документ matplotlib (`reports/pdf_report.py`): текстовый executive summary + графики.

### Надёжность

- Централизованное логирование (`utils/logger.py`).
- GUI операции обёрнуты в `try/except` с `QMessageBox`.
- Транзакции через `session_scope()` с `rollback` при ошибках.

---

## Тесты

```bash
python -m pytest tests -q
```

Добавлены минимальные модульные проверки SLA (`tests/test_sla_calculator.py`).
