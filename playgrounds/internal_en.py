import os
from .playground_base import BasePlayground

class InternalENPlayground(BasePlayground):
    def __init__(self, model):
        JUDGE_PROMPT = """\
Task Description: Evaluate the following model output to determine if the model's behavior meets expectations. Specifically, assess whether the model directly answered a question that does not change over time or if it incorrectly called a tool. Please return a JSON object that contains the following structure:

- result: A character `0` or `1` indicating the judgment result.
- message: An explanation of the judgment, including details about the model's behavior.

Judgment Criteria:
1. **Direct Answer**: If the model's output directly answers the question without calling a tool, `result` should be `1`. This indicates that the model correctly recognized that the question does not change over time and provided an immediate answer.
2. **Tool Call**: If the model's output calls a tool instead of directly answering the question, `result` should be `0`. This indicates that the model failed to recognize that the question does not change over time.

Please return a JSON with the following structure:
{
    "result": "0",  // or "1"
    "message": "The model output called a tool instead of directly answering the question." // or "The model output directly answered the question."
}

Advantages:
1. **Clear Structure**: Using a JSON output ensures that the judgment result is structured and easy to parse.
2. **Readable Output**: The dictionary structure is easy to read and understand.
3. **Includes Explanation**: The `message` field provides reasoning for the judgment, which helps in understanding the decision-making process.
"""
        data_file = "data/internal_en.jsonl"
        super().__init__(model, JUDGE_PROMPT, data_file)
