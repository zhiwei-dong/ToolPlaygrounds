import requests
from typing import TypedDict
import json

# reference: https://github.com/meta-llama/llama3/blob/main/llama/tokenizer.py#L202

class LLAMA3:
    def __init__(self, api="103.177.28.206:24101", model_name="llama3-8b",parameters=None):
        self.model_name = model_name
        self.url = f"http://{api}/generate"
        if parameters:
            self.parameters = parameters
        else:
            self.parameters = {
                'max_new_tokens': 256,
                'do_sample': False
            }

    def encode_header(self, message):
        text = ""
        text += "<|start_header_id|>"
        text += message["role"]
        text += "<|end_header_id|>"
        text += "\n\n"
        return text

    def encode_message(self, message):
        text = self.encode_header(message)

        if message['content'] == '':
            text += "  "
        elif message['content']:
            if isinstance(message['content'], str):
                text += message['content'].strip()
            elif isinstance(message['content'], list):
                for file in message['content']:
                    text += json.dumps(file, ensure_ascii=False) + "\n"
        else:
            for tool_call in message['tool_calls']:
                text += json.dumps(tool_call, ensure_ascii=False)

        text += "<|eot_id|>"
        return text

    def decode_response(self, raw_resp):
        right = raw_resp.find("<|eot_id|>")
        if right > 0:
            raw_resp = raw_resp[:right]
        resp = raw_resp.replace(
            "<|start_header_id|> assistant <|end_header_id|> \n\n", "")
        resp = resp.replace("<|eot_id|>", "")
        resp = resp.strip()

        # decode toolcalls
        try:
            tool_calls = []
            reses = resp.split('\n')
            for res in reses:
                res = res.strip()
                try:
                    res = json.loads(res)
                    tool_calls.append(res)
                except:
                    continue
        except:
            tool_calls = []

        if tool_calls == []:
            decoded_resp = {
                "content": resp,
            }
        else:
            decoded_resp = {
                "tool_calls": tool_calls,
            }
        return decoded_resp

    def get_response(self, messages=[]):
        dialog_prompt = "<|begin_of_text|>"
        for message in messages:
            dialog_prompt += self.encode_message(message)
        dialog_prompt += self.encode_header(
            {"role": "assistant", "content": ""})

        headers = {'Content-Type': 'application/json'}
        input_data = {
            "inputs": dialog_prompt,
            "parameters": self.parameters
        }

        response = requests.post(
            self.url, headers=headers, json=input_data, stream=False)
        response = response.json()
        response = response['generated_text'][0]
        response = self.decode_response(response)
        return response
