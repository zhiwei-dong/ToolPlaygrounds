import argparse
import json
import time
from openai import OpenAI

# Default prompts
TASK_INSTRUCTION = """
You are an expert in composing functions. You are given a question and a set of possible functions. 
Based on the question, you will need to make one or more function/tool calls to achieve the purpose. 
If none of the functions can be used, point it out and refuse to answer. 
If the given question lacks the parameters required by the function, also point it out.
""".strip()

FORMAT_INSTRUCTION = """
The output MUST strictly adhere to the following JSON format, and NO other text MUST be included.
The example format is as follows. Please make sure the parameter type is correct. If no function call is needed, please make tool_calls an empty list '[]'
```
{
  "tool_calls": [
    {"name": "func_name1", "arguments": {"argument1": "value1", "argument2": "value2"}},
    ... (more tool calls as required)
  ]
}
```
""".strip()


class XLAM:
    def __init__(self, model_name, temperature=0.3, top_p=1, max_tokens=512, port=8001, **kwargs):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        if self.model_name == "xlam-7b-fc-r":
            port = 8086
        elif self.model_name == "xlam-1b-fc-r":
            port=8085
        base_url = f"http://127.0.0.1:{port}/v1"
        self.client = OpenAI(api_key="Empty", base_url=base_url)

    def get_response(self, messages, tools, task_instruction=TASK_INSTRUCTION, format_instruction=FORMAT_INSTRUCTION):
        # Convert tools to XLAM format
        # breakpoint()
        xlam_tools = self.convert_to_xlam_tool(tools)

        # Build the input prompt
        prompt = self.build_prompt(messages, xlam_tools, task_instruction, format_instruction)

        # Create message for API call
        message = [{"role": "user", "content": prompt}]

        # Make API call
        start_time = time.time()
        response = self.client.chat.completions.create(
            messages=message,
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )
        latency = time.time() - start_time

        # Parse response
        result = response.choices[0].message.content
        parsed_result, success, _ = self.parse_response(result)

        # Prepare metadata
        metadata = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "latency": latency
        }

        return parsed_result, metadata

    def convert_to_xlam_tool(self, tools):
        if isinstance(tools, dict):
            tools = tools['function']
            return {
                "name": tools["name"],
                "description": tools["description"],
                "parameters": {k: v for k, v in tools["parameters"].get("properties", {}).items()}
            }
        elif isinstance(tools, list):
            return [self.convert_to_xlam_tool(tool) for tool in tools]
        else:
            return tools

    def build_prompt(self, query, tools, task_instruction=TASK_INSTRUCTION, format_instruction=FORMAT_INSTRUCTION):
        prompt = f"[BEGIN OF TASK INSTRUCTION]\n{task_instruction}\n[END OF TASK INSTRUCTION]\n\n"
        prompt += f"[BEGIN OF AVAILABLE TOOLS]\n{json.dumps(tools)}\n[END OF AVAILABLE TOOLS]\n\n"
        prompt += f"[BEGIN OF FORMAT INSTRUCTION]\n{format_instruction}\n[END OF FORMAT INSTRUCTION]\n\n"
        prompt += f"[BEGIN OF QUERY]\n{query}\n[END OF QUERY]\n\n"
        return prompt

    def parse_response(self, response):
        try:
            data = json.loads(response)
            tool_calls = data.get('tool_calls', []) if isinstance(data, dict) else data
            result = [
                {tool_call['name']: tool_call['arguments']}
                for tool_call in tool_calls if isinstance(tool_call, dict)
            ]
            return result, True, []
        except json.JSONDecodeError:
            return [], False, ["Failed to parse JSON response"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test XLAM model with endpoint")
    parser.add_argument("--model_name", default="xlam-1b-fc-r", help="Name of the model")
    parser.add_argument("--port", type=int, default=8001, help="Port number for the endpoint")
    parser.add_argument("--temperature", type=float, default=0.3, help="Temperature for sampling")
    parser.add_argument("--top_p", type=float, default=1.0, help="Top p for sampling")
    parser.add_argument("--max_tokens", type=int, default=512, help="Maximum number of tokens to generate")
    
    args = parser.parse_args()

    # Initialize the XLAMHandler with command-line arguments
    handler = XLAM(args.model_name, temperature=args.temperature, top_p=args.top_p, max_tokens=args.max_tokens, port=args.port)

    # Test case 1: Weather API, follows the OpenAI format: https://platform.openai.com/docs/guides/function-calling
    weather_api = {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature to return"
                }
            },
            "required": ["location"]
        }
    }

    # Test queries
    test_queries = [
        "What's the weather like in New York?",
        "Tell me the temperature in London in Celsius",
        "What's the weather forecast for Tokyo?",
        "What is the stock price of CRM?", # the model should return an empty list, meaning that it refuse to answer this irrelevant query and tools.
        "What's the current temperature in Paris in Fahrenheit?"
    ]

    # Run test cases
    for query in test_queries:
        print(f"Query: {query}")
        result, metadata = handler.process_query(query, weather_api, TASK_INSTRUCTION, FORMAT_INSTRUCTION)
        print(f"Result: {json.dumps(result, indent=2)}")
        print(f"Metadata: {json.dumps(metadata, indent=2)}")
        print("-" * 50)

    # Test case 2: Multiple APIs, follows the OpenAI format: https://platform.openai.com/docs/guides/function-calling
    calculator_api = {
        "name": "calculate",
        "description": "Perform a mathematical calculation",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The mathematical operation to perform"
                },
                "x": {
                    "type": "number",
                    "description": "The first number"
                },
                "y": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["operation", "x", "y"]
        }
    }

    multi_api_query = "What's the weather in Miami and what's 15 multiplied by 7?"
    multi_api_result, multi_api_metadata = handler.process_query(
        multi_api_query, 
        [weather_api, calculator_api], 
        TASK_INSTRUCTION, 
        FORMAT_INSTRUCTION
    )

    print("Multi-API Query Result:")
    print(json.dumps(multi_api_result, indent=2))
    print(f"Metadata: {json.dumps(multi_api_metadata, indent=2)}")