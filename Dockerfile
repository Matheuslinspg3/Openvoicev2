FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STORAGE_DIR=/app/storage \
    OUTPUT_DIR=/app/storage/outputs \
    CHECKPOINTS_DIR=/app/checkpoints_v2 \
    DEFAULT_LANGUAGE=pt \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 1) System dependencies for OpenVoice/MeloTTS + PyAV/FFmpeg build
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    pkg-config \
    git \
    build-essential \
    python3-dev \
    libavcodec-dev \
    libavformat-dev \
    libavdevice-dev \
    libavutil-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    curl \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 2) Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# 3) Ensure build tooling exists before compiling native deps (e.g. PyAV)
RUN python -m pip install --no-cache-dir --upgrade setuptools wheel "Cython<3"

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 4) Install PyAV with pinned Cython in non-isolated build environment
RUN pip install --no-cache-dir --no-build-isolation av==10.0.0

# 5) Clone OpenVoice
RUN git clone --depth 1 https://github.com/myshell-ai/OpenVoice.git /opt/OpenVoice

# 6) Install OpenVoice
RUN pip install --no-cache-dir --no-build-isolation -e /opt/OpenVoice

# 7) Install MeloTTS
RUN pip install --no-cache-dir git+https://github.com/myshell-ai/MeloTTS.git

# 8) Download UniDic dictionary used by MeloTTS
RUN python -m unidic download

COPY app /app/app
COPY scripts/start.sh /app/scripts/start.sh
RUN chmod +x /app/scripts/start.sh

RUN mkdir -p /app/storage/outputs /app/checkpoints_v2

EXPOSE 8001

CMD ["/app/scripts/start.sh"]
