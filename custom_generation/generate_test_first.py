import os
import sys
import json
import argparse

from openai import OpenAI
from utils import load_tokenizer_model, model_generate, extract_python_code, extract_json_code, ds_api_generate

FORMATTING_MESSAGE_WITH_STARTER_CODE = "You will use the following starter code to write the solution to the problem and enclose your code within delimiters."

FORMATTING_WITHOUT_STARTER_CODE = "Read the inputs from stdin solve the problem and write the answer to stdout (do not directly test on the sample inputs). Enclose your code within delimiters as follows. Ensure that when the python program runs, it reads the inputs, runs the algorithm and writes output to STDOUT."


def get_generic_question_template_answer(sample: dict, gen_tests: str):
    prompt = f"### Question:\n{sample["question_content"]}\n\n"

    prompt += f"Additional testcases:\n{gen_tests}\n\n"

    if sample["starter_code"]:
        prompt += (
            f"### Format: {FORMATTING_MESSAGE_WITH_STARTER_CODE}\n"
        )
        prompt += f"```python\n{sample["starter_code"]}\n```\n\n"
    else:
        prompt += f"### Format: {FORMATTING_WITHOUT_STARTER_CODE}\n"
        prompt += "```python\n# YOUR CODE HERE\n```\n\n"
    
    prompt += f"Only output the solution code without any explanation."
    return prompt


data_path = "/data0/xjh/LiveCodeBench/data/total.json"

USE_DS_API = True

# parser = argparse.ArgumentParser()
# parser.add_argument("model_path")
# parser.add_argument("output_path")
# args = parser.parse_args()
# model_path = args.model_path
# output_path = args.output_path
model_path = "/data1/model/qwen/Qwen/Qwen2.5-Coder-7B-Instruct/"
output_path = "/data0/xjh/LiveCodeBench/custom_generation/ds_test_first_generations"

if USE_DS_API:
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")
else:
    tokenizer, model = load_tokenizer_model(model_path)

os.makedirs(output_path, exist_ok=True)

with open(data_path, "r") as f:
    data = json.load(f)

for sample in data:
    question_id = sample["question_id"]
    question_content = sample["question_content"]
    public_test_cases = sample["public_test_cases"]
    if len(public_test_cases) > 0:
        test_case = public_test_cases[0]
        test_case.pop("testtype")
    else:
        test_case = {"input": "xxx", "output": "xxx"}
    gen_test_prompt = f"""Consider the following question and generate more testcases for the question.
### Question:
{question_content}

### Format Request:
You should generate 3-5 testcases in the format like:
```
{json.dumps(test_case, indent=2)}
```
Try to generate testcases covering all scenarios.
Don't generate testcases that already exist in the question description.
Only output testcases without any description."""
    # print(gen_test_prompt)
    if USE_DS_API:
        generated_text = ds_api_generate(gen_test_prompt, client)
    else:
        generated_text = model_generate(gen_test_prompt, model, tokenizer)
    gen_tests = extract_json_code(generated_text)

    # print("gen tests:")
    # print(gen_tests)

    prompt = get_generic_question_template_answer(sample, gen_tests)
    # print("prompt:")
    # print(prompt)
    if USE_DS_API:
        generated_text = ds_api_generate(prompt, client)
    else:
        generated_text = model_generate(prompt, model, tokenizer)
    # print(generated_text)
    code = extract_python_code(generated_text)
    with open(os.path.join(output_path, f"{question_id}.py"), "w") as f:
        f.write(code)