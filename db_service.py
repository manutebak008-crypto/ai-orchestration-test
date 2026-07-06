from datetime import datetime
from db import SessionLocal
from models import OrchestrationSession, AgentRun


class DBService:

    def create_session(self, jira_story_key):
        db = SessionLocal()

        session = OrchestrationSession(
            jira_story_key=jira_story_key,
            current_stage="WEBHOOK_RECEIVED",
            status="STARTED"
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        session_id = session.id
        db.close()

        return session_id

    def update_session(
        self,
        session_id,
        status=None,
        current_stage=None,
        tokens_used=None,
        github_branch=None,
        pr_url=None,
        error_message=None
    ):
        db = SessionLocal()

        session = db.query(OrchestrationSession).filter(
            OrchestrationSession.id == session_id
        ).first()

        if session:
            if status:
                session.status = status

            if current_stage:
                session.current_stage = current_stage

            if tokens_used is not None:
                session.total_tokens_used += tokens_used

            if github_branch:
                session.github_branch = github_branch

            if pr_url:
                session.pr_url = pr_url

            if error_message:
                session.error_message = error_message

            session.updated_at = datetime.utcnow()

            db.commit()

        db.close()

    def create_agent_run(
        self,
        session_id,
        jira_story_key,
        agent_name,
        stage,
        status="STARTED",
        tokens_used=0
    ):
        db = SessionLocal()

        run = AgentRun(
            session_id=session_id,
            jira_story_key=jira_story_key,
            agent_name=agent_name,
            stage=stage,
            status=status,
            tokens_used=tokens_used
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        run_id = run.id
        db.close()

        return run_id

    def complete_agent_run(
        self,
        run_id,
        status,
        tokens_used=0,
        github_branch=None,
        pr_url=None,
        error_message=None
    ):
        db = SessionLocal()

        run = db.query(AgentRun).filter(
            AgentRun.id == run_id
        ).first()

        if run:
            run.status = status
            run.tokens_used = tokens_used
            run.github_branch = github_branch
            run.pr_url = pr_url
            run.error_message = error_message
            run.completed_at = datetime.utcnow()

            db.commit()

        db.close()