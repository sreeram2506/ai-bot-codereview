import httpx
from src.config import settings
from src.utils.logger import logger
from src.interfaces import GitProvider

class GitHubClient(GitProvider):
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_pr_diff(self, workspace: str, repo_slug: str, pr_id: int) -> str:
        # workspace in GitHub context is usually the owner
        url = f"{self.base_url}/repos/{workspace}/{repo_slug}/pulls/{pr_id}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text

    async def post_comment(self, workspace: str, repo_slug: str, pr_id: int, content: str):
        # GitHub PRs are issues, so we post to the issues endpoint for general comments
        url = f"{self.base_url}/repos/{workspace}/{repo_slug}/issues/{pr_id}/comments"
        payload = {"body": content}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            if response.status_code != 201:
                logger.error(f"Failed to post GitHub comment: {response.text}")
                response.raise_for_status()
            return response.json()

    async def post_inline_comment(self, workspace: str, repo_slug: str, pr_id: int, content: str, path: str, line: int):
        # For inline comments, we need the commit_id. 
        # We'll fetch the PR details first to get the head commit SHA.
        pr_url = f"{self.base_url}/repos/{workspace}/{repo_slug}/pulls/{pr_id}"
        
        async with httpx.AsyncClient() as client:
            # 1. Get PR details for commit_id
            pr_resp = await client.get(pr_url, headers=self.headers)
            pr_resp.raise_for_status()
            pr_data = pr_resp.json()
            commit_id = pr_data["head"]["sha"]

            # 2. Post review comment
            url = f"{self.base_url}/repos/{workspace}/{repo_slug}/pulls/{pr_id}/comments"
            payload = {
                "body": content,
                "path": path,
                "line": line,
                "side": "RIGHT", # Assume commenting on the new version
                "commit_id": commit_id
            }
            
            response = await client.post(url, json=payload, headers=self.headers)
            if response.status_code != 201:
                logger.error(f"Failed to post GitHub inline comment: {response.text}")
                # Log but don't crash
            return response.json()
