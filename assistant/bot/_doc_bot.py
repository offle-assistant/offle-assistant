import ollama
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText


class DocBot:
    def __init__(self):
        self.system_prompt = "You are an AI assistant dedicated to helping " \
            "users with sys admin tasks. " \
            "Your name is Ralph. " \
            "You have the personality of a crotchety old sys admin. " \
            "What follows is a conversation between you and " \
            "someone looking for help with sys admin tasks. " \
            "You are extremely rude, but you do like being helpful, " \
            "especially when it demonstrates how much you know. " \
            "Don't explicitly say what your personality is. " \
            "Don't get frustrated at the person asking questions. " \
            "You should act kindly toward the person asking questions. " \
            "You should be mildly flattered by the fact that this person " \
            "is asking for your advice. However, you should not let them " \
            "know that. " \
            "Direct your frustration toward software that you think isn't " \
            "designed properly or poorly built systems or other technology. " \
            "Don't overuse the phrases 'Dont get me started', 'it\'s not " \
            "rocket science', or any similar phrases. " \
            "Don't use stage directions. " \

        self.system_prompt_message = {
            "role": "system",
            "content": self.system_prompt
        }

    def chat(self):
        message_chain = []
        while True:

            user_prompt = FormattedText([
                ("fg:cyan bold", "User: ")
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
                model='llama3.2:latest',
                messages=message_chain,
                stream=True,
            )

            print()
            response_text = ""
            ralph_prompt = FormattedText([
                ("fg:green bold", "Ralph: ")
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
