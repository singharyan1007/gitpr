from fastapi import APIRouter, Request, Response, Header, HTTPException


from app.domain.signature import verify_signature
from app.domain.checks import run_all_checks, format_findings
from app.infra.github_client import GitHubClient
from app.payloads import PullRequestPayload, RELEVANT_ACTIONS

router = APIRouter()

@router.post("/webhook")
async def webhook(
    request:Request,
    x_hub_signature_256:str | None = Header(default=None),
    x_github_event:str | None = Header(default=None)
):
    """
    Endpoint to receive GitHub webhook events. It verifies the signature, checks if the event is relevant, and runs checks on pull requests. If any findings are detected, it posts a comment on the pull request.
    """

    """
    "Create a parameter called x_hub_signature_256. It should contain a string if GitHub sends the signature header, otherwise it can be None. Get this value from the HTTP request headers."
    """

    body=await request.body() # contains raw bytes from Github webhook payload
    settings= request.app.state.settings
    # the request object first gets the fastapi application object, then gets the settings object from the application state


    # Verify the signature of the incoming request
    if not verify_signature(body, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    if x_github_event != "pull_request":
        return Response(status_code=204, content="Not a pull request event")  # No Content for irrelevant events

    payload = PullRequestPayload.model_validate_json(body)
    if payload.action not in RELEVANT_ACTIONS:
        return Response(status_code=204, content="Irrelevant pull request action")  # No Content for irrelevant actions

    # Call the GitHubClient object
    gh = GitHubClient(request.app.state.http, settings)

    # Get the diff of the pull request
    diff = await gh.get_pr_diff(payload.owner, payload.repo, payload.number)

    # Run all checks on the diff
    findings = run_all_checks(diff)

    return {"ok":True, "findings": format_findings(findings)}


