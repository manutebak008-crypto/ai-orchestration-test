import os
import time
from git import Repo
from github import Github
from dotenv import load_dotenv

load_dotenv()


class GitWorkspaceWorker:

    def __init__(self):
        self.owner = os.getenv("TARGET_REPO_OWNER")
        self.repo_name = os.getenv("TARGET_REPO_NAME")
        self.token = os.getenv("GITHUB_TOKEN")

        print("OWNER =", self.owner)
        print("REPO =", self.repo_name)

    def clone_repo(self, issue_key):
        folder = f"workspace_{issue_key}_{int(time.time())}"

        url = (
            f"https://{self.token}"
            f"@github.com/"
            f"{self.owner}/"
            f"{self.repo_name}.git"
        )

        print("\nCloning repository...")
        print("URL:", f"https://github.com/{self.owner}/{self.repo_name}.git")
        print("Workspace:", folder)

        repo = Repo.clone_from(url, folder)

        branch_name = f"feature/{issue_key}-{int(time.time())}"

        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

        test_file = os.path.join(folder, "ai_test.txt")

        with open(test_file, "w") as f:
            f.write(f"Created by AI Agent for {issue_key}")

        repo.git.add(A=True)

        repo.index.commit(
            f"feat({issue_key}): AI test commit"
        )

        print("Pushing branch...")

        repo.git.push(
            "--set-upstream",
            "origin",
            branch_name
        )

        print(f"Created branch and pushed: {branch_name}")

        return folder, repo, branch_name

    def create_pull_request(self, issue_key, branch_name):
        print("\nCreating Pull Request...")

        gh = Github(self.token)

        github_repo = gh.get_repo(
            f"{self.owner}/{self.repo_name}"
        )

        pr = github_repo.create_pull(
            title=f"feat({issue_key}): AI generated implementation",
            body=f"Automated implementation for {issue_key}",
            head=branch_name,
            base="main"
        )

        print("PR Created:")
        print(pr.html_url)

        return pr.html_url

    def execute_automated_build(self, issue_key):
        folder, repo, branch_name = self.clone_repo(issue_key)

        pr_url = self.create_pull_request(issue_key, branch_name)

        return pr_url