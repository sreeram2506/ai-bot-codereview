# AI-Powered Bitbucket PR Review Bot

This is a production-ready backend project that acts as an AI-powered Pull Request Review Bot for Bitbucket. It uses FastAPI, Bitbucket Webhooks, and the HuggingFace Inference API to analyze code changes and post both summary and inline comments.

## Features

- **Automated Code Review**: Listens for PR creation and updates.
- **AI Analysis**: Uses hosted HuggingFace models (e.g., Llama 3) to analyze diffs.
- **Inline Comments**: Posts specific issues directly on the relevant lines of code.
- **Summary Comment**: Provides a high-level overview of the changes.
- **Async Architecture**: Uses `httpx` and FastAPI background tasks for non-blocking operations.

## Prerequisites

- Python 3.9+
- A Bitbucket account
- A HuggingFace account (for API Key)

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

- `BITBUCKET_USERNAME`: Your Bitbucket username.
- `BITBUCKET_APP_PASSWORD`: Create one at [Bitbucket Settings](https://bitbucket.org/account/settings/app-passwords/).
  - **Required Permissions**: `Pull requests: Write`, `Repositories: Read`.
- `GITHUB_TOKEN`: (Optional) Personal Access Token for GitHub support.
  - **Required Scopes**: `repo`.
- `HF_API_KEY`: Get one at [HuggingFace Settings](https://huggingface.co/settings/tokens).
- `HF_MODEL`: The model ID to use (default: `meta-llama/Meta-Llama-3-70B-Instruct`).
- `PORT`: Port to run the server on (default: 8000).

## Running the Server

```bash
uvicorn src.main:app --reload --port 8000
```

Or using python directly:

```bash
python src/main.py
```

## Webhook Configuration

### Bitbucket
1. Go to your Bitbucket Repository Settings > Webhooks.
2. Click **Add Webhook**.
3. **Title**: AI Review Bot
4. **URL**: `https://your-server-domain.com/webhook`
5. **Triggers**: Select "Pull Request: Created" and "Pull Request: Updated".
6. Save.

### GitHub
1. Go to your GitHub Repository Settings > Webhooks.
2. Click **Add webhook**.
3. **Payload URL**: `https://your-server-domain.com/webhook`
4. **Content type**: `application/json`
5. **Which events would you like to trigger this webhook?**: Select **Let me select individual events**.
6. Check **Pull requests**.
7. Click **Add webhook**.


## How it Works

1. Bitbucket sends a webhook event when a PR is created or updated.
2. The bot fetches the unified diff of the PR.
3. The diff is parsed to identify changed files and line numbers.
4. The diff is sent to the HuggingFace Inference API with a prompt to identify issues.
5. The AI response is parsed.
6. A summary comment is posted on the PR.
7. Inline comments are posted for specific issues found in the changed lines.

## Project Structure

```
ai-review-bot/
  src/
    main.py           # FastAPI entry point & webhook handler
    bitbucket.py      # Bitbucket API client
    ai_engine.py      # HuggingFace API client
    diff_parser.py    # Diff parsing logic
    comment_mapper.py # Orchestrator for reviews
    config.py         # Configuration management
    utils/
      logger.py       # Logging utility
  requirements.txt
  .env.example
  README.md
```
# ai-bot-codereview
