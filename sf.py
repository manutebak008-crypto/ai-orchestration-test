from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from jira_service import JiraService
from logger_service import AgentLogger
from agent_tracker import AgentTracker

from db import Base, engine, SessionLocal
from db_service import DBService
from models import OrchestrationSession, AgentRun

from agent.orchestration_agent import OrchestrationAgent

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

jira_service = JiraService()
agent_logger = AgentLogger()
db_service = DBService()
orchestration_agent = OrchestrationAgent()

latest_status = {}


def update_status(issue_key, agent, status, message):
    data = agent_logger.log(issue_key, agent, status, message)
    latest_status[issue_key] = data
    AgentTracker.update(issue_key, data)
    return data


def run_orchestration(issue_key, session_id):
    try:
        update_status(issue_key, "Orchestration Agent", "STARTED", "Workflow started")

        orchestration_run_id = db_service.create_agent_run(
            session_id=session_id,
            jira_story_key=issue_key,
            agent_name="Orchestration Agent",
            stage="ORCHESTRATION",
            status="STARTED",
            tokens_used=0
        )

        db_service.update_session(
            session_id=session_id,
            status="RUNNING",
            current_stage="ORCHESTRATION_STARTED"
        )

        result = orchestration_agent.run(issue_key)

        planning_tokens = result["planning"]["tokens_used"]
        build_tokens = result["build"]["tokens_used"]
        review_tokens = result["review"]["tokens_used"]

        pr_url = result["build"]["pr_url"]
        github_branch = result["build"]["github_branch"]
        total_tokens = result["total_tokens_used"]

        db_service.complete_agent_run(
            run_id=orchestration_run_id,
            status="SUCCESS",
            tokens_used=total_tokens,
            github_branch=github_branch,
            pr_url=pr_url
        )

        db_service.create_agent_run(
            session_id=session_id,
            jira_story_key=issue_key,
            agent_name="Planning Agent",
            stage="PLAN",
            status="SUCCESS",
            tokens_used=planning_tokens
        )

        db_service.create_agent_run(
            session_id=session_id,
            jira_story_key=issue_key,
            agent_name="Build Agent",
            stage="BUILD",
            status="SUCCESS",
            tokens_used=build_tokens
        )

        db_service.create_agent_run(
            session_id=session_id,
            jira_story_key=issue_key,
            agent_name="Review Agent",
            stage="REVIEW",
            status="SUCCESS",
            tokens_used=review_tokens
        )

        jira_service.add_comment_and_transition(
            issue_key,
            f"🚀 Multi-Agent Build completed successfully.\n\n"
            f"Pull Request:\n{pr_url}\n\n"
            f"Branch:\n{github_branch}\n\n"
            f"Total Tokens Used: {total_tokens}",
            "Agent Review"
        )

        db_service.update_session(
            session_id=session_id,
            status="SUCCESS",
            current_stage="AGENT_REVIEW",
            tokens_used=total_tokens,
            github_branch=github_branch,
            pr_url=pr_url
        )

        update_status(
            issue_key,
            "Orchestration Agent",
            "SUCCESS",
            f"Workflow completed. PR: {pr_url}"
        )

    except Exception as e:
        error_msg = str(e)

        db_service.update_session(
            session_id=session_id,
            status="FAILED",
            current_stage="ORCHESTRATION_FAILED",
            error_message=error_msg
        )

        update_status(issue_key, "Orchestration Agent", "FAILED", error_msg)


@app.get("/")
def home():
    return {
        "status": "server running",
        "service": "AI Multi-Agent Orchestrator"
    }


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/dashboard/ui", response_class=HTMLResponse)
def dashboard_ui():
    return """
    <html>
        <head>
            <title>AI Agent Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f4f6f8;
                    padding: 30px;
                }
                h1 { color: #222; }
                .card {
                    background: white;
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                a {
                    display: block;
                    margin: 10px 0;
                    font-size: 18px;
                    color: #0052cc;
                    text-decoration: none;
                }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>AI Multi-Agent Dashboard</h1>

            <div class="card">
                <h2>System Health</h2>
                <a href="/health">Health Check</a>
            </div>

            <div class="card">
                <h2>Sessions</h2>
                <a href="/dashboard/sessions">All Orchestration Sessions</a>
                <a href="/dashboard/story/KAN-3">KAN-3 Story Details</a>
            </div>

            <div class="card">
                <h2>Agent Monitoring</h2>
                <a href="/agent/all-status">All Agent Status</a>
                <a href="/stories">Tracked Stories</a>
                <a href="/agent/logs">Agent Logs</a>
            </div>
        </body>
    </html>
    """


