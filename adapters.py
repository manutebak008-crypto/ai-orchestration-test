import os
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()


class ClaudeAdapter:


    def __init__(self):

        self.client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )


    def execute_view_command(self, prompt):


        response = self.client.messages.create(

            model="claude-opus-4-1-20250805",

            max_tokens=3000,

            system="You are an expert software architect.",

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )


        return response.content[0].text





class CLIAdapterFactory:


    @staticmethod
    def get_adapter():

        return ClaudeAdapter()