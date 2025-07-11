import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


def get_ignored_sender_ids() -> List[str]:
    """
    Возвращает список уникальных sender_id из переменной окружения.
    Пробелы убираются, пустые строки фильтруются.
    """
    return list(
        {sender_id for sender_id in os.getenv('IGNORED_SENDER_IDS', '').replace(' ', '').split(',') if sender_id})


def get_config():
    return {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'TELEGRAM_API_ID': int(os.getenv('TELEGRAM_API_ID')),
        'TELEGRAM_API_HASH': os.getenv('TELEGRAM_API_HASH'),
        'TELEGRAM_PHONE': os.getenv('TELEGRAM_PHONE'),
        'TELEGRAM_SESSION_NAME': os.getenv('TELEGRAM_SESSION_NAME'),
        'MAX_TOKENS_PER_CHUNK': int(os.getenv('MAX_TOKENS_PER_CHUNK', 3000)),
        'IGNORED_SENDER_IDS': get_ignored_sender_ids(),
        'DAY_OFFSET': abs(int(os.getenv('DAY_OFFSET', 7))),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'OPENAI_API_BASE_URL': os.getenv('OPENAI_API_BASE_URL'),
        'OPENAI_API_MODEL': os.getenv('OPENAI_API_MODEL'),
    }
