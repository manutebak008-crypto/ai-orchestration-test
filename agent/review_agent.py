class ReviewAgent:

    def run(self, issue_key, pr_url):
        print("Review Agent running for:", issue_key)

        tokens_used = 50

        return {
            "review_status": "PASSED",
            "message": f"Review completed for PR: {pr_url}",
            "tokens_used": tokens_used
        }
    