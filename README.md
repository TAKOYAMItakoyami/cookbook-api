# Cookbook API

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.17.1-A30000?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-1.22-009639?style=for-the-badge&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

REST API сервиса рецептов: пользователи публикуют рецепты, ищут их по тегам и ингредиентам,
добавляют блюда в избранное и в список покупок, скачивают список покупок файлом и подписываются
на других авторов.

Проект — бэкенд-часть: Django + Django REST Framework, PostgreSQL (или SQLite для разработки),
Gunicorn и Nginx. Интерфейс в репозиторий не входит, API используется фронтендом или любым другим
HTTP-клиентом.

## Возможности

- регистрация, вход по email и аутентификация по токену;
- профиль пользователя, загрузка и удаление аватара;
- CRUD-операции над собственными рецептами;
- справочники ингредиентов и тегов;
- фильтры рецептов по автору, тегам, избранному и списку покупок;
- избранное и список покупок, скачивание списка покупок в `.txt`;
- подписки на авторов и лента их рецептов;
- короткие ссылки на рецепты;
- панель администратора Django.

## База данных

Проект поддерживает две СУБД — выбор делается переменной `DB_ENGINE`
в файле `.env`, код приложения от этого не зависит:

| Режим | СУБД | `DB_ENGINE` |
| ----- | ---- | ----------- |
| Локальная разработка | SQLite | `django.db.backends.sqlite3` |
| Docker / прод | PostgreSQL 16 | `django.db.backends.postgresql` |

При `DB_ENGINE=django.db.backends.sqlite3` база создаётся в файле `db.sqlite3`
в корне проекта; при `DB_ENGINE=django.db.backends.postgresql` подключение идёт
к контейнеру `db` по параметрам `POSTGRES_USER` / `POSTGRES_PASSWORD` / `DB_HOST` / `DB_PORT`.

## Использованные технологии

