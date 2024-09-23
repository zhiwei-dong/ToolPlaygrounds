from aoai_utils.aoai import aoai_instance

class GPT:
    def __init__(self, model_name):
        self.model_name = model_name
        self.gpt_instance = aoai_instance  # 实例化 GPT 模型

    def get_response(self, messages, tools=None):
        """
        获取 GPT 模型的响应
        :param messages: 输入消息列表
        :param tools: 可选工具列表
        :return: 模型的响应
        """
        try:
            # 调用 aoai_instance 的 get_response 方法
            response = self.gpt_instance.get_response(self.model_name, messages, tools=tools)
            return response
        except Exception as e:
            print(f"Error getting response: {e}")
            return None
