from openai import OpenAI
import requests
from typing import TypedDict
import json
from jinja2 import Template, exceptions
from transformers import AutoTokenizer

# functionary vllm


class Functionary:
    def __init__(self, api='http://127.0.0.1:8000', parameters=None, model_name="functionary-small-v3.2", **kwargs):
        self.model_name = model_name
        if self.model_name == "functionary-small-v3.2":
            api = 'http://127.0.0.1:8083'
        elif self.model_name == "functionary-medium-v3.2":
            api = 'http://127.0.0.1:8082'
        elif self.model_name == "functionary-medium-v3.1":
            api = 'http://127.0.0.1:8081'
        base_url = f"{api}/v1"
        self.client = OpenAI(api_key="functionary", base_url=base_url)

    def decode_response(self, raw_resp):
        raw_resp = raw_resp.strip()
        try:
            name, args = raw_resp.split("\n")
            args = json.loads(args)
            resp = {
                "content": "",
                "tool_calls": [{
                    "name": name,
                    "arguments": args
                }]
            }
        except:
            resp = {
                "content": raw_resp,
                "tool_calls": []
            }
        return resp

    def process_message(self, messages):
        new_messages = []
        for msg in messages:
            if msg['role'] == 'assistant':
                if "tool_calls" in msg:
                    tc = msg['tool_calls'][0]['function']
                    content = f"{tc['name']}\n{json.dumps(tc['arguments'], ensure_ascii=False)}"
                    msg = {
                        "role": "assistant",
                        "content": content,
                    }
            elif msg['role'] == 'tool':
                msg = {
                    "role": "tool",
                    "observation": msg['content']
                }
            new_messages.append(msg)
        return new_messages

    def get_response(self, messages, tools):
        messages = self.process_message(messages)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",  # use "auto" to let the model choose the tool automatically
        )
        # breakpoint()
        if response:
            resp = response.choices[0].message
        else:
            err_str = f"Error: {response.status_code}"
            resp = {
                "content": err_str
            }
        return resp


def tool_chat():
    dialog = [
        {
            "role": "system",
            "content": "你是一个会调用工具的人工智能助手。"
        },
        {
            "role": "user",
            "content": "今天天气咋样, j间谍过家家有多少集"
        },
    ]

    tools = [{
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
    }]

    model = Functionary()
    # breakpoint()
    resp = model.get_response(dialog, tools)
    print(resp)


if __name__ == "__main__":
    tool_chat()
