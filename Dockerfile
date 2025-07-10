FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1. Copiar requirements y instalarlos
COPY src .
RUN pip install -r requirements.txt

CMD ["python", "gemini.py"]