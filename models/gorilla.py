# done
import requests
import json


# reference: https://huggingface.co/gorilla-llm/gorilla-openfunctions-v2

class Gorilla:
    def __init__(self, api_base="http://101.230.144.204:24103", parameters=None, **kwargs):
        self.api_base = api_base
        if parameters:
            self.parameters = parameters
        else:
            self.parameters = {
                'max_new_tokens': 2048,
                'do_sample': False
            }

    def decode_response(self, raw_resp):
        resp = raw_resp.strip()
        return resp

    def get_response(self, messages, tools=[]):
        assert len(messages) <= 2, "Only support single turn !"

        if len(messages) == 2:
            assert messages[1]['role'] == "user" and messages[0]['role'] == "system"
            system = messages[0]['content']
            messages = messages[1:]
        else:
            assert messages[0]['role'] == "user"
            system = "You are an AI programming assistant, utilizing the Gorilla LLM model, developed by Gorilla LLM, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer."

        if len(tools) == 0:
            dialog_prompt = f"{system}\n### Instruction: <<question>> {messages[0]['content']}\n### Response: "
        else:
            functions_string = ""
            for func in tools:
                functions_string += json.dumps(func)
            dialog_prompt = f"{system}\n### Instruction: <<function>>{functions_string}\n<<question>>{messages[0]['content']}\n### Response: "

        headers = {'Content-Type': 'application/json'}
        input_data = {
            "inputs": dialog_prompt,
            "parameters": self.parameters
        }

        response = requests.post(
            self.api_base + '/generate', headers=headers, json=input_data, stream=False)
        response = response.json()
        response = response['generated_text'][0]
        response = self.decode_response(response)
        return response


if __name__ == "__main__":
    dialog = [
        {
            "role": "system",
            "content": "你是个搜索大师，会使用搜索工具"
        },
        {
            "role": "user",
            "content": "Python诞生于哪一年"
        },
    ]

    web_search_define = {
        "type": "function",
        "function": {
                "name": "web_search",
                "description": "This function acts as a search engine to retrieve a wide range of information from the web. It is capable of processing queries related to various topics and returning relevant results. If the user specifies a vague date, such as today or tomorrow, please replace it with a specific date. If the user specifies vague times like 'morning' or 'forenoon', these should be mapped to specific times later than the current time, e.g., midnight defaults to 1 AM, morning to 7 AM, and forenoon to 10 AM.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query used to retrieve information from the internet. While the primary language for queries is Chinese, queries in other languages are also accepted and processed."
                        }
                    },
                    "required": ["query"]
                }
        }
    }

    functions = [web_search_define]

    model = Gorilla_V2("101.230.144.204:16900")
    response = model.chat(messages=dialog, functions=functions)
