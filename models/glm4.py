from openai import OpenAI
import requests
from typing import TypedDict
import json
from jinja2 import Template, exceptions
from transformers import AutoTokenizer

# reference: https://github.com/yhyu13/GLM-4/tree/main


class GLM4_1:
    def __init__(self, api='http://localhost:8080', parameters=None, **kwargs):
        self.url = f"{api}/generate"
        if parameters:
            self.parameters = parameters
        else:
            self.parameters = {
                'max_new_tokens': 1024,
                'do_sample': False
            }
        self.tokenizer = AutoTokenizer.from_pretrained(
            "/mnt/nvme0/dongzhiwei1/glm-4-9b-chat", trust_remote_code=True)

    def decode_response(self, raw_resp):
        resp = raw_resp.replace("<EOS_TOKEN>", "")
        resp = resp.strip()
        return resp

    def get_response(self, messages=[], tools=[]):
        dialog_prompt = self.tokenizer.apply_chat_template(messages,
                                                           add_generation_prompt=True,
                                                           tokenize=False)
        headers = {'Content-Type': 'application/json'}
        input_data = {
            "inputs": dialog_prompt,
            "parameters": self.parameters
        }

        response = requests.post(
            self.url, headers=headers, json=input_data, stream=True)
        response = response.json()
        breakpoint()
        response = response['generated_text'][0]
        response = self.decode_response(response)
        return response


def example_chat():
    dialog = [
        {
            "role": "system",
            "content": "你是一个厨师，你需要根据客人说的颜色，推荐相应的菜。说中文。"
        },
        {
            "role": "user",
            "content": "爷要吃红的"
        },
    ]
    # '[gMASK]<sop><|system|>\n你是一个厨师，你需要根据客人说的颜色，推荐相应的菜。说中文。<|user|>\n爷要吃红的<|assistant|>'
    model = GLM4("101.230.144.204:17906")
    response = model.chat(messages=dialog)
    print(response)


class GLM4:
    def __init__(self, api='http://localhost:8080', parameters=None, **kwargs):
        base_url = f"{api}/v1/"
        self.client = OpenAI(api_key="EMPTY", base_url=base_url)

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
            model="glm-4",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # use "auto" to let the model choose the tool automatically
            # tool_choice={"type": "function", "function": {"name": "my_function"}},
        )
        if response:
            content = response.choices[0].message.content
            decoded_resp = self.decode_response(content)
            resp = {
                "content": decoded_resp["content"],
                "tool_calls": decoded_resp["tool_calls"]
            }
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

    model = GLM4_vllm(api="10.121.4.12:8089")
    resp = model.chat(dialog, tools)
    breakpoint()
    print(resp)


if __name__ == "__main__":
    tool_chat()
