from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/history/{owner}/{repo}")
async def history(owner: str, repo: str, request: Request):
    reviews = await request.app.state.repository.list_for_repo(owner, repo)
    return [
        {
            "pr": r.pr_number,
            "sha": r.head_sha,
            "findings": r.findings_count,
            "at": r.created_at,
        }
        for r in reviews
    ]


@router.get("/stats/{owner}/{repo}")
async def stats(owner: str, repo: str, request: Request):
    return await request.app.state.repository.stats_for_repo(owner, repo)
