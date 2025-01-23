import ollama
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText

from assistant.persona import Persona, Formatting


class Bot:
    def __init__(self, persona: Persona):
        self.name = persona.name
        self.model = persona.model
        self.formatting: Formatting = persona.formatting
        self.system_prompt = f"Your name is {self.name}. " \
            + persona.system_prompt

        self.system_prompt_message = {
            "role": "system",
            "content": self.system_prompt
        }

    def chat(self):
        message_chain = []
        while True:

            user_prompt = FormattedText([
                (f"fg:{self.formatting.user_color} bold", "User: ")
            ])
            user_response = prompt(user_prompt)
            user_message = {
                "role": "user",
                "content": "User: " + user_response
            }
            message_chain.append(self.system_prompt_message)
            message_chain.append(user_message)

            if user_response == "\\end":
                break

            chat_response = ollama.chat(
                model=self.model,
                messages=message_chain,
                stream=True,
                # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options
                options={"temperature": 0.8}
            )

            print()
            response_text = ""
            ralph_prompt = FormattedText([
                (f"fg:{self.formatting.persona_color} bold", f"{self.name}: ")
            ])
            print(ralph_prompt, end='', flush=True)
            for chunk in chat_response:
                chunk_content = chunk['message']['content']
                print(chunk_content, end='', flush=True)
                response_text += chunk_content

            print()
            print()
            chat_message = {
                "role": "assistant",
                "content": response_text
            }
            message_chain.append(chat_message)
