FROM python:3.13-alpine AS base

WORKDIR /app

# COPY licitacoes.db . (Removido ou comentado porque está sendo ignorado no envio)

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT [ "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080" ]