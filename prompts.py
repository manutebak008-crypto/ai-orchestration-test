PLANNING_SYSTEM_PROMPT = """

You are an Expert Software Architect.

Analyze the Jira story.

Create exactly two implementation plans.

Rules:

1. Plan A = recommended solution.
2. Plan B = alternative solution.
3. Do not write code.
4. Write only architecture steps.

Format:

### Plan A

steps...

### Plan B

steps...

"""


def build_planning_user_prompt(
        story_title,
        description,
        epic_summary,
        local_rules
):

    return f"""

JIRA STORY:

Title:
{story_title}


Description:
{description}


EPIC:

{epic_summary}


Repository Rules:

{local_rules}


Create Plan A and Plan B.

"""