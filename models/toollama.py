import requests


def process_system_prompt(tools):
    system_prompt = "with a function call to actually excute your step. Your output should follow this format:\nThought:\nAction\nAction Input:\n"
    system_prompt = system_prompt + \
        "\nSpecifically, you have access to the following APIs: " + \
        str(tools)
    return system_prompt


class ToolLlama:
    def __init__(self, api_base="http://101.230.144.204:24103", parameters=None, **kwargs):
        self.api_base = api_base
        if parameters:
            self.parameters = parameters
        else:
            self.parameters = {
                'max_new_tokens': 2048,
                'do_sample': False
            }

    def get_response(self, messages=[], tools=[]):
        prompt = ''
        # add system first
        if tools:
            system_prompt= process_system_prompt
            (tools)
            prompt += f"system: {system_prompt}\n"
        for message in messages:
            role = message['role']
            content = message['content']
            prompt += f"{role}: {content}\n"
        prompt += "assistant:\n"

        headers = {'Content-Type': 'application/json'}
        input_data = {
            "inputs": prompt,
            "parameters": self.parameters
        }
        response = requests.post(
            self.api_base + '/generate', headers=headers, json=input_data, stream=False)
        response = response.json()
        response = response['generated_text'][0]
        return response
