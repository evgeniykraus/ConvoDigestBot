# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

COPY . .

# По умолчанию запускать оба процесса (бот и планировщик)
CMD ["python", "main.py"]
# Для запуска только бота: docker run ... python main.py bot
# Для запуска только планировщика: docker run ... python main.py scheduler