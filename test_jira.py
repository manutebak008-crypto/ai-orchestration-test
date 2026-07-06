from jira_service import JiraService

jira = JiraService()

pr_url = "https://github.com/manutebak008-crypto/ai-orchestration-test/pull/2"

jira.add_comment(
    "KAN-3",
    f"🚀 Build completed successfully.\n\nPull Request:\n{pr_url}"
)