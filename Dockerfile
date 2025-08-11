# ========= build image =========
FROM python:3.11-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Collect static at build time (no user input)
RUN python manage.py collectstatic --noinput

# Gunicorn config via env or default below
ENV PORT=8000 \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=600

# Expose
EXPOSE 8000

# Startup: migrate then run gunicorn
CMD sh -c "python manage.py migrate --noinput && \
           gunicorn bot_testing.wsgi:application \
             --bind 0.0.0.0:${PORT} \
             --workers ${GUNICORN_WORKERS} \
             --threads ${GUNICORN_THREADS} \
             --timeout ${GUNICORN_TIMEOUT} \
             --access-logfile - --error-logfile -"
