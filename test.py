from git_worker import GitWorkspaceWorker

worker = GitWorkspaceWorker()

worker.clone_repo("AIOS-4")

worker.create_pull_request("AIOS-4")