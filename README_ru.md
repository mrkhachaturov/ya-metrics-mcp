# ya-metrics-mcp

![License](https://img.shields.io/github/license/mrkhachaturov/ya-metrics-mcp)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastMCP](https://img.shields.io/badge/FastMCP-2.13%2B-green)

MCP-сервер для аналитики [Яндекс Метрики](https://metrika.yandex.ru/). Предоставляет 31 инструмент для вашего ИИ-ассистента — трафик, контент, демография, география, конверсии, e-commerce и иерархические отчёты drill-down.

Документация на английском — [здесь](README.md).

## Быстрый старт

### 1. Получите OAuth-токен

1. Перейдите на [oauth.yandex.ru/client/new](https://oauth.yandex.ru/client/new) и создайте новое приложение:
   - **Название** — любое
   - **Платформы** — выберите **Веб-сервисы**
   - **Redirect URI** — укажите `https://oauth.yandex.ru/verification_code`
   - **Доступ к данным** — добавьте `metrika:read` (обязательно); при необходимости добавьте:
     - `metrika:write` — создание и редактирование счётчиков
     - `metrika:expenses` — загрузка расходов на рекламу
     - `metrika:user_params` — загрузка параметров пользователей
     - `metrika:offline_data` — загрузка офлайн-конверсий

2. Нажмите **Создать приложение** и скопируйте **ClientID**.

3. Откройте в браузере ссылку (замените `<ClientID>` на ваше значение):
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=<ClientID>
   ```

4. Авторизуйтесь и скопируйте токен с открывшейся страницы.

### 2. Настройте IDE

Добавьте в конфигурацию MCP вашего Claude Desktop / Cursor:

```json
{
  "mcpServers": {
    "ya-metrics": {
      "command": "uvx",
      "args": ["ya-metrics-mcp"],
      "env": {
        "YANDEX_API_KEY": "ваш_oauth_токен"
      }
    }
  }
}
```

> **Запуск из исходников?** Используйте `uv run`:
> ```json
> {
>   "mcpServers": {
>     "ya-metrics": {
>       "command": "uv",
>       "args": ["run", "--directory", "/путь/к/ya-metrics-mcp", "ya-metrics-mcp"],
>       "env": { "YANDEX_API_KEY": "ваш_oauth_токен" }
>     }
>   }
> }
> ```

### 3. Начните работу

Спросите у ИИ-ассистента:
- **«Покажи мои счётчики в Метрике»** — начните здесь, чтобы найти ID счётчика
- **«Покажи визиты для счётчика 12345678 за последние 30 дней»**
- **«Какие основные источники трафика на моём сайте?»**
- **«Сравни мобильных и десктопных пользователей в этом месяце»**
- **«Покажи конверсии для целей 1 и 2»**
- **«Детализируй трафик по стране → городу»**
- **«Сравни сегменты органического и прямого трафика»**

## Инструменты

31 инструмент в 7 категориях:

### Аккаунт и счётчики
| Инструмент | Описание |
|------------|----------|
| `list_counters` | Список всех счётчиков на аккаунте (начните здесь) |
| `list_goals` | Список целей счётчика (вызовите перед `get_goals_conversion`) |
| `get_account_info` | Метаданные счётчика: название, сайт, часовой пояс, права |

### Трафик и источники
| Инструмент | Описание |
|------------|----------|
| `get_visits` | Статистика визитов с фильтром по дате (по умолчанию 7 дней) |
| `sources_summary` | Общий обзор источников трафика |
| `sources_search_phrases` | Топ поисковых фраз |
| `get_traffic_sources_types` | Разбивка по типам источников (органика, прямой, реферальный) |
| `get_search_engines_data` | Сессии по поисковым системам |
| `get_new_users_by_source` | Привлечение новых пользователей по источнику (30 дней) |

### Контент-аналитика
> Требует подключения Яндекс Дзен/Турбо к счётчику.

| Инструмент | Описание |
|------------|----------|
| `get_content_analytics_sources` | Источники трафика к статьям |
| `get_content_analytics_categories` | Статистика по категориям контента |
| `get_content_analytics_authors` | Эффективность авторов |
| `get_content_analytics_topics` | Статистика по темам |
| `get_content_analytics_articles` | Топ статей по просмотрам |

### Демография и устройства
| Инструмент | Описание |
|------------|----------|
| `get_user_demographics` | Возраст, пол, тип устройства |
| `get_device_analysis` | Анализ по браузерам и ОС |
| `get_mobile_vs_desktop` | Сравнение мобильного и десктопного трафика |
| `get_page_depth_analysis` | Сессии по глубине просмотра страниц |

### География
| Инструмент | Описание |
|------------|----------|
| `get_regional_data` | Трафик по городам |
| `get_geographical_organic_traffic` | Органический трафик по стране и городу |

### Производительность и конверсии
| Инструмент | Описание |
|------------|----------|
| `get_page_performance` | Отказы и время на странице по URL |
| `get_goals_conversion` | Конверсии по заданным целям |
| `get_organic_search_performance` | SEO-эффективность по запросам и системам |
| `get_conversion_rate_by_source_and_landing` | Конверсия по источнику и посадочной странице |

### Расширенные отчёты
| Инструмент | Описание |
|------------|----------|
| `get_ecommerce_performance` | E-commerce: покупки по названию товара |
| `get_data_by_time` | Временные ряды с группировкой |
| `get_yandex_direct_experiment` | Отказы по A/B-экспериментам Яндекс Директ |
| `get_browsers_report` | Отчёт по браузерам |
| `get_drilldown` | Иерархический drill-down отчёт |
| `compare_segments` | Сравнение двух сегментов |
| `compare_segments_drilldown` | Сравнение сегментов в виде иерархии |

### Ограничение размера ответа

Многие инструменты принимают параметр `limit` для ограничения количества строк. Поддерживают `limit`: `sources_summary`, `sources_search_phrases`, `get_device_analysis`, `get_page_performance`, `get_organic_search_performance`, `get_conversion_rate_by_source_and_landing`, `get_regional_data`, `get_geographical_organic_traffic`, `get_drilldown`, `compare_segments`, `compare_segments_drilldown`.

## Конфигурация

Все настройки через переменные окружения:

| Переменная | Обязательно | По умолчанию | Описание |
|------------|-------------|--------------|----------|
| `YANDEX_API_KEY` | ✓ | — | OAuth-токен Яндекса |
| `YANDEX_TIMEOUT` | | `30` | Таймаут запроса (секунды) |
| `YANDEX_RETRIES` | | `3` | Количество повторных попыток при 5xx |
| `YANDEX_RETRY_DELAY` | | `1.0` | Базовая задержка между попытками (секунды) |
| `READ_ONLY_MODE` | | `false` | Только инструменты чтения |
| `ENABLED_TOOLS` | | все | Список разрешённых инструментов через запятую |

Скопируйте `.env.example` в `.env` и заполните значения.

## CLI

```bash
# stdio (по умолчанию, для MCP-клиентов)
ya-metrics-mcp

# HTTP-транспорт
ya-metrics-mcp --transport streamable-http --port 8000

# Подробные логи
ya-metrics-mcp -vv

# Указать .env-файл
ya-metrics-mcp --env-file /путь/к/.env
```

## Установка

**Из PyPI:**
```bash
uvx ya-metrics-mcp
```

**Из исходников:**
```bash
git clone https://github.com/mrkhachaturov/ya-metrics-mcp
cd ya-metrics-mcp
uv sync
uv run ya-metrics-mcp
```

## Разработка

```bash
# Установка с dev-зависимостями
uv sync --extra dev

# Запуск тестов
uv run pytest

# Линтер
uv run ruff check src/
```

## Лицензия

MIT
