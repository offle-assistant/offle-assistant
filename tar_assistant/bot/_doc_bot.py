import ollama


class DocBot:
    def __init__(self):
        self.system_prompt = "You are a helpful assistant. " \
            "What follows is a conversation between you and " \
            "someone looking for help with sys admin tasks."
        self.system_prompt_message = {
            "role": "system",
            "content": self.system_prompt
        }

    def chat(self):
        message_chain = []
        while True:

            user_response = input("Input: ")
            user_message = {"role": "user", "content": user_response}
            message_chain.append(self.system_prompt_message)
            message_chain.append(user_message)

            if user_response == "\\end":
                break

            chat_response = ollama.chat(
                 model='llama3.2',
                 messages=message_chain,
                 stream=True,
            )

            print()
            print("Assistant: ")
            response_text = ""
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
