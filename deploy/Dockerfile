FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

FROM base AS deps
COPY pyproject.toml .
RUN pip install --upgrade pip && pip install .

FROM deps AS runtime
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
