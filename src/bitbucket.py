import httpx
from src.config import settings
from src.utils.logger import logger
from src.interfaces import GitProvider

class AsyncBitbucketClient(GitProvider):
    def __init__(self):
        self.base_url = "https://api.bitbucket.org/2.0"
        self.auth = (settings.BITBUCKET_USERNAME, settings.BITBUCKET_APP_PASSWORD)

    async def get_pr_diff(self, workspace: str, repo_slug: str, pr_id: int) -> str:
        url = f"{self.base_url}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/diff"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, auth=self.auth)
            response.raise_for_status()
            return response.text

    async def post_comment(self, workspace: str, repo_slug: str, pr_id: int, content: str):
        url = f"{self.base_url}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
        payload = {
            "content": {
                "raw": content
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, auth=self.auth)
            if response.status_code != 201:
                logger.error(f"Failed to post comment: {response.text}")
                response.raise_for_status()
            return response.json()

    async def post_inline_comment(self, workspace: str, repo_slug: str, pr_id: int, content: str, path: str, line: int):
        url = f"{self.base_url}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"
        payload = {
            "content": {
                "raw": content
            },
            "inline": {
                "path": path,
                "to": line
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, auth=self.auth)
            if response.status_code != 201:
                logger.error(f"Failed to post inline comment: {response.text}")
                # We might not want to raise here to avoid failing the whole review for one bad comment
                # but for now let's log it.
            return response.json()
