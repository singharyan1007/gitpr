from fastapi import APIRouter, Header, HTTPException, Request

from app.domain.signature import verify_signature
from app.infra.queue import enqueue_review
from app.payloads import RELEVANT_ACTIONS, PullRequestPayload

router = APIRouter()


@router.post("/webhook")
async def webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    body = await request.body()
    settings = request.app.state.settings

    if not verify_signature(body, x_hub_signature_256, settings.webhook_secret):
        raise HTTPException(401, "Invalid signature")

    if x_github_event != "pull_request":
        return {"ok": True, "skipped": "not a pull_request event"}

    payload = PullRequestPayload.model_validate_json(body)
    if payload.action not in RELEVANT_ACTIONS:
        return {"ok": True, "skipped": payload.action}

    await enqueue_review(
        request.app.state.redis_pool,
        owner=payload.owner,
        repo=payload.repo,
        number=payload.number,
        head_sha=payload.head_sha,
    )
    return {"ok": True}
