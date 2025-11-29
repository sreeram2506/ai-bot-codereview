from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from src.comment_mapper import CommentMapper
from src.bitbucket import AsyncBitbucketClient
from src.github import GitHubClient
from src.utils.logger import logger
from src.config import settings

app = FastAPI(title="AI PR Review Bot")
mapper = CommentMapper()

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        print(f"DEBUG: Received Webhook Payload: {payload.keys()}")
        print(f"DEBUG: Headers: {request.headers}")
    except Exception:
        print("DEBUG: Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Detect Provider
    headers = request.headers
    
    # --- Bitbucket ---
    if "X-Event-Key" in headers:
        event_key = headers.get("X-Event-Key")
        if event_key not in ["pullrequest:created", "pullrequest:updated"]:
            return {"message": "Event ignored"}
            
        try:
            pr = payload.get("pullrequest", {})
            repo = payload.get("repository", {})
            pr_id = pr.get("id")
            repo_slug = repo.get("slug")
            workspace = repo.get("workspace", {}).get("slug")
            
            if not pr_id or not repo_slug or not workspace:
                return {"message": "Invalid Bitbucket payload"}

            provider = AsyncBitbucketClient()
            background_tasks.add_task(mapper.process_review, provider, workspace, repo_slug, pr_id)
            return {"message": f"Bitbucket review queued for PR #{pr_id}"}
        except Exception as e:
            logger.error(f"Error processing Bitbucket webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    # --- GitHub ---
    elif "X-GitHub-Event" in headers:
        event_type = headers.get("X-GitHub-Event")
        if event_type == "pull_request":
            action = payload.get("action")
            if action not in ["opened", "reopened", "synchronize"]:
                return {"message": "Event ignored"}
            
            try:
                pr = payload.get("pull_request", {})
                repo = payload.get("repository", {})
                pr_id = pr.get("number")
                repo_name = repo.get("name")
                owner = repo.get("owner", {}).get("login")
                
                if not pr_id or not repo_name or not owner:
                    return {"message": "Invalid GitHub payload"}

                provider = GitHubClient()
                background_tasks.add_task(mapper.process_review, provider, owner, repo_name, pr_id)
                return {"message": f"GitHub review queued for PR #{pr_id}"}
            except Exception as e:
                logger.error(f"Error processing GitHub webhook: {e}")
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
             return {"message": "Event ignored"}

    else:
        return {"message": "Unknown webhook source"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT)
