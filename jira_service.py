import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()


class JiraService:

    def __init__(self):
        self.server = os.getenv("JIRA_SERVER_URL")
        self.email = os.getenv("JIRA_USER_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")

        self.client = JIRA(
            server=self.server,
            basic_auth=(self.email, self.token)
        )

    def add_comment(self, issue_key, comment_text):
        self.client.add_comment(issue_key, comment_text)
        print("Jira comment added")

    def transition_issue(self, issue_key, target_status):
        transitions = self.client.transitions(issue_key)

        for transition in transitions:
            if transition["name"].lower() == target_status.lower():
                self.client.transition_issue(
                    issue_key,
                    transition["id"]
                )
                print(f"Issue moved to {target_status}")
                return

        print(f"Transition to {target_status} not found")

    def add_comment_and_transition(self, issue_key, comment_text, target_status):
        self.add_comment(issue_key, comment_text)
        self.transition_issue(issue_key, target_status)

    def get_latest_comment_text(self, issue_key):
        issue = self.client.issue(issue_key)
        comments = issue.fields.comment.comments

        if not comments:
            return "No comment found. Build standard implementation."

        return comments[-1].body