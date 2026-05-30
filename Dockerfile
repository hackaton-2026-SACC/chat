FROM python:3.13-alpine as base

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT [ "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080" ]