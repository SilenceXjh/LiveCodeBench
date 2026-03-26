import os
import sys
import json

from openai import OpenAI
from utils import load_tokenizer_model, model_generate, extract_python_code, ds_api_generate

FORMATTING_MESSAGE_WITH_STARTER_CODE = "You will use the following starter code to write the solution to the problem and enclose your code within delimiters."

FORMATTING_WITHOUT_STARTER_CODE = "Read the inputs from stdin solve the problem and write the answer to stdout (do not directly test on the sample inputs). Enclose your code within delimiters as follows. Ensure that when the python program runs, it reads the inputs, runs the algorithm and writes output to STDOUT."


def get_generic_question_template_answer(sample: dict):
    prompt = f"### Question:\n{sample["question_content"]}\n\n"

    if sample["starter_code"]:
        prompt += (
            f"### Request: {FORMATTING_MESSAGE_WITH_STARTER_CODE}\n"
        )
        prompt += f"```python\n{sample["starter_code"]}\n```\n\n"
    else:
        prompt += f"### Request: {FORMATTING_WITHOUT_STARTER_CODE}\n"
    
    prompt += f"""Before generating the code, think through the problem step by step, identify the key requirements, edge cases and correct algorithm.
Then output the final code in the following format:
```python
[Your code]
```"""
    return prompt


data_path = "/data0/xjh/LiveCodeBench/data/total.json"
model_path = "/data1/model/qwen/Qwen/Qwen2.5-Coder-7B-Instruct/"
output_path = "/data0/xjh/LiveCodeBench/custom_generation/ds_cot_generations"

USE_DS_API = True

os.makedirs(output_path, exist_ok=True)

with open(data_path, "r") as f:
    data = json.load(f)

if USE_DS_API:
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")
else:
    tokenizer, model = load_tokenizer_model(model_path)

for sample in data:
    question_id = sample["question_id"]
    prompt = get_generic_question_template_answer(sample)
    if USE_DS_API:
        generated_text = ds_api_generate(prompt, client)
    else:
        generated_text = model_generate(prompt, model, tokenizer)
    # print(generated_text)
    code = extract_python_code(generated_text)
    with open(os.path.join(output_path, f"{question_id}.py"), "w") as f:
        f.write(code)