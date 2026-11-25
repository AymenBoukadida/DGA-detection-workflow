# DGA classifier API

FastAPI service that scores domains as DGA-generated or benign. The model is trained
from generated data at container start, with fixed seeds. No network is needed at runtime.

## Run with Docker

```bash
docker build -t dga-ml-api .
docker run --rm -p 8000:8000 dga-ml-api
```

## Endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/model-info
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"domain":"google.com"}'
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"domains":["google.com","xj3kq9zvtbwrm7p2.com"]}'
```

## Tests

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest
```

On Linux and macOS use `.venv/bin/` instead of `.venv/Scripts/`.

## Layout

```text
app/        API and model pipeline
training/   deterministic dataset generator
tests/      pytest suite
```
