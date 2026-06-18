FROM python:3.13-alpine AS base

WORKDIR /app

# Download licitacoes.db from GitHub LFS via raw content API
RUN apk add --no-cache curl && \
    curl -L --max-time 300 -o licitacoes.db https://raw.githubusercontent.com/hackaton-2026-SACC/chat/main/licitacoes.db && \
    apk del curl

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT [ "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080" ]