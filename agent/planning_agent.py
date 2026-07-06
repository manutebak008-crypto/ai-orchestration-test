class PlanningAgent:

    def run(self, issue_key):
        print("Planning Agent running for:", issue_key)

        plan = (
            f"Plan for {issue_key}: "
            "Create branch, generate code, open PR."
        )

        tokens_used = 100

        return {
            "plan": plan,
            "tokens_used": tokens_used
        }