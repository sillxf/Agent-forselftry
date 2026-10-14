from openai import OpenAI
import json

class LLMClient:


    def __init__(
        self,
        api_key,
        base_url,
        model
    ):

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        self.model=model



    def generate(
        self,
        prompt
    ):

        response = (
            self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                    "role":"user",
                    "content":prompt
                    }
                ]

            )
        )


        return (
            response
            .choices[0]
            .message
            .content
        )