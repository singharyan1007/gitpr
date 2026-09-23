# github-review-bot

A GitHub pull-request review bot: FastAPI webhook receiver -> Redis/arq queue
-> worker that fetches the diff, runs checks, posts a comment, and records
the review.

## Layout

```
app/
  main.py            FastAPI app + lifespan wiring
  config.py           pydantic-settings, one source of truth for env vars
  payloads.py          GitHub webhook payload models
  api/                 HTTP routes (webhook, history, health)
  domain/              pure logic: signature verification, diff parsing, checks
  infra/                GitHub client, DB, Redis cache, queue
  worker.py            arq job(s) that do the actual review
tests/
deploy/               Dockerfile + docker-compose.yml
```

## Quick start (local, no Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env          # then fill in GITHUB_TOKEN and WEBHOOK_SECRET
redis-server &                 # or: docker run -p 6379:6379 redis:7-alpine

uvicorn app.main:app --reload  # terminal 1: web
arq app.worker.WorkerSettings  # terminal 2: worker
```

The default `DATABASE_URL` is SQLite, so no Postgres is required to start.
Swap it for `postgresql+asyncpg://...` in `.env` when you outgrow it — no
code changes needed elsewhere.

Expose the webhook locally with `ngrok http 8000` and register the URL +
`WEBHOOK_SECRET` under your test repo's Settings -> Webhooks (content type
`application/json`, event: "Pull requests").

## Quick start (Docker)

```bash
cp .env.example .env   # fill in real values first
docker compose -f deploy/docker-compose.yml up --build
```

## Tests

```bash
pytest
```

`test_webhook.py` spins up the full app (including its Redis connection),
so run `redis-server` (or the compose `redis` service) before running the
full suite. `test_checks.py` and `test_signature.py` need nothing running.

## What's deliberately left out of this starting point

- Retry/backoff is wired via `tenacity` in `github_client.py`, and the
  worker requeues on rate-limit (`RateLimited`) — but there's no
  dead-letter queue yet beyond arq's `max_tries` cutoff.
- No Alembic migrations — `init_db()` just calls `create_all()`. Add
  Alembic once the schema needs to evolve without dropping data.
- No structured JSON request-id/delivery-id correlation in logs yet —
  `logging_config.py` is a minimal starting point.
- `domain/diff.py` is a hand-rolled parser good enough for the checks in
  this starter; swap it for the `unidiff` package if you need hunk-level
  detail (line numbers, renames, binary files).
