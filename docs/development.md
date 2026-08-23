# Запуск и разработка

## Требования

Рекомендуемая версия Python:

```text
Python 3.10 или 3.11
```

Python 3.13 использовать не рекомендуется: в проекте есть зависимости для NLP и ML, у которых могут быть ограничения по бинарным сборкам.

Также понадобятся:

- PostgreSQL;
- доступный `OPENAI_API_KEY`;
- браузер и драйвер для Selenium;
- PowerShell или другой терминал для запуска команд.

## Установка после клонирования

```mermaid
flowchart LR
    A["Клонировать репозиторий"] --> B["Создать .venv"]
    B --> C["Активировать окружение"]
    C --> D["Установить зависимости"]
    D --> E["Настроить .env"]
    E --> F["Применить миграции"]
    F --> G["Запустить FastAPI"]
```

```powershell
git clone https://github.com/EgorPlehanov/news_intelligence.git
cd news_intelligence

py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Альтернативный вариант для разработки - установка проекта в editable-режиме через `pyproject.toml`:

```powershell
pip install -e .
```

Для установки вместе с тестовыми инструментами:

```powershell
pip install -e ".[dev]"
```

## Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

Затем укажите в `.env` параметры локальной базы данных и ключ OpenAI API:

```env
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_intelligence
OPENAI_API_KEY=your_openai_api_key
HOST=127.0.0.1
PORT=8000
```

Создайте базу данных PostgreSQL с именем, указанным в `DB_NAME`, затем примените миграции:

```powershell
alembic upgrade head
```

## Запуск

```powershell
uvicorn app.main:app --reload
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

При старте `app/main.py` запускает фоновый планировщик, который периодически вызывает парсер новостей.

## Проверка окружения

Проверить установленные зависимости:

```powershell
pip check
```

Проверить импорт ключевых модулей:

```powershell
python -c "import fastapi, sqlalchemy, bs4, nltk, sklearn, hdbscan, openai; print('ok')"
```

Проверить подключение к базе данных через настройки проекта:

```powershell
python -c "from app.database import engine; print(engine.url.render_as_string(hide_password=True))"
```

## Структура проекта

```text
news_intelligence/
├── app/
│   ├── main.py                         # маршруты FastAPI и запуск приложения
│   ├── config.py                       # настройки из переменных окружения
│   ├── database.py                     # engine SQLAlchemy и фабрика сессий
│   ├── models.py                       # ORM-модели базы данных
│   ├── schemas.py                      # Pydantic-схемы данных
│   ├── crud.py                         # операции чтения и записи в БД
│   ├── news_parser/
│   │   ├── parser.py                   # координация запуска парсеров
│   │   ├── parser_scheduler.py         # фоновое расписание парсинга
│   │   └── ria_parsers/                # парсеры РИА Новости
│   └── news_processing/
│       ├── processing.py               # основной пайплайн создания сводки
│       ├── processing_utils.py         # валидация и форматирование кластеров
│       ├── clustering/                 # предобработка и кластеризация текстов
│       └── summarize/                  # сокращение текста и генерация через ChatGPT
├── alembic/                            # миграции базы данных
├── templates/                          # HTML-шаблоны Jinja2
├── static/                             # CSS, JS и изображения интерфейса
├── docs/images/                        # скриншоты для документации
├── pyproject.toml                      # метаданные проекта и прямые зависимости
├── requirements.txt
└── README.md
```

## Тесты

Автоматические тесты в репозитории пока отсутствуют.

Минимальный набор тестов, который стоит добавить для повышения качества проекта:

- unit-тесты для `parse_date`: время за сегодня, формат `Вчера`, дата с русским месяцем;
- unit-тесты для `preprocess_text`: удаление стоп-слов, лемматизация, удаление пунктуации;
- unit-тесты для `extract_keywords`: ограничение количества ключевых слов и фильтрация частей речи;
- тесты CRUD-слоя на временной тестовой базе или SQLite-совместимой конфигурации;
- тест основного сценария `news_processing` с mock-объектами вместо реального парсинга и OpenAI API;
- smoke-тест FastAPI-маршрутов через `TestClient`.

После добавления `pytest` тесты можно будет запускать командой:

```powershell
pytest
```

## Технические улучшения

- добавить минимальный набор тестов и бейдж тестов в README;
- заменить устаревший `openai.ChatCompletion.create` на актуальный клиент OpenAI SDK;
- инициализировать счетчик повторных попыток в `parse_ria_news`;
- исправить получение новости по `news_id` в `get_news`;
- сделать парсеры источников явным реестром вместо динамического поиска функции по имени;
- добавить обработку пустых наборов новостей перед кластеризацией и расчетом метрик;
- отделить запуск планировщика от импорта приложения, чтобы тесты и dev-сервер стартовали предсказуемее.
