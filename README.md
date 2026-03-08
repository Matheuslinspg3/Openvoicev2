# openvoice-worker

FastAPI worker service for local OpenVoice V2 voice cloning on a VPS.

## Features

- `GET /` basic service info
- `GET /health` health check
- `POST /clone` receives text + speaker reference wav path and generates cloned speech
- Writes generated files to local persistent storage (`/app/storage/outputs`)
- Validates mounted OpenVoice V2 checkpoints (`/app/checkpoints_v2`)

## Project layout

```bash
openvoice-worker/
  app/
    main.py
    routes/
      health.py
      clone.py
    services/
      clone_service.py
      storage.py
      config.py
    schemas/
      clone.py
  scripts/
    start.sh
  requirements.txt
  Dockerfile
  README.md
  .env.example
```

## Environment variables

Copy `.env.example` and adjust if needed:

```bash
STORAGE_DIR=/app/storage
OUTPUT_DIR=/app/storage/outputs
CHECKPOINTS_DIR=/app/checkpoints_v2
DEFAULT_LANGUAGE=pt
```

## Local setup (without Docker)

> Python 3.9 is required.

```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# install OpenVoice + MeloTTS (official approach)
git clone https://github.com/myshell-ai/OpenVoice.git
pip install -e ./OpenVoice
pip install git+https://github.com/myshell-ai/MeloTTS.git
python -m unidic download

mkdir -p /app/storage/outputs
mkdir -p /app/checkpoints_v2

uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## API

### `GET /`

Response:

```json
{
  "status": "ok",
  "service": "openvoice-worker"
}
```

### `GET /health`

Response:

```json
{
  "status": "ok"
}
```

### `POST /clone`

Request:

```json
{
  "text": "Olá, isso é um teste.",
  "speaker_wav_path": "/app/storage/voices/<voice_id>/reference.wav",
  "language": "pt"
}
```

Success response:

```json
{
  "status": "ok",
  "output_file": "<uuid>.wav",
  "output_path": "/app/storage/outputs/<uuid>.wav"
}
```

Common error response when checkpoints are missing:

```json
{
  "detail": "Missing checkpoints directory. Expected folder: /app/checkpoints_v2"
}
```

## Docker

### Build

```bash
docker build -t openvoice-worker .
```

### Run

```bash
docker run -d \
  --name openvoice-worker \
  -p 8001:8001 \
  --env-file .env \
  -v /your/host/storage:/app/storage \
  -v /your/host/checkpoints_v2:/app/checkpoints_v2 \
  openvoice-worker
```

## Storage mounts

For persistence, always mount:

- `/app/storage` for references and outputs
- `/app/checkpoints_v2` for OpenVoice V2 checkpoints

## If checkpoints are missing

1. Ensure host directory is mounted into `/app/checkpoints_v2`.
2. Confirm required files are inside that folder.
3. Re-run `POST /clone`.

The API will return a clear error including expected path: `/app/checkpoints_v2`.

## EasyPanel notes

- Expose container port `8001`.
- Configure environment variables from `.env.example`.
- Add two persistent volume mounts:
  - host path/data volume -> `/app/storage`
  - host path/data volume -> `/app/checkpoints_v2`
- Startup command can remain default (`/app/scripts/start.sh`).
- Add healthcheck endpoint: `/health`.
