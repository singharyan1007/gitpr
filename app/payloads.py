from pydantic import BaseModel

RELEVANT_ACTIONS = {"opened", "synchronize"}


class PullRequestPayload(BaseModel):
    """Just the fields we actually use from GitHub's pull_request webhook body.

    GitHub's real payload has far more fields; Pydantic ignores the rest.
    """

    action: str
    number: int
    repository: dict
    pull_request: dict

    @property
    def owner(self) -> str:
        return self.repository["owner"]["login"]

    @property
    def repo(self) -> str:
        return self.repository["name"]

    @property
    def head_sha(self) -> str:
        return self.pull_request["head"]["sha"]
