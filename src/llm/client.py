"""
Модуль для суммаризации сообщений через OpenAI-совместимый API.
"""
import json
import logging
import tiktoken
from typing import List, Dict
from openai import AsyncOpenAI
from src.llm.prompts import REPORT_PROMPT, SYSTEM_PROMPT
from src.config.config import load_config

from src.config.schemas import RESPONSE_FORMAT

config = load_config()
OPENAI_API_KEY = config['OPENAI_API_KEY']
OPENAI_API_BASE_URL = config['OPENAI_API_BASE_URL']
OPENAI_API_MODEL = config['OPENAI_API_MODEL']
MAX_TOKENS_PER_CHUNK = config['MAX_TOKENS_PER_CHUNK']
OPENAI_CLIENT = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE_URL)

tokenizer = tiktoken.get_encoding("cl100k_base")


async def prepare_report(partial_summaries: Dict, model: str = OPENAI_API_MODEL) -> Dict:
    """Объединяет JSON-сводки чанков в итоговый отчёт."""
    combined_summary = json.dumps(partial_summaries, ensure_ascii=False)
    return await llm_call(model, REPORT_PROMPT, combined_summary)


def merge_partial_summaries(partials: List[Dict]) -> Dict:
    """Объединяет JSON-отчёты чанков в один итоговый отчёт согласно схеме."""
    result = {
        "main_fragments": [],
        "failures_and_rage": [],
        "topics_to_discuss": []
    }

    for partial in partials:
        result["main_fragments"].extend(partial.get("main_fragments", []))
        result["failures_and_rage"].extend(partial.get("failures_and_rage", []))
        result["topics_to_discuss"].extend(partial.get("topics_to_discuss", []))

    return result


async def summarize(messages: List[Dict], model: str = OPENAI_API_MODEL) -> Dict:
    """Разбивает сообщения на чанки, суммаризирует их и формирует объект с необходимыми темами."""
    chunks = split_messages(messages)

    if not chunks:
        error_message = "Нет сообщений для анализа"
        logging.error(f"Ошибка в summarize_chunk: {error_message}")
        raise Exception(error_message)

    partial_summaries = []
    for chunk in chunks:
        partial = await summarize_chunk(chunk, model=model)
        partial_summaries.append(partial)

    # Сразу склеиваем без повторного LLM
    result = merge_partial_summaries(partial_summaries)
    return await prepare_report(result)


def split_messages(messages: List[Dict], max_tokens: int = MAX_TOKENS_PER_CHUNK) -> List[List[Dict]]:
    """Делит сообщения на чанки так, чтобы по токенам не превышать лимит модели."""
    chunks = []
    current_chunk = []
    current_tokens = 0

    for msg in messages:
        text = msg.get("text", "")
        tokens = len(tokenizer.encode(str(f"{msg.get('username', 'Anonymous')}: {text}")))

        # если добавление этого сообщения превысит лимит токенов или сообщений
        if current_tokens + tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append(msg)
        current_tokens += tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


async def summarize_chunk(messages_chunk: List[Dict], model: str = OPENAI_API_MODEL) -> Dict:
    payload = "\n".join([f"{msg.get('username', 'Anonymous')}: {msg.get('text', '')}" for msg in messages_chunk])

    return await llm_call(model, SYSTEM_PROMPT, payload)


async def llm_call(model: str, prompt: str, content: str) -> Dict:
    try:
        response = await OPENAI_CLIENT.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            stream=False,
            response_format=RESPONSE_FORMAT
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        logging.error(f"Ошибка в summarize_chunk: {str(e)}")
        raise
