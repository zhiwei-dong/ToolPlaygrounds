import json
from re import I
import requests


CONVSATION_START = "<|im_start|>"
CONVSATION_END = "<|im_end|>"
PLUGIN_START = "<|action_start|>"
PLUGIN_END = "<|action_end|>"
CODE_INTERPRETER = "<|interpreter|>"
TOOLS_DEFINE = "<|plugin|>"
TOOLS_RESULT = "<|im_start|>environment name=<|plugin|>"
INTERPRETER_RESULT = "<|im_start|>environment name=<|interpreter|>"


headers = {
    'Content-Type': 'application/json'
}

default_parameters = {
    'temperature': 0,
    'top_p': 1.0,
    'top_k': 1,
    'repetition_penalty': 1.0,
    'max_new_tokens': 1024,
    'do_sample': False
}

description = """你现在可以使用一个支持 Python 代码执行的 Jupyter 笔记本环境。只需向 python 发送代码，即可在这个有状态环境中进行运行。这功能适用于:
- 数据分析或处理（如数据操作和图形制作）
- 复杂计算（如数学和物理问题）
- 编程示例（用于理解编程概念或语言特性）
- 文本处理和分析（包括文本分析和自然语言处理）
- 机器学习和数据科学（模型训练和数据可视化展示）
- 文件操作和数据导入（处理CSV、JSON等格式文件）"""

interpreter = [{"name": "python_interpreter", "description": description}]


class INTERNLM2:
    def __init__(self, api_base="http://101.230.144.204:24103", parameters=default_parameters, **kwargs):
    # def __init__(self, api_base="http://103.177.28.206:24101", parameters=default_parameters, **kwargs):
        self.api_base = api_base
        self.parameters = parameters

    def parse_intern_function(self, response):
        interpreter_left = response.find(f"{CODE_INTERPRETER}")
        tool_left = response.find(f"{TOOLS_DEFINE}")
        right = response.find(f"{PLUGIN_END}")

        reses = []
        if ((interpreter_left == -1) and (tool_left == -1)) or right == -1 or ((interpreter_left != -1) and (tool_left != -1)):
            return response

        if (interpreter_left == -1):
            left = tool_left
        else:
            left = interpreter_left

        if left >= right:
            return response

        if (interpreter_left == -1):
            tool_str = response[left + len(TOOLS_DEFINE):right]
            calls = tool_str.split(TOOLS_DEFINE)
            for call in calls:
                call = call.strip()
                # breakpoint()
                try:
                    call = json.loads(call)
                    if "parameters" in call:
                        call["arguments"] = call["parameters"]
                    reses.append(call)
                except:
                    pass
            if len(reses) == 0:
                return response
        else:
            calls = response[left+len(CODE_INTERPRETER):right]
            calls = calls.strip()
            try:
                assert (calls.strip()[:10] == "```python\n") and (
                    calls.strip()[-4:] == "\n```")
                code_calls = {'name': 'python_interpreter',
                              'arguments': {'code': calls}}
                reses.append(code_calls)
            except:
                return response
        return reses


    def get_response(self, messages, tools=[], interpreter=[], system_info=""):
        system_info = system_info.replace("<system>: ", "")
        system_text = f"{CONVSATION_START}system\n{system_info}{CONVSATION_END}\n"

        # 检查解释器
        if interpreter:
            assert (len(interpreter) == 1) and (
                interpreter[0]["name"] == "python_interpreter"), "Only support python interpreter now!"
            interpreter_test = f"{CONVSATION_START}system name={CODE_INTERPRETER}\n{interpreter[0]['description']}\n{CONVSATION_END}\n"
        else:
            interpreter_test = ""

        # 处理工具
        pure_tools = []
        for tool in tools:
            if tool['function']['name'] != "python_interpreter":
                pure_tools.append(tool['function'])

        if pure_tools:
            tool_text_str = json.dumps(pure_tools, ensure_ascii=False)
            tool_text = f"{CONVSATION_START}system name={TOOLS_DEFINE}\n{tool_text_str}\n{CONVSATION_END}\n"
        else:
            tool_text = ""

        # 处理messages
        history_text = ""
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            conv_text = f"{CONVSATION_START}{role}\n{content}{CONVSATION_END}\n"
            history_text += conv_text

        # 构建输入文本
        input_text = system_text + interpreter_test + tool_text + \
            history_text + f"{CONVSATION_START}assistant\n"

        input_data = {
            "inputs": input_text,
            "parameters": self.parameters
        }

        response = requests.post(self.api_base + '/generate',
                                headers=headers, json=input_data, stream=True)
        response = response.json()
        response = response['generated_text'][0]
        functions = self.parse_intern_function(response)

        if functions == []:
            return response

        return functions
