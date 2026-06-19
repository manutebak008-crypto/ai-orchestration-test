import os
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv

from jira_service import JiraService
from git_worker import GitWorkspaceWorker

load_dotenv()

app = FastAPI()

jira_service = JiraService()
git_worker = GitWorkspaceWorker()


def run_build_agent(issue_key):
    try:
        print("Running Build Agent for:", issue_key)

        pr_url = git_worker.execute_automated_build(issue_key)

        jira_service.add_comment_and_transition(
            issue_key,
            f"🚀 Build completed successfully.\n\nPull Request:\n{pr_url}",
            "Agent Review"
        )

        print("Build Agent completed for:", issue_key)

    except Exception as e:
        print("ERROR OCCURRED:")
        print(str(e))


@app.get("/")
def home():
    return {"status": "server running"}


@app.post("/webhook/jira")
async def jira_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    issue_key = payload.get("issue", {}).get("key")
    print("Issue:", issue_key)

    changelog_items = payload.get("changelog", {}).get("items", [])

    for item in changelog_items:
        if item.get("field") == "status":
            target_status = item.get("toString")
            print("Moved to:", target_status)

            if target_status.lower() == "to build":
                background_tasks.add_task(run_build_agent, issue_key)

            break

    return {"status": "event_received"}