from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from db import Base


class OrchestrationSession(Base):
    __tablename__ = "orchestration_sessions"

    id = Column(Integer, primary_key=True, index=True)
    jira_story_key = Column(String, index=True)
    current_stage = Column(String, default="RECEIVED")
    status = Column(String, default="STARTED")
    total_tokens_used = Column(Integer, default=0)
    github_branch = Column(String, nullable=True)
    pr_url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    jira_story_key = Column(String, index=True)
    agent_name = Column(String)
    stage = Column(String)
    status = Column(String)
    tokens_used = Column(Integer, default=0)
    github_branch = Column(String, nullable=True)
    pr_url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)