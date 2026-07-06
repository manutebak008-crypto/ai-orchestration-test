import os
from jira import JIRA
from dotenv import load_dotenv


load_dotenv()


class JiraService:


    def __init__(self):

        self.client = JIRA(
            server=os.getenv("JIRA_SERVER_URL"),

            basic_auth=(
                os.getenv("JIRA_USER_EMAIL"),
                os.getenv("JIRA_API_TOKEN")
            )
        )



    def fetch_story_context(self, issue_key):

        issue = self.client.issue(issue_key)


        return {

            "title":
            issue.fields.summary,


            "description":
            issue.fields.description,


            "epic_summary":
            "No Epic"

        }



    def add_comment_and_transition(
        self,
        issue_key,
        comment_text
    ):


        self.client.add_comment(
            issue_key,
            comment_text
        )


        transitions = self.client.transitions(issue_key)


        for t in transitions:

            if t["name"] == "Review Plan":

                self.client.transition_issue(
                    issue_key,
                    t["id"]
                )

                break