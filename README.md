# ConvoDigestBot

## Структура проекта

```
ConvoDigestBot/
├── src/
│   ├── config/
│   │   ├── config.py
│   │   └── schemas.py
│   ├── llm/
│   │   ├── client.py
│   │   └── prompts.py
│   ├── scheduler/
│   │   └── scheduler.py
│   └── telegram/
│       ├── bot.py
│       ├── sender.py
│       ├── telethon_client.py
│       └── telethon_session.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── main.py
```

- Исходные Python-файлы разложены по папкам внутри `src/`:
  - `llm/` — генерация отчёта через LLM, промпты
  - `telegram/` — работа с Telegram: загрузка истории (Telethon), отправка отчёта (aiogram)
  - `scheduler/` — планировщик задач и пайплайн
  - `config/` — конфигурация и схемы (загрузка переменных окружения, обработка списков)
- Точка входа — файл `main.py` в корне.
- Конфигурационные и документационные файлы — в корне.

## Получение API ID и API Hash для Telegram

1. Войдите в аккаунт Telegram на [my.telegram.org](https://my.telegram.org/).
2. Перейдите в раздел **API development tools**.
3. Создайте новое приложение, заполнив поля:
   - **App title**: Название приложения (любое).
   - **Short name**: Короткое имя (любое).
   - **Platform**: Выберите подходящую платформу (например, "Other").
   - **Description**: Краткое описание (опционально).
4. Нажмите **Create application**.
5. Сохраните полученные **App api_id** и **App api_hash** — они понадобятся для заполнения переменных `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` в вашем `.env` файле.

> **Важно:** Храните api_id и api_hash в безопасном месте и не делитесь ими публично!
>
> Подробнее: [Официальная документация Telegram](https://core.telegram.org/api/obtaining_api_id)

## Авторизация Telethon user session

Перед заполнением .env необходимо авторизовать Telethon user session (userbot):

```
docker-compose run --rm app python src/telegram/telethon_session.py
```

Если сессия не создана, скрипт попросит ввести код из Telegram. Если уже авторизовано — просто сообщит об этом.

После успешной авторизации в консоли будет выведен ваш **user_id**, а в корне проекта появится файл **anon.session** (или SESSION_NAME(имя сессии из конфига).session):

```
[Telethon] Ваш user_id: 123456789
```

Скопируйте этот user_id — он понадобится для переменной `TELEGRAM_OWNER_ID` в .env.

---

## Конфигурация
- Все параметры берутся из файла `.env`.
- Для загрузки и обработки переменных окружения используется `src/config/config.py`.
- Для извлечения списков из переменных окружения используется функция `extract_list_from_env` (например, для списков ID или хэштегов).

### Основные переменные окружения

| Переменная                | Описание                                                                     |
|--------------------------|------------------------------------------------------------------------------|
| BOT_TOKEN                | Токен Telegram-бота (aiogram)                                                |
| MODE                     | Режим работы: both (по умолчанию)                                            |
| TELEGRAM_OWNER_ID        | user_id владельца сессии Telethon (разрешённый пользователь для команд бота) |
| TELEGRAM_CHAT_ID         | ID исходного Telegram-чата                                                   |
| TELEGRAM_DIST_CHAT_ID    | ID чата для отправки отчёта                                                  |
| TELEGRAM_API_ID          | API ID Telegram (userbot, Telethon)                                          |
| TELEGRAM_API_HASH        | API Hash Telegram (userbot, Telethon)                                        |
| TELEGRAM_PHONE           | Телефон для авторизации userbot                                              |
| TELEGRAM_SESSION_NAME    | Имя файла сессии Telethon                                                    |
| MAX_TOKENS_PER_CHUNK     | Максимум токенов в одном чанке (по умолчанию 3000)                           |
| IGNORED_SENDER_IDS       | Список ID отправителей для игнорирования                                     |
| DAY_OFFSET               | За сколько дней собирать сообщения (по умолчанию 7)                          |
| HASHTAGS                 | Список хэштегов для фильтрации                                               |
| OPENAI_API_KEY           | Ключ OpenAI                                                                  |
| OPENAI_API_BASE_URL      | Базовый URL OpenAI API                                                       |
| OPENAI_API_MODEL         | Модель OpenAI                                                                |

- Для списков (например, IGNORED_SENDER_IDS, HASHTAGS) значения указываются через запятую, пробелы игнорируются.
---

## Запуск через Docker

1. Скопируйте `.env.example` в `.env` и заполните параметры.
2. Соберите и запустите контейнер:
   ```sh
   docker-compose up --build
   ```
   По умолчанию запустится планировщик (еженедельный отчёт).

## Локальный запуск (без Docker)
1. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```
2. Запустите:
   ```sh
   python main.py
   ```
   Это запустит планировщик, который сразу выполнит пайплайн и далее будет работать по расписанию.

## Возможности

- **Автоматический сбор сообщений из Telegram-чата за DAY_OFFSET**
- **Генерация отчёта через LLM (OpenAI)**
- **Отправка отчёта в Telegram-чат**
- **Планировщик (APScheduler) для запуска по расписанию**

> **Внимание:**  
> На данный момент нет CLI-режимов для ручного запуска только генерации отчёта или только отправки.  
> Все действия происходят автоматически через планировщик.

## Технологии
- Telethon, aiogram, APScheduler, OpenAI 