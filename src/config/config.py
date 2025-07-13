import os
from typing import List, Optional, TypeVar
from dotenv import load_dotenv

T = TypeVar('T')
load_dotenv()


def load_config():
    return {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'MODE': os.environ.get("MODE", "both").lower(),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'TELEGRAM_DIST_CHAT_ID': os.getenv('TELEGRAM_DIST_CHAT_ID'),
        'TELEGRAM_API_ID': int(os.getenv('TELEGRAM_API_ID')),
        'TELEGRAM_API_HASH': os.getenv('TELEGRAM_API_HASH'),
        'TELEGRAM_PHONE': os.getenv('TELEGRAM_PHONE'),
        'TELEGRAM_SESSION_NAME': os.getenv('TELEGRAM_SESSION_NAME'),
        'MAX_TOKENS_PER_CHUNK': int(os.getenv('MAX_TOKENS_PER_CHUNK', 3000)),
        'IGNORED_SENDER_IDS': extract_list_from_env('IGNORED_SENDER_IDS', convert_type=int),
        'DAY_OFFSET': abs(int(os.getenv('DAY_OFFSET', 7))),
        'HASHTAGS': extract_list_from_env('HASHTAGS', convert_type=str),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'OPENAI_API_BASE_URL': os.getenv('OPENAI_API_BASE_URL'),
        'OPENAI_API_MODEL': os.getenv('OPENAI_API_MODEL'),
    }


def extract_list_from_env(
        env_key: str,
        default: str = '',
        convert_type: Optional[callable] = None,
        remove_duplicates: bool = True
) -> List[T]:
    """
    Извлекает список из переменной окружения, разделенной запятыми.

    Args:
        env_key: Название переменной окружения.
        default: Значение по умолчанию, если переменная не задана.
        convert_type: Функция для преобразования элементов (например, int, str).
        remove_duplicates: Удалять ли дубликаты (по умолчанию True).

    Returns:
        Список элементов, отфильтрованный от пустых значений.
    """
    raw_value = os.getenv(env_key, default).replace(' ', '')
    items = [item for item in raw_value.split(',') if item]

    if convert_type:
        try:
            items = [convert_type(item) for item in items]
        except (ValueError, TypeError) as e:
            raise ValueError(f"Ошибка преобразования элементов в {env_key}: {e}")

    return list(set(items)) if remove_duplicates else items
