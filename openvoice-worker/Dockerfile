FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STORAGE_DIR=/app/storage \
    OUTPUT_DIR=/app/storage/outputs \
    CHECKPOINTS_DIR=/app/checkpoints_v2 \
    DEFAULT_LANGUAGE=pt

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    build-essential \
    curl \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/myshell-ai/OpenVoice.git /opt/OpenVoice
RUN pip install --no-cache-dir -e /opt/OpenVoice
RUN pip install --no-cache-dir git+https://github.com/myshell-ai/MeloTTS.git
RUN python -m unidic download

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY scripts/start.sh /app/scripts/start.sh
RUN chmod +x /app/scripts/start.sh

RUN mkdir -p /app/storage/outputs /app/checkpoints_v2

EXPOSE 8001

CMD ["/app/scripts/start.sh"]
