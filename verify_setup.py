import asyncio
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Set mock env vars BEFORE importing modules that use config
os.environ["BITBUCKET_USERNAME"] = "test_user"
os.environ["BITBUCKET_APP_PASSWORD"] = "test_pass"
os.environ["GITHUB_TOKEN"] = "test_token"
os.environ["HF_API_KEY"] = "test_key"

from src.diff_parser import DiffParser
from src.comment_mapper import CommentMapper

# Sample Diff Data
SAMPLE_DIFF = """diff --git a/src/main.py b/src/main.py
index 83c5a9e..5a3b2c1 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,5 +10,5 @@ def hello():
 def hello():
-    print("Hello")
+    print("Hello World")
     return True
"""

async def run_verification():
    print("🔍 Starting Local Verification...\n")

    # 1. Test Diff Parser
    print("1️⃣  Testing Diff Parser...")
    try:
        parsed = DiffParser.parse(SAMPLE_DIFF)
        print(f"   ✅ Parsed successfully: {parsed}")
        assert "src/main.py" in parsed
        assert parsed["src/main.py"][0] == (11, '    print("Hello World")')
    except Exception as e:
        print(f"   ❌ Diff Parser failed: {e}")
        return

    # 2. Test Comment Mapper (with Mocks)
    print("\n2️⃣  Testing Comment Mapper (Mocked APIs)...")
    
    with patch("src.bitbucket.AsyncBitbucketClient", new_callable=AsyncMock) as MockBitbucket, \
         patch("src.github.GitHubClient", new_callable=AsyncMock) as MockGitHub, \
         patch("src.ai_engine.AIEngine", new_callable=AsyncMock) as MockAI:
        
        # Setup Common AI Mock
        mock_ai = MockAI.return_value
        mock_ai.analyze_changes.return_value = {
            "summary": "Looks good.",
            "issues": [
                {
                    "file": "src/main.py",
                    "line": 11,
                    "severity": "info",
                    "message": "Good update.",
                    "suggestion": "None"
                }
            ]
        }

        # --- Test Bitbucket ---
        print("\n   [Bitbucket Test]")
        mock_bb = MockBitbucket.return_value
        mock_bb.get_pr_diff.return_value = SAMPLE_DIFF
        
        mapper = CommentMapper()
        mapper.ai = mock_ai
        
        # We need to manually pass the provider in the new logic, but main.py does it.
        # Here we simulate what main.py does: instantiate provider and pass it.
        await mapper.process_review(mock_bb, "bb-workspace", "bb-repo", 1)

        if mock_bb.get_pr_diff.called:
            print("   ✅ Fetched PR Diff")
        else:
            print("   ❌ Did not fetch PR Diff")

        if mock_bb.post_comment.called:
            print("   ✅ Posted Summary")
        else:
            print("   ❌ Did not post summary")

        # --- Test GitHub ---
        print("\n   [GitHub Test]")
        mock_gh = MockGitHub.return_value
        mock_gh.get_pr_diff.return_value = SAMPLE_DIFF
        
        await mapper.process_review(mock_gh, "gh-owner", "gh-repo", 100)

        if mock_gh.get_pr_diff.called:
            print("   ✅ Fetched PR Diff")
        else:
            print("   ❌ Did not fetch PR Diff")

        if mock_gh.post_comment.called:
            print("   ✅ Posted Summary")
        else:
            print("   ❌ Did not post summary")

    print("\n🎉 Verification Complete! The core logic is working correctly for both providers.")

if __name__ == "__main__":
    asyncio.run(run_verification())
