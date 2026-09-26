import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings
from app.infra.cache import Cache

BASE = "https://api.github.com"


class RateLimited(Exception):
    def __init__(self, reset_at: int | None = None):
        self.reset_at = reset_at


class GitHubClient:
    def __init__(self,http:httpx.AsyncClient,settings:Settings,cache:Cache | None = None):
        self._http = http
        self._settings = settings
        self._cache = cache
        self._headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
        }
        self._diff_ttl=settings.diff_cache_ttl_seconds # Time to live in redis cache for the diff of a PR, in seconds. This is to avoid hitting the github api too often for the same PR.


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.TransportError)           
    )
    # This is a tenacity retry decorator that will retry the function if it raises a httpx.TransportError. It will stop after 3 attempts, and wait exponentially between attempts, with a minimum of 2 seconds and a maximum of 10 seconds.
    async def get_pr_diff(self, ownerName:str, repoName:str, prNumber:int)-> str:

        """
        Get the diff of a pull request from github. If the diff is cached in redis, return the cached diff. Otherwise, fetch the diff from github and cache it in redis.
        """    
        cache_key=f"pr_diff:{ownerName}/{repoName}/{prNumber}"
        if self._cache:
            cached_data = await self._cache.get_json(cache_key)
            if cached_data is not None:
                return cached_data["diff"]
            
        headers = {**self._headers, "Accept": "application/vnd.github.v3.diff"}

        # The **self._headers is a dictionary unpacking operator that merges the self._headers dictionary with the new Accept header. This is done to avoid overwriting the existing headers. 

        response = await self._http.get(f"{BASE}/repos/{ownerName}/{repoName}/pulls/{prNumber}", headers=headers)

        # wait for the response and if there is a rate limit error, throw an error with the reset time. The reset time is in seconds since epoch. We can use this to wait until the rate limit is reset before retrying the request. Later
        self._raise_for_rate_limit(response)
        response.raise_for_status()
        # If the response status code is not 2xx, raise an httpx.HTTPStatusError. This will be caught by the retry decorator and retried if it is a transport error.

        diff = response.text

        if self._cache:
            await self._cache.set_json(cache_key, {"diff": diff}, ttl=self._diff_ttl)

        return diff

    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.TransportError),
    )
    async def post_review_comments(self, ownerName:str, repoName:str, prNumber:int,body:str) -> None:
        """
        Post review comments to a pull request on github.
        """
        url = f"{BASE}/repos/{ownerName}/{repoName}/pulls/{prNumber}/reviews"
        data = {
            "body": "Automated review comments",
            "event": "COMMENT",
            "comments": body,
        }
        response = await self._http.post(url, headers=self._headers, json=data)
        response.raise_for_status()
        return response.json()


    async def get_rate_limit(self) -> dict:
        resp = await self._http.get(f"{BASE}/rate_limit", headers=self._headers)
        resp.raise_for_status()
        return resp.json()

    def _raise_for_rate_limit(self, resp: httpx.Response) -> None:
        if resp.status_code in (403, 429) and resp.headers.get("X-RateLimit-Remaining") == "0":
            reset_at = int(resp.headers.get("X-RateLimit-Reset", 0))
            raise RateLimited(reset_at=reset_at)



