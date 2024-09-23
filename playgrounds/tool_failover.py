import os
from .playground_base import BasePlayground

class ToolFailoverPlayground(BasePlayground):
    def __init__(self, model):
        JUDGE_PROMPT = """\
Task Description: Evaluate the following model output to determine if the model's behavior meets expectations in judgment criteria. Please return a JSON object that contains the following structure:

- result: A character `0` or `1` indicating the judgment result.
- message: An explanation of the judgment, including the reasoning behind the decision and the specific criteria met or not met.

Judgment Criteria:
1. **Empty Output**: If the model's output is empty or does not include any tool calls, `result` should be `0`. This indicates that the model failed to provide a meaningful response.
2. **No Tool Calls**: If the model output includes only a natural language explanation without any tool calls, `result` should also be `0`. This means the model did not attempt to handle the error.
3. **Tool Calls Present**: If the model output includes tool calls (regardless of whether there is a natural language explanation, other content, or even a meaningful explanation), **only assess the following**:
    - If the tool call's name match those in the conversation history, count this as a **retry** and set `result` to `1`.
    - If the model uses a different tool but with similar functionality, count this as a **failover** and set `result` to `1`.
    - **Else**: `result` should be `0`.
    - **Note**: Given that many model outputs may consist only of tool calls or explanations, do not set `result` to `0` solely due to the absence of an explanation when tool calls are present.

Please return a JSON with the following structure:
{
    "result": "1",  // or "0"
    "message": "The model successfully retried the failed tool or called an alternative tool after receiving an error message." // or "The model did not attempt to retry or call an alternative tool after receiving an error message."
    // Include detailed reasoning about the judgment process, specifying which criteria were or were not met.
}

Example Output:
{
    "result": "1",
    "message": "The model initially attempted to call the 'user_profile_picture_for_instagram_v13' function to retrieve user information. After receiving a timeout error, it successfully called the similar 'user_data_for_instagram_v13' function, demonstrating effective error handling by using an alternative tool to fulfill the user request."
}

Advantages:
1. **Clear Structure**: Using a JSON output ensures that the judgment result is structured and easy to parse.
2. **Readable Output**: The dictionary structure is easy to read and understand.
3. **Includes Explanation**: The `message` field provides reasoning for the judgment, which helps in understanding the decision-making process.
"""

        data_file = "data/failover.jsonl"
        super().__init__(model, JUDGE_PROMPT, data_file)

