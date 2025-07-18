"""
Модуль для хранения и поиска эмбеддингов сообщений (FAISS).
"""
import faiss
import numpy as np
from typing import List, Dict
from openai import AsyncOpenAI
from src.config.config import load_config

config = load_config()
RAG_CONFIG = config['RAG_CONFIG']
RAG_API_KEY = RAG_CONFIG.get('api_key')
RAG_BASE_URL = RAG_CONFIG.get('base_url')
RAG_MODEL = RAG_CONFIG.get('model', 'text-embedding-3-small')
RAG_CLIENT = AsyncOpenAI(api_key=RAG_API_KEY, base_url=RAG_BASE_URL)

class MessageVectorStore:
    def __init__(self):
        self.index = None
        self.messages: List[Dict] = []
        self.embeddings: List[np.ndarray] = []
        self.dim = None

    async def add_messages(self, messages: List[Dict]):
        # Формируем расширенный контекст для каждого сообщения
        texts = [self._message_context(msg) for msg in messages]
        embeddings = await self.get_embeddings(texts)
        if not embeddings:
            return
        if self.index is None:
            self.dim = len(embeddings[0])
            self.index = faiss.IndexFlatL2(self.dim)
        for emb, msg in zip(embeddings, messages):
            self.index.add(np.array([emb], dtype=np.float32))
            self.messages.append(msg)
            self.embeddings.append(emb)

    def _message_context(self, msg: Dict) -> str:
        """
        Формирует текстовый контекст для embedding, включая вложения.
        """
        parts = []
        username = msg.get('username', 'Anonymous')
        text = msg.get('text', '')
        parts.append(f"{username}: {text}")

        # Фото
        if msg.get('photo'):
            caption = msg.get('caption', '')
            parts.append(f"[Фото] {caption}")

        # Документ
        if msg.get('document'):
            doc_name = msg.get('document_name', 'Документ')
            caption = msg.get('caption', '')
            parts.append(f"[Документ: {doc_name}] {caption}")

        # Видео
        if msg.get('video'):
            caption = msg.get('caption', '')
            parts.append(f"[Видео] {caption}")

        # Голосовое
        if msg.get('voice'):
            parts.append("[Голосовое сообщение]")

        # Ссылки
        if msg.get('links'):
            for link in msg['links']:
                parts.append(f"[Ссылка] {link}")

        # Прочие вложения
        if msg.get('media_type'):
            parts.append(f"[Вложение: {msg['media_type']}] {msg.get('caption', '')}")

        return " ".join(parts)

    async def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        # Используем RAG API для получения эмбеддингов
        response = await RAG_CLIENT.embeddings.create(
            model=RAG_MODEL,
            input=texts
        )
        return [np.array(data.embedding, dtype=np.float32) for data in response.data]

    def search(self, query_emb: np.ndarray, top_k: int = 20) -> List[Dict]:
        D, I = self.index.search(np.array([query_emb], dtype=np.float32), top_k)
        return [self.messages[i] for i in I[0] if i < len(self.messages)]

    async def get_query_embedding(self, query: str) -> np.ndarray:
        response = await RAG_CLIENT.embeddings.create(
            model=RAG_MODEL,
            input=[query]
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
