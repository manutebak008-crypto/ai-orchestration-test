class AgentTracker:
    active_stories = {}

    @classmethod
    def update(cls, issue_key, data):
        cls.active_stories[issue_key] = data

    @classmethod
    def get(cls, issue_key):
        return cls.active_stories.get(
            issue_key,
            {"message": "No status found for this issue"}
        )

    @classmethod
    def get_all(cls):
        return cls.active_stories