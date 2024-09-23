import os
from .playground_base import BasePlayground

class ParamCorrectionPlayground(BasePlayground):
    def __init__(self, model):
        JUDGE_PROMPT = """\
Task Description: Evaluate the following model output to determine if the model's behavior meets expectations regarding correcting erroneous parameters. Please return a JSON object that contains the following structure:

- result: A character `0` or `1` indicating the judgment result.
- message: An explanation of the judgment.

Judgment Criteria:
1. If the model output identifies and corrects the previously provided erroneous parameters, `result` should be `1`.
2. If the model output fails to identify or correct the erroneous parameters, `result` should be `0`.

Please return a JSON object with the following structure:
{
    "result": "1",  // or "0"
    "message": "The model output successfully identifies and corrects the erroneous parameters (replace specific parameter names here)." // or "The model output fails to identify or correct the erroneous parameters (replace specific parameter names here)."
}
"""
        data_file = "data/correction.jsonl"
        super().__init__(model, JUDGE_PROMPT, data_file)

