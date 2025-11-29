from src.interfaces import GitProvider
from src.ai_engine import AIEngine
from src.diff_parser import DiffParser
from src.utils.logger import logger

class CommentMapper:
    def __init__(self):
        self.ai = AIEngine()

    async def process_review(self, provider: GitProvider, workspace: str, repo_slug: str, pr_id: int):
        logger.info(f"Starting review for PR #{pr_id} in {workspace}/{repo_slug}")
        
        # 1. Fetch Diff
        try:
            diff_text = await provider.get_pr_diff(workspace, repo_slug, pr_id)
        except Exception as e:
            logger.error(f"Failed to fetch diff: {e}")
            return

        # 2. Parse Diff
        parsed_diff = DiffParser.parse(diff_text)
        if not parsed_diff:
            logger.info("No relevant changes found to analyze.")
            return

        # 3. Analyze with AI
        ai_response = await self.ai.analyze_changes(parsed_diff)
        
        # 4. Post Summary
        summary = ai_response.get("summary", "No summary provided.")
        await provider.post_comment(workspace, repo_slug, pr_id, f"**AI Review Summary**\n\n{summary}")

        # 5. Post Inline Comments
        issues = ai_response.get("issues", [])
        for issue in issues:
            file_path = issue.get("file")
            line_number = issue.get("line")
            message = f"**[{issue.get('severity', 'info').upper()}]** {issue.get('message')}\n\n*Suggestion:* {issue.get('suggestion')}"
            
            # Verify that the file and line exist in our parsed diff to ensure valid inline comment
            if file_path in parsed_diff:
                # Check if line number is valid (exists in the added lines)
                # This is a basic check. In a real scenario, we might want to be more flexible 
                # or map to the nearest valid line, but for now we stick to strict matching
                # to avoid API errors.
                valid_lines = [l[0] for l in parsed_diff[file_path]]
                if line_number in valid_lines:
                    await provider.post_inline_comment(
                        workspace, repo_slug, pr_id, message, file_path, line_number
                    )
                else:
                    logger.warning(f"Skipping inline comment: Line {line_number} in {file_path} not found in added lines.")
            else:
                logger.warning(f"Skipping inline comment: File {file_path} not found in parsed diff.")
        
        logger.info(f"Completed review for PR #{pr_id}")
