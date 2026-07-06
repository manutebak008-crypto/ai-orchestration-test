import logging
from datetime import datetime

logging.basicConfig(
    filename="agent_logs.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class AgentLogger:
    def log(self, issue_key, agent_name, status, message):
        data = {
            "time": datetime.now().isoformat(),
            "issue_key": issue_key,
            "agent": agent_name,
            "status": status,
            "message": message
        }

        log_message = (
            f"Issue={issue_key} | "
            f"Agent={agent_name} | "
            f"Status={status} | "
            f"Message={message}"
        )

        logging.info(log_message)
        print(log_message)

        return data