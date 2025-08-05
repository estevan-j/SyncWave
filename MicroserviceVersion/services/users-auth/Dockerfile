FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

COPY services/users-auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY shared/logging ./shared/logging
RUN pip install -e ./shared/logging

# Copia el código de la app y el run.py fuera de /app
COPY services/users-auth/app/ ./app/
COPY services/users-auth/run.py ./

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    SERVICE_NAME=users-auth \
    SERVICE_VERSION=1.0.0 \
    LOG_LEVEL=WARNING

CMD ["python", "run.py"]