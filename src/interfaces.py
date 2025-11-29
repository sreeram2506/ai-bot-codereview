from abc import ABC, abstractmethod

class GitProvider(ABC):
    @abstractmethod
    async def get_pr_diff(self, workspace: str, repo_slug: str, pr_id: int) -> str:
        pass

    @abstractmethod
    async def post_comment(self, workspace: str, repo_slug: str, pr_id: int, content: str):
        pass

    @abstractmethod
    async def post_inline_comment(self, workspace: str, repo_slug: str, pr_id: int, content: str, path: str, line: int):
        pass