| Технология | Версия | Назначение |
| ---------- | ------ | ---------- |
| [Python](https://www.python.org/) | 3.12 | Язык разработки |
| [Django](https://www.djangoproject.com/) | 5.2 | Веб-фреймворк |
| [Django REST Framework](https://www.django-rest-framework.org/) | 3.17.1 | Построение REST API |
| [Djoser](https://djoser.readthedocs.io/) | 2.3.3 | Регистрация, профиль и токен-аутентификация |
| [django-filter](https://django-filter.readthedocs.io/) | 26.1 | Фильтрация queryset-ов |
| [drf-extra-fields](https://github.com/Hipo/drf-extra-fields) | 3.7.0 | Загрузка изображений в формате Base64 |
| [Pillow](https://python-pillow.org/) | 12.3.0 | Работа с изображениями |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 1.2.2 | Переменные окружения из `.env` |
| [PostgreSQL](https://www.postgresql.org/) | 16 | Основная база данных |
| [SQLite](https://www.sqlite.org/) | — | База данных для локальной разработки |
| [Gunicorn](https://gunicorn.org/) | 25.3.0 | WSGI-сервер |
| [Nginx](https://nginx.org/) | 1.22.1 | Отдача статики и проксирование запросов |
| [Docker](https://www.docker.com/) / [Docker Compose](https://docs.docker.com/compose/) | — | Контейнеризация и запуск сервисов |

## Проверка кода

Проект настроен на flake8 (конфигурация в `setup.cfg`), isort (профиль `black`,
длина строки 79) и black (длина строки 79, `pyproject.toml`). Линтеры и форматтеры
включены в `requirements.txt`:

```bash
flake8 .
isort --check-only --diff .
black --check .
```

CI (GitHub Actions) запускает flake8, isort и black при каждом push и pull request
в ветки `main` и `develop` (`.github/workflows/ci.yml`).

## Структура проекта

```text
cookbook-api/
├── api/                      # Слой API
│   ├── constants.py          # Константы API
│   ├── filters.py            # Фильтры рецептов и ингредиентов
│   ├── pagination.py         # Пагинация с настраиваемым лимитом
│   ├── permissions.py        # Право доступа автора и администратора
│   ├── serializers.py        # Сериализаторы чтения и записи
│   ├── urls.py               # Маршруты API и авторизации
│   └── views.py              # ViewSet-ы API
│
├── cookbook/                 # Настройки проекта
│   ├── settings.py           # Настройки Django, DRF, Djoser, БД
│   ├── urls.py               # Корневые маршруты: admin, api, короткие ссылки
│   ├── wsgi.py               # Точка входа WSGI
│   └── asgi.py               # Точка входа ASGI
│
├── recipes/                  # Приложение рецептов
│   ├── constants.py          # Ограничения полей моделей
│   ├── models.py             # Recipe, Tag, Ingredient, Favorite и другие
│   ├── admin.py              # Регистрация моделей в админке
│   ├── utils.py              # Генерация кода короткой ссылки
│   └── management/
│       └── commands/
│           ├── load_ingredients.py   # Загрузка ингредиентов из CSV
│           └── load_tags.py          # Загрузка тегов из CSV
│
├── users/                    # Приложение пользователей
│   ├── models.py             # Кастомная модель User (email вместо username)
│   └── admin.py              # Администрирование пользователей
│
├── data/
│   ├── ingredients.csv       # Справочник ингредиентов для загрузки
│   ├── ingredients.json      # Тот же справочник в JSON
│   └── tags.csv              # Справочник тегов для загрузки
│
├── gateway/                  # Веб-сервер перед приложением
│   ├── Dockerfile            # Образ Nginx
│   └── nginx.conf            # Конфигурация Nginx
│
├── .dockerignore             # Исключения для сборки Docker-образа
├── .env.example              # Шаблон переменных окружения
├── .gitattributes            # Правила нормализации переводов строк
├── .github/
│   └── workflows/
│       └── ci.yml            # CI: flake8, isort, black, тесты, сборка Docker
├── .gitignore                # Исключения для Git
├── docker-compose.yml        # Сервисы db, backend, gateway
├── Dockerfile                # Образ приложения
├── entrypoint.sh             # Точка входа контейнера приложения
├── manage.py                 # Управляющий скрипт Django
├── openapi.yml               # Спецификация API в формате OpenAPI 3.0
├── pyproject.toml            # Конфигурация black
├── requirements.txt          # Зависимости Python
├── setup.cfg                 # Конфигурация flake8 и isort
└── LICENSE                   # Лицензия MIT
```

Загружаемые пользователем файлы попадают в каталог `media/`, собранная статика —
в `collected_static/`.

## Запуск через Docker

Этот способ поднимает сразу три сервиса: базу PostgreSQL, приложение и Nginx.

Требуется установленные Docker Engine и Docker Compose.

1. Клонировать репозиторий:

   ```bash
   git clone https://github.com/TAKOYAMItakoyami/cookbook-api.git
   cd cookbook-api
   ```

2. Создать файл `.env` в корне проекта и заполнить его. Файл нужен и `docker-compose.yml`
   (он передаёт переменные сервисам `db` и `backend`), и самому приложению:

   ```bash
   cp .env.example .env        # Linux / macOS
   copy .env.example .env      # Windows (cmd)
   ```

   Минимально для Docker:

   ```env
   SECRET_KEY=замените-на-свой-ключ
   DEBUG=False

   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=cookbook

   POSTGRES_DB=cookbook
   POSTGRES_USER=cookbook_user
   POSTGRES_PASSWORD=cookbook_password

   DB_HOST=db
   DB_PORT=5432
   ```

   Значения `POSTGRES_DB`, `POSTGRES_USER` и `POSTGRES_PASSWORD` должны совпадать
   с `DB_NAME`, `POSTGRES_USER` и `POSTGRES_PASSWORD`, иначе приложение не подключится
   к базе.

3. Собрать и запустить контейнеры:

   ```bash
   docker compose up -d --build
   ```

   При старте контейнера приложения `entrypoint.sh` последовательно выполняет миграции,
   загружает справочники тегов и ингредиентов, собирает статику и запускает Gunicorn.

4. Создать администратора (по желанию):

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

Готово:

- API — `http://localhost:8080/api/`
- админ-панель — `http://localhost:8080/admin/`

Полезные команды:

```bash
docker compose logs -f backend            # логи приложения
docker compose exec backend python manage.py <команда>   # manage.py внутри контейнера
docker compose down                       # остановить контейнеры
docker compose down -v                    # остановить и удалить том с базой данных
```

Как распределены сервисы:

| Сервис | Образ | Что делает |
| ------ | ----- | ---------- |
| `db` | `postgres:16` | Хранит данные, ждёт готовности по healthcheck |
| `backend` | сборка из корня | Gunicorn на порту 8000, миграции и загрузка данных |
| `gateway` | сборка из `gateway/` | Nginx на порту 8080: отдаёт `/static/` и `/media/`, проксирует `/api/`, `/admin/` и `/s/` в `backend` |

Данные базы, статики и медиафайлов лежат в именованных томах `pg_data`, `static` и `media`.

## Запуск без Docker

Локально проект можно запустить на SQLite — отдельная база данных для этого не нужна.

Требуется Python 3.12 и pip.

1. Клонировать репозиторий:

   ```bash
   git clone https://github.com/TAKOYAMItakoyami/cookbook-api.git
   cd cookbook-api
   ```

2. Создать и активировать виртуальное окружение:

   ```bash
   python -m venv venv
   ```

   - Windows:

     ```bash
     venv\Scripts\activate
     ```

   - Linux / macOS:

     ```bash
     source venv/bin/activate
     ```

3. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Создать `.env` в корне проекта. Для SQLite:

   ```env
   SECRET_KEY=замените-на-свой-ключ
   DEBUG=True

   ALLOWED_HOSTS=localhost,127.0.0.1

   DB_ENGINE=django.db.backends.sqlite3
   DB_NAME=db.sqlite3
   ```

   `ALLOWED_HOSTS` оставлять пустым нельзя: без него Django отвечает `400 Bad Request`
   на запросы к `localhost`.

5. Применить миграции:

   ```bash
   python manage.py migrate
   ```

6. Загрузить справочники тегов и ингредиентов из `data/tags.csv` и `data/ingredients.csv`:

   ```bash
   python manage.py load_tags
   python manage.py load_ingredients
   ```

7. Создать администратора (по желанию):

   ```bash
   python manage.py createsuperuser
   ```

8. Запустить сервер разработки:

   ```bash
   python manage.py runserver
   ```

Готово:

- API — `http://127.0.0.1:8000/api/`
- админ-панель — `http://127.0.0.1:8000/admin/`

При `DEBUG=True` Django сам отдаёт медиафайлы по адресу `/media/`. В остальных случаях
их отдаёт Nginx.

### Переменные окружения

| Переменная | Назначение |
| ---------- | ---------- |
| `SECRET_KEY` | Ключ Django. По умолчанию `django_key`, в production замените |
| `DEBUG` | `True` включает режим отладки и раздачу медиафайлов средствами Django |
| `ALLOWED_HOSTS` | Список допустимых хостов через запятую |
| `CSRF_TRUSTED_ORIGINS` | Доверенные источники CSRF (нужны при работе за Nginx) |
| `DB_ENGINE` | `django.db.backends.sqlite3` или `django.db.backends.postgresql` |
| `DB_NAME` | Имя файла базы SQLite или имя базы PostgreSQL |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Параметры создания базы в контейнере PostgreSQL |
| `DB_HOST`, `DB_PORT` | Хост и порт PostgreSQL (для Docker — `db` и `5432`) |

## Документация API

Полная спецификация OpenAPI 3.0 лежит в файле [`openapi.yml`](openapi.yml) в корне проекта.
Её можно открыть в любом просмотрщике OpenAPI, например в
[Redocly Preview](https://redocly.com/docs/api-registry/guides/markdown-topics#previewing-openapi)
или локально:

```bash
npx @redocly/cli build-docs openapi.yml --output redoc.html
```

## API: общие сведения

| Развёртывание | Базовый URL |
| ------------- | ----------- |
| `runserver` | `http://127.0.0.1:8000/api/` |
| Docker Compose | `http://localhost:8080/api/` |

Аутентификация — токен Django REST Framework. Защищённые запросы требуют заголовок:

```text
Authorization: Token <ваш_токен>
```

Публичные эндпоинты (`GET` списков и деталей рецептов, ингредиентов, тегов, пользователей)
доступны без токена.

### Аутентификация

| Метод | Эндпоинт | Доступ | Описание |
| ----- | -------- | ------ | -------- |
| POST | `/api/auth/token/login/` | все | Получить токен по `email` и `password` |
| POST | `/api/auth/token/logout/` | токен | Удалить текущий токен |

### Пользователи

| Метод | Эндпоинт | Доступ | Описание |
| ----- | -------- | ------ | -------- |
| POST | `/api/users/` | все | Регистрация (`email`, `username`, `first_name`, `last_name`, `password`) |
| GET | `/api/users/` | все | Список пользователей с признаком подписки |
| GET | `/api/users/{id}/` | все | Профиль пользователя |
| GET | `/api/users/me/` | токен | Текущий пользователь |
| PUT, PATCH | `/api/users/me/` | токен | Обновить свой профиль |
| DELETE | `/api/users/me/` | токен + пароль | Удалить свой аккаунт |
| PUT | `/api/users/me/avatar/` | токен | Загрузить или обновить аватар (Base64) |
| DELETE | `/api/users/me/avatar/` | токен | Удалить аватар |
| POST | `/api/users/{id}/subscribe/` | токен | Подписаться на автора |
| DELETE | `/api/users/{id}/subscribe/` | токен | Отписаться от автора |
| GET | `/api/users/subscriptions/` | токен | Список авторов, на которые подписан пользователь |

Djoser дополнительно предоставляет эндпоинты для работы с паролем и почтой:
`/api/users/set_password/`, `/api/users/set_email/`, `/api/users/reset_password/`,
`/api/users/reset_password_confirm/`, `/api/users/activation/`,
`/api/users/resend_activation/`. Для тех из них, где отправляется письмо, нужно настроить
почтовый сервис Django (`EMAIL_BACKEND` и связанные настройки).

### Рецепты

| Метод | Эндпоинт | Доступ | Описание |
| ----- | -------- | ------ | -------- |
| GET | `/api/recipes/` | все | Список рецептов с фильтрацией и пагинацией |
| POST | `/api/recipes/` | токен | Создать рецепт |
| GET | `/api/recipes/{id}/` | все | Детали рецепта |
| PUT, PATCH | `/api/recipes/{id}/` | автор, админ | Обновить рецепт |
| DELETE | `/api/recipes/{id}/` | автор, админ | Удалить рецепт |
| POST | `/api/recipes/{id}/favorite/` | токен | Добавить рецепт в избранное |
| DELETE | `/api/recipes/{id}/favorite/` | токен | Удалить рецепт из избранного |
| POST | `/api/recipes/{id}/shopping_cart/` | токен | Добавить рецепт в список покупок |
| DELETE | `/api/recipes/{id}/shopping_cart/` | токен | Удалить рецепт из списка покупок |
| GET | `/api/recipes/{id}/get-link/` | все | Получить короткую ссылку на рецепт |
| GET | `/api/recipes/download_shopping_cart/` | токен | Скачать список покупок файлом `.txt` |

Поля создаваемого рецепта: `name`, `text`, `cooking_time` (от 1 до 32000), `image`
(изображение в Base64), `tags` — список ID тегов, `ingredients` — список
`{"id": <ID ингредиента>, "amount": <количество от 1 до 32000>}`. Ingredients и tags
обязательны и не должны повторяться.

### Ингредиенты и теги

| Метод | Эндпоинт | Описание |
| ----- | -------- | -------- |
| GET | `/api/ingredients/` | Список ингредиентов (без пагинации), фильтр `?name=` — поиск по началу названия без учёта регистра |
| GET | `/api/ingredients/{id}/` | Детали ингредиента |
| GET | `/api/tags/` | Список тегов (без пагинации) |
| GET | `/api/tags/{id}/` | Детали тега |

### Фильтрация рецептов

| Параметр | Значение | Описание |
| -------- | -------- | -------- |
| `author` | ID пользователя | Рецепты указанного автора |
| `tags` | слаг тега | Рецепты с тегом; параметр можно повторить — `?tags=breakfast&tags=lunch` |
| `is_favorited` | `1` | Только рецепты из избранного текущего пользователя |
| `is_in_shopping_cart` | `1` | Только рецепты из списка покупок текущего пользователя |

### Пагинация

Страницы переключаются параметром `page`, размер страницы задаётся параметром `limit`.
По умолчанию 6 объектов на страницу. Пагинация не применяется
к ингредиентам и тегам. В ответах подписок и списков рецептов количество рецептов автора
можно ограничить параметром `recipes_limit`.

### Короткие ссылки

`GET /api/recipes/{id}/get-link/` возвращает адрес вида `http://<хост>/s/<код>/`.
Переход по такому адресу (`/s/<код>/`) редиректит пользователя (HTTP 302) на
API-эндпоинт рецепта `/api/recipes/<id>/` — JSON-представление рецепта.

## Примеры запросов

> Примеры ниже используют базовый URL `http://127.0.0.1:8000` (запуск без Docker).
> Для Docker замените его на `http://localhost:8080`.

### Регистрация пользователя

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "first_name": "Иван",
    "last_name": "Иванов",
    "password": "securepassword123"
  }'
```

### Получение токена

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Создание рецепта

```bash
curl -X POST http://127.0.0.1:8000/api/recipes/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Борщ",
    "text": "Классический рецепт борща...",
    "cooking_time": 120,
    "image": "data:image/png;base64,iVBORw0KGgo...",
    "tags": [1, 2],
    "ingredients": [
      {"id": 1, "amount": 300},
      {"id": 5, "amount": 2}
    ]
  }'
```

### Загрузка аватара

```bash
curl -X PUT http://127.0.0.1:8000/api/users/me/avatar/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"avatar": "data:image/png;base64,iVBORw0KGgo..."}'
```

### Добавление рецепта в избранное

```bash
curl -X POST http://127.0.0.1:8000/api/recipes/1/favorite/ \
  -H "Authorization: Token <your_token>"
```

### Скачивание списка покупок

```bash
curl -X GET http://127.0.0.1:8000/api/recipes/download_shopping_cart/ \
  -H "Authorization: Token <your_token>" \
  -o shopping_list.txt
```

### Получение короткой ссылки

```bash
curl http://127.0.0.1:8000/api/recipes/1/get-link/
```

### Подписка на автора

```bash
curl -X POST http://127.0.0.1:8000/api/users/2/subscribe/ \
  -H "Authorization: Token <your_token>"
```

### Фильтрация рецептов по тегам

```bash
curl "http://127.0.0.1:8000/api/recipes/?tags=breakfast&tags=lunch"
```

## Особенности реализации

- отдельные сериализаторы для чтения и для записи рецепта;
- оптимизация запросов через `select_related` и `prefetch_related`;
- признаки `is_favorited`, `is_in_shopping_cart` и `is_subscribed` вычисляются аннотациями `Exists`;
- `bulk_create()` при сохранении ингредиентов рецепта;
- уникальные ограничения на уровне БД для избранных, купленных и подписок;
- разграничение доступа разрешениями DRF: изменение рецепта доступно автору и администратору;
- кастомная модель пользователя с входом по email;
- токен-аутентификация через Djoser;
- загрузка изображений рецептов и аватаров в формате Base64;
- генерация коротких ссылок на рецепты и редирект по ним.

Djoser предоставляет стандартный набор эндпоинтов для работы с пользователем; удаление аккаунта требует подтверждения пароля.
Проект — выделенная бэкенд-часть учебного проекта Foodgram (Яндекс.Практикум).

## Автор

| Имя | GitHub |
| --- | ------ |
| Юлия Тарханова | [@TAKOYAMItakoyami](https://github.com/TAKOYAMItakoyami) |

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).
