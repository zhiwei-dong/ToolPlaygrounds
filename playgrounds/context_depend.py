import os
from .playground_base import BasePlayground

class ContextDependPlayground(BasePlayground):
    def __init__(self, model):
        JUDGE_PROMPT = """\
Task Description: Evaluate the following model output to determine if the model's behavior meets expectations regarding utilizing prior information to correct parameters in subsequent calls. Please return a JSON object that contains the following structure:

- result: A character `0` or `1` indicating the judgment result.
- message: An explanation of the judgment.

Judgment Criteria:
1. If the model output successfully uses previously provided information to identify and supplement the correct parameters for the next call, `result` should be `1`.
2. If the model output fails to use the previous information or does not supplement the correct parameters in the next call, `result` should be `0`.

Please return a JSON object with the following structure:
{
    "result": "1",  // or "0"
    "message": "The model output successfully utilizes prior information and supplements the correct parameters for the next call (replace specific parameter names here)." // or "The model output fails to utilize prior information or supplement the correct parameters for the next call (replace specific parameter names here)."
}

Advantages:
1. Clear Structure: Using a JSON output ensures that the judgment result is structured and easy to parse.
2. Readable Output: The dictionary structure is easy to read and understand.
3. Includes Explanation: The `message` field provides reasoning for the judgment, which helps in understanding the decision-making process.
"""
        data_file = "data/context.jsonl"
        super().__init__(model, JUDGE_PROMPT, data_file)

