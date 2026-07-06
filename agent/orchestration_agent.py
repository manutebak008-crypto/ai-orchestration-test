from agent.planning_agent import PlanningAgent
from agent.build_agent import BuildAgent
from agent.review_agent import ReviewAgent


class OrchestrationAgent:

    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.build_agent = BuildAgent()
        self.review_agent = ReviewAgent()

    def run(self, issue_key):
        print("Orchestration Agent started for:", issue_key)

        planning_result = self.planning_agent.run(issue_key)

        build_result = self.build_agent.run(issue_key)

        review_result = self.review_agent.run(
            issue_key,
            build_result["pr_url"]
        )

        total_tokens = (
            planning_result["tokens_used"]
            + build_result["tokens_used"]
            + review_result["tokens_used"]
        )

        return {
            "planning": planning_result,
            "build": build_result,
            "review": review_result,
            "total_tokens_used": total_tokens
        }