@app.get("/agent/status/{issue_key}")
def get_agent_status(issue_key: str):
    return latest_status.get(issue_key, {"message": "No status found"})


@app.get("/agent/all-status")
def get_all_agent_status():
    return latest_status


@app.get("/stories")
def get_all_stories():
    return AgentTracker.get_all()


@app.get("/stories/{issue_key}")
def get_story_status(issue_key: str):
    return AgentTracker.get(issue_key)


@app.get("/agent/logs")
def get_logs():
    try:
        with open("agent_logs.log", "r", encoding="utf-8") as file:
            return {"logs": file.readlines()[-100:]}
    except FileNotFoundError:
        return {"logs": []}


@app.get("/dashboard/sessions")
def dashboard_sessions():
    db = SessionLocal()

    rows = db.query(OrchestrationSession).order_by(
        OrchestrationSession.id.desc()
    ).all()

    data = [
        {
            "id": row.id,
            "jira_story_key": row.jira_story_key,
            "current_stage": row.current_stage,
            "status": row.status,
            "total_tokens_used": row.total_tokens_used,
            "github_branch": row.github_branch,
            "pr_url": row.pr_url,
            "error_message": row.error_message,
            "created_at": str(row.created_at),
            "updated_at": str(row.updated_at)
        }
        for row in rows
    ]

    db.close()
    return data


@app.get("/dashboard/story/{issue_key}")
def dashboard_story(issue_key: str):
    db = SessionLocal()

    sessions = db.query(OrchestrationSession).filter(
        OrchestrationSession.jira_story_key == issue_key
    ).order_by(OrchestrationSession.id.desc()).all()

    runs = db.query(AgentRun).filter(
        AgentRun.jira_story_key == issue_key
    ).order_by(AgentRun.id.desc()).all()

    data = {
        "sessions": [
            {
                "id": s.id,
                "jira_story_key": s.jira_story_key,
                "current_stage": s.current_stage,
                "status": s.status,
                "total_tokens_used": s.total_tokens_used,
                "github_branch": s.github_branch,
                "pr_url": s.pr_url,
                "error_message": s.error_message,
                "created_at": str(s.created_at),
                "updated_at": str(s.updated_at)
            }
            for s in sessions
        ],
        "agent_runs": [
            {
                "id": r.id,
                "session_id": r.session_id,
                "jira_story_key": r.jira_story_key,
                "agent_name": r.agent_name,
                "stage": r.stage,
                "status": r.status,
                "tokens_used": r.tokens_used,
                "github_branch": r.github_branch,
                "pr_url": r.pr_url,
                "error_message": r.error_message,
                "started_at": str(r.started_at),
                "completed_at": str(r.completed_at)
            }
            for r in runs
        ]
    }

    db.close()
    return data


@app.post("/webhook/jira")
async def jira_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    issue_key = payload.get("issue", {}).get("key")
    changelog_items = payload.get("changelog", {}).get("items", [])

    for item in changelog_items:
        if item.get("field") == "status":
            target_status = item.get("toString")
            print("Issue:", issue_key)
            print("Moved to:", target_status)

            if target_status and target_status.lower() == "to build":
                update_status(
                    issue_key,
                    "Webhook Router",
                    "RECEIVED",
                    "Jira ticket moved to To Build"
                )

                session_id = db_service.create_session(issue_key)

                background_tasks.add_task(
                    run_orchestration,
                    issue_key,
                    session_id
                )

            break

    return {
        "status": "event_received",
        "issue_key": issue_key
    }