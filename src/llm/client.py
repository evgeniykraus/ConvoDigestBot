from typing import Optional, List, Dict
import logging
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from src.config.config import load_config
from src.llm.prompts import SYSTEM_PROMPT
from src.llm.vector_store import MessageVectorStore
from src.config.schemas import LLMResponse

config = load_config()
LLM_CONFIG = config['LLM_CONFIG']
RAG_CONFIG = config['RAG_CONFIG']


def get_langchain_llm(model: Optional[str] = None):
    """Возвращает LangChain LLM-объект в зависимости от провайдера с поддержкой JSON-формата."""
    provider = LLM_CONFIG['provider']
    model_name = model or LLM_CONFIG['model']
    base_url = LLM_CONFIG.get('base_url')
    api_key = LLM_CONFIG.get('api_key')
    output_parser = JsonOutputParser(pydantic_object=LLMResponse)

    if provider == 'openai':
        llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model_name,
            temperature=0.2,
        )
        try:
            # Пробуем использовать with_structured_output для моделей, поддерживающих JSON Schema
            return llm.with_structured_output(LLMResponse, method="json_schema")
        except Exception as e:
            logging.warning(
                f"with_structured_output not supported for {model_name}: {e}. Falling back to JsonOutputParser.")
            return llm | output_parser
    elif provider == 'ollama':
        llm = ChatOllama(
            base_url=base_url or 'http://localhost:11434',
            model=model_name,
            temperature=0.2,
        )
        # Для Ollama всегда используем JsonOutputParser с промптом
        return llm | output_parser
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


async def summarize(messages: List[Dict], model: str = None) -> Dict:
    """Разбивает сообщения на чанки, суммаризирует их и формирует объект с необходимыми темами."""
    # --- RAG: Индексация и поиск релевантных сообщений ---
    vector_store = MessageVectorStore()
    await vector_store.add_messages(messages)
    query = RAG_CONFIG['query']
    query_emb = await vector_store.get_query_embedding(query)
    relevant_messages = vector_store.search(query_emb, top_k=RAG_CONFIG['top_k'])
    if not relevant_messages:
        error_message = "Нет релевантных сообщений для анализа"
        logging.error(f"Ошибка в RAG summarize: {error_message}")
        raise Exception(error_message)
    payload = "\n".join([f"{msg.get('username', 'Anonymous')}: {msg.get('text', '')}" for msg in relevant_messages])
    return await llm_call(model or LLM_CONFIG.get('model', 'gpt-3.5-turbo'), SYSTEM_PROMPT, payload)


async def llm_call(model: str, prompt: str, content: str):
    """Универсальный вызов LLM через LangChain."""
    llm = get_langchain_llm(model)
    messages = [SystemMessage(content=prompt), HumanMessage(content=content)]
    try:
        response = await llm.ainvoke(messages)
        return response.dict() if hasattr(response, 'dict') else response
    except Exception as e:
        logging.error(f"Ошибка при вызове LLM: {e}")
        raise Exception(f"Не удалось получить валидный JSON-ответ: {e}")
