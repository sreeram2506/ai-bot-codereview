import httpx
import json
import asyncio
from typing import Dict, Any
from src.config import settings
from src.utils.logger import logger


class AIEngine:
    def __init__(self):
        # Make sure your HF token has "Inference Providers" enabled
        self.model = settings.HF_MODEL

        # NEW Router API Endpoint
        self.base_url = "https://router.huggingface.co/v1/chat/completions"

        self.headers = {
            "Authorization": f"Bearer {settings.HF_API_KEY}",
            "Content-Type": "application/json"
        }

    async def analyze_changes(self, diff_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._construct_prompt(diff_data)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.2
        }

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(
                        self.base_url,
                        headers=self.headers,
                        json=payload
                    )

                    response.raise_for_status()
                    data = response.json()

                    generated_text = data["choices"][0]["message"]["content"]
                    return self._parse_json_response(generated_text)

            except Exception as e:
                logger.error(f"[Attempt {attempt+1}] HF Router API error: {e}")
                await asyncio.sleep(1.5)

        return {"summary": "AI Analysis failed after retries.", "issues": []}

    def _construct_prompt(self, diff_data: Dict[str, Any]) -> str:
        diff_str = ""

        for file, lines in diff_data.items():
            diff_str += f"\nFile: {file}\n"
            for line_num, content in lines:
                diff_str += f"{line_num}: {content}\n"

        return f"""
You are an expert code reviewer. Analyze the following code diff and provide a review.
Focus on correctness, bugs, security issues, performance issues, and best coding practices.

Diff Input:
{diff_str}

Return ONLY valid JSON:

{{
  "summary": "text summary in markdown",
  "issues": [
    {{
      "file": "path/to/file",
      "line": 123,
      "severity": "error|warning|info",
      "message": "issue description",
      "suggestion": "how to fix it"
    }}
  ]
}}

If no issues:

{{
  "summary": "summary",
  "issues": []
}}
"""

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        try:
            clean = text.strip()

            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]

            parsed = json.loads(clean)

            if "issues" not in parsed:
                parsed["issues"] = []

            return parsed

        except Exception as e:
            logger.error(f"Failed to parse JSON AI response: {e}")
            logger.error(f"Raw Text: {text}")
            return {
                "summary": "Failed to parse AI response.",
                "issues": []
            }
