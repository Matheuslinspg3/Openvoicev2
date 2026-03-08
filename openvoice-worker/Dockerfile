FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STORAGE_DIR=/app/storage \
    OUTPUT_DIR=/app/storage/outputs \
    CHECKPOINTS_DIR=/app/checkpoints_v2 \
    DEFAULT_LANGUAGE=pt \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    pkg-config \
    build-essential \
    git \
    curl \
    libsndfile1 \
    libavcodec-dev \
    libavformat-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN git clone --depth 1 https://github.com/myshell-ai/OpenVoice.git /opt/OpenVoice \
    && pip install --no-cache-dir -e /opt/OpenVoice \
    && pip install --no-cache-dir git+https://github.com/myshell-ai/MeloTTS.git \
    && python -m unidic download

COPY app /app/app
COPY scripts/start.sh /app/scripts/start.sh
RUN chmod +x /app/scripts/start.sh

RUN mkdir -p /app/storage/outputs /app/checkpoints_v2

EXPOSE 8001

CMD ["/app/scripts/start.sh"]
