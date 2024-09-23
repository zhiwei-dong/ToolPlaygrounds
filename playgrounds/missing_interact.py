import os
from .playground_base import BasePlayground

class MissingInteractPlayground(BasePlayground):
    def __init__(self, model):
        JUDGE_PROMPT = """\
Task Description: Evaluate the following model output to determine if the model's behavior meets expectations. Please return a JSON object that contains the following structure:

- result: A character `0` or `1` indicating the judgment result.
- message: An explanation of the judgment, including details about the parameter requirements.

Judgment Criteria:
1. **Direct Tool Call Without Parameter Inquiry**: If the model's output directly calls the tool without asking for the required parameters, `result` should be `0`. This indicates that the model did not acknowledge the requirement for those parameters in the user's query.
2. **Inquiry About Missing Required Parameters**: If the model's output explicitly asks for the missing tool's required parameters (e.g., "What number should I use?") but does not call the tool, `result` should be `1`. This indicates that the model recognized the missing parameters but failed to act.

Please return a JSON with the following structure:
{
    "result": "0",  // or "1"
    "message": "The model output does not ask for the tool's required parameters (e.g., 'number')." // or "The model output explicitly asks for the tool's required parameters (e.g., 'number')."
}

Advantages:
1. **Clear Structure**: Using a JSON output ensures that the judgment result is structured and easy to parse.
2. **Readable Output**: The dictionary structure is easy to read and understand.
3. **Includes Explanation**: The `message` field provides reasoning for the judgment, which helps in understanding the decision-making process.
"""
        data_file = "data/missing.jsonl"
        super().__init__(model, JUDGE_PROMPT, data_file)

