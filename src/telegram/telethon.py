"""
Модуль для работы с историей сообщений из Telegram-чатов через Telethon (user session).
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict
from telethon.tl.types import User
from telethon import TelegramClient
from src.config.config import load_config

config = load_config()

API_ID = config['TELEGRAM_API_ID']
API_HASH = config['TELEGRAM_API_HASH']
PHONE = config['TELEGRAM_PHONE']
SESSION_NAME = config['TELEGRAM_SESSION_NAME']
DAY_OFFSET = config['DAY_OFFSET']
IGNORED_SENDER_IDS = config['IGNORED_SENDER_IDS']
IGNORED_PREFIXES = ['/start', '/help', '/telegram', '/command', '🎆Дай мне мудрость']


def get_telegram_client():
    return TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def get_messages(chat_id_or_username: str, day_offset: int = DAY_OFFSET) -> list[dict]:
    since = datetime.now() - timedelta(days=day_offset)
    messages = []

    client = get_telegram_client()
    await client.start(phone=PHONE)

    # Найдём нужный чат
    entity = await find_entity(client, chat_id_or_username)

    # Загружаем только сообщения за последние 7 дней
    async for msg in client.iter_messages(entity):
        if msg.date.replace(tzinfo=None) < since:
            break
        if msg.text and not should_skip_message(msg):
            messages.insert(0, {
                'id': msg.id,
                'date': msg.date.isoformat(),
                'username': get_formatted_username(msg.sender),
                'reply_to': msg.reply_to_msg_id,
                'text': msg.text
            })

    await client.disconnect()
    return messages


async def get_messages_tree(chat_id_or_username: str, day_offset: int = DAY_OFFSET) -> str:
    """
    Преобразует плоский список сообщений в линейный текст с отступами, отражающими иерархию.

    Args:
        chat_id_or_username: ID или имя пользователя чата.
        day_offset: Количество дней для загрузки сообщений.

    Returns:
        Строка, представляющая переписку с отступами для вложенных сообщений.
        Возвращает пустую строку, если нет сообщений.
    """
    messages = await get_messages(chat_id_or_username, day_offset)

    # Если нет сообщений, возвращаем пустую строку
    if not messages:
        return ""

    # Словарь для хранения сообщений по ID
    messages_dict = {msg['id']: {**msg, 'children': []} for msg in messages}

    # Список корневых сообщений
    root_messages = []

    # Строим иерархию
    for msg_id, msg_data in messages_dict.items():
        reply_to = msg_data['reply_to']
        if reply_to and reply_to in messages_dict:
            # Если сообщение отвечает на другое, добавляем его как потомка
            messages_dict[reply_to]['children'].append(msg_data)
        else:
            # Если нет reply_to или родитель не найден, это корневое сообщение
            root_messages.append(msg_data)

    # Сортируем корневые сообщения по дате (от старых к новым)
    root_messages.sort(key=lambda x: x['date'])

    # Сортируем потомков каждого сообщения по дате
    for msg in messages_dict.values():
        msg['children'].sort(key=lambda x: x['date'])

    # Формируем линейный текст с отступами
    def format_message(msg, indent: int = 0) -> str:
        result = ["  " * indent + f"{msg['username']}: {msg['text']}"]
        for child in msg['children']:
            result.append(format_message(child, indent + 1))
        return "\n".join(result)

    result = [format_message(msg) for msg in root_messages]
    print(f"Built text with {len(result)} root messages")
    return "\n".join(result)


def should_skip_message(msg) -> bool:
    """
    Фильтрует мусорные сообщения.
    """
    if msg.sender_id in IGNORED_SENDER_IDS:
        return True
    if msg.fwd_from:
        fwd_sender_id = (getattr(msg.fwd_from.from_id, 'user_id', None)
                         or getattr(msg.fwd_from.from_id, 'channel_id', None))
        if fwd_sender_id in IGNORED_SENDER_IDS:
            return True
    text = (msg.text or "").strip()
    if not text:
        return True
    # Игнорируем бот-команды и сообщения с @telegram
    if text.startswith('/') or re.search(r'@\w*telegram\w*', text, re.IGNORECASE):
        return True

    return False


async def find_entity(client, chat_id_or_username):
    # Сначала пробуем напрямую через get_entity
    try:
        return await client.get_entity(chat_id_or_username)
    except (ValueError, TypeError):
        pass

    # Если не нашлось — ищем по локальным диалогам (и названию)
    async for dialog in client.iter_dialogs():
        if (str(dialog.id) == str(chat_id_or_username)
                or dialog.name == chat_id_or_username
                or getattr(dialog.entity, 'username', None) == chat_id_or_username):
            return dialog.entity

    raise ValueError(f"Чат с id/username '{chat_id_or_username}' не найден среди ваших диалогов!")


def get_formatted_username(sender: User) -> str:
    if sender.username:
        return f"@{sender.username}"
    if sender.first_name and sender.last_name:
        return f"{sender.first_name} {sender.last_name}".strip()
    return sender.first_name or "Unknown"


async def get_list_chats() -> List[Dict]:
    """
    Возвращает список всех чатов пользователя (id, name, username) в виде JSON-объекта.
    """
    client = get_telegram_client()
    await client.start(phone=PHONE)

    chats = []
    async for dialog in client.iter_dialogs():
        chat_info = {
            "id": dialog.id,
            "name": dialog.name,
            "username": getattr(dialog.entity, 'username', None)
        }
        chats.append(chat_info)

    await client.disconnect()

    return chats
