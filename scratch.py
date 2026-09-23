import asyncio
import httpx

from app.config import get_settings
from app.infra.github_client import GitHubClient
from app.domain.checks import run_all_checks, format_findings


async def main():
    settings = get_settings()
    async with httpx.AsyncClient(timeout=15) as http:
        gh = GitHubClient(http, settings)
        diff = await gh.get_pr_diff("fastapi", "fastapi", 1)

    print(f"--- diff is {len(diff)} chars ---")
    findings = run_all_checks(diff)
    print(format_findings(findings))


asyncio.run(main())