"""
Модуль для загрузки истории сообщений из Telegram-чата за последние 7 дней через Telethon (user session).
"""
import asyncio
import re
from datetime import datetime, timedelta
from telethon import TelegramClient

from src.config.config import get_config

config = get_config()

API_ID = int(config['TELEGRAM_API_ID'])
API_HASH = config['TELEGRAM_API_HASH']
PHONE = config['TELEGRAM_PHONE']
SESSION_NAME = config['TELEGRAM_SESSION_NAME']
DAY_OFFSET = config['DAY_OFFSET']
IGNORED_PREFIXES = ['/start', '/help', '/telegram', '/command', '🎆Дай мне мудрость']
IGNORED_SENDER_IDS = [177224227]


def should_skip_message(msg) -> bool:
    """
    Фильтрует мусорные сообщения, оставляя только движ, поздравления и #повестка.
    """
    if msg.sender_id in IGNORED_SENDER_IDS:
        return True
    text = (msg.text or "").strip()
    if not text:
        return True

    # Игнорируем бот-команды и сообщения с @telegram
    if text.startswith('/') or re.search(r'@\w*telegram\w*', text, re.IGNORECASE):
        return True

    # Игнорируем короткие сообщения с эмодзи или без смысла (меньше 10 символов)
    if len(text) < 10 and any(c in text for c in '🎆😎👍😂'):
        return True

    # Всегда берём поздравления и #повестка
    if 'день рождения' in text.lower() or '#повестка' in text.lower():
        return False

    # Игнорируем сообщения без реакций, ответов или ников, если они короткие
    has_nick = '@' in text
    has_reaction = bool(getattr(msg, 'reactions', None))
    has_reply = bool(msg.reply_to_msg_id)
    is_long = len(text) >= 10

    return not (has_nick or has_reaction or has_reply or is_long)


async def get_messages(chat_id_or_username: str, day_offset: int = DAY_OFFSET) -> list[dict]:
    since = datetime.now() - timedelta(days=day_offset)
    messages = []

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start(phone=PHONE)

    # Найдём нужный чат
    entity = None
    async for dialog in client.iter_dialogs():
        if (str(dialog.id) == str(chat_id_or_username)
                or dialog.name == chat_id_or_username
                or getattr(dialog.entity, 'username', None) == chat_id_or_username):
            entity = dialog.entity
            break

    if entity is None:
        await client.disconnect()
        raise ValueError(f"Чат с id/username '{chat_id_or_username}' не найден среди ваших диалогов!")

    # Загружаем только сообщения за последние 7 дней
    async for msg in client.iter_messages(entity):
        if msg.date.replace(tzinfo=None) < since:
            break
        sender = msg.sender
        username = getattr(sender, 'username', None)

        if username:
            formatted_username = f"@{username}"
        else:
            first_name = getattr(sender, 'first_name', '')
            last_name = getattr(sender, 'last_name', '')
            formatted_username = f"{first_name} {last_name}".strip()
        if msg.text and not should_skip_message(msg):
            messages.insert(0, {
                'id': msg.id,
                'date': msg.date.isoformat(),
                'username': formatted_username,
                'reply_to': msg.reply_to_msg_id,
                'text': msg.text
            })

    await client.disconnect()
    return messages


def get_last_week_messages(chat_id_or_username: str) -> list[dict]:
    """
    Получить сообщения за последние 7 дней из чата (по chat_id или username).
    Возвращает список dict'ов с ключами: id, date, sender_id, text
    """
    return asyncio.run(get_messages(chat_id_or_username))
