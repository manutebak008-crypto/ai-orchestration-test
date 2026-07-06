from git_worker import GitWorkspaceWorker


class BuildAgent:

    def __init__(self):
        self.git_worker = GitWorkspaceWorker()

    def run(self, issue_key):
        print("Build Agent running for:", issue_key)

        pr_url, branch_name = self.git_worker.execute_automated_build(
            issue_key
        )

        tokens_used = 150

        return {
            "pr_url": pr_url,
            "github_branch": branch_name,
            "tokens_used": tokens_used
        }