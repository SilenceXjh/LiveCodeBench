import argparse
import os
import sys

from openai import OpenAI

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from utils import load_dataset_from_local_files, load_tokenizer_model, model_generate, extract_python_code, ds_api_generate

from lcb_runner.evaluation.compute_code_generation_metrics import check_correctness

# parser = argparse.ArgumentParser()
# parser.add_argument("code_dir")
# parser.add_argument("model_path")
# parser.add_argument("output_dir")
# args = parser.parse_args()
# code_dir = args.code_dir
# model_path = args.model_path
# output_dir = args.output_dir

code_dir = "/data0/xjh/LiveCodeBench/custom_generation/ds_generations"
model_path = "/data1/model/qwen/Qwen/Qwen2.5-Coder-1.5B-Instruct/"
output_dir = "/data0/xjh/LiveCodeBench/custom_generation/ds_repairs"

USE_DS_API = True

os.makedirs(output_dir, exist_ok=True)

dataset = load_dataset_from_local_files()
print(f"load {len(dataset)} problems")

if USE_DS_API:
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")
else:
    tokenizer, model = load_tokenizer_model(model_path)

total = 0
right = 0
repaired = [0,0,0]

for sample in dataset:
    total += 1

    question_id = sample.question_id
    with open(os.path.join(code_dir, f"{question_id}.py"), "r") as f:
        code = f.read()
    question_content = sample.question_content

    eval_sample = sample.get_evaluation_sample()
    print(f"check {question_id}.")
    results, metadata = check_correctness(eval_sample, code, timeout=6)
    # print("-" * 10)
    # print("question id:", question_id)
    # print("results", results)
    # print("metadata:", metadata)
    if len(metadata["errors"]) > 0:
        print(f"repairing {question_id}...")
        for i in range(3):
            feedback = metadata["errors"]
            prompt = f"""Please fix a Python program based on the question description, current code, and test feedback.
### Question description:
{question_content}

### Current code:
```python
{code}
```

### Test feedback:
{feedback}

Only Provide the fixed Python code without any other content."""
            # print("prompt:")
            # print(prompt)
            print("question length:", len(question_content))
            print("code length:", len(code))
            print("feedback length:", len(str(feedback)))
            print("prompt length:", len(prompt))
            if USE_DS_API:
                generated_text = ds_api_generate(prompt, client)
            else:
                generated_text = model_generate(prompt, model, tokenizer)
            code = extract_python_code(generated_text)
            results, metadata = check_correctness(eval_sample, code, timeout=6)
            if len(metadata["errors"]) == 0:
                print(f"{question_id} successfully repaired in round {i+1}!")
                repaired[i] += 1
                with open(os.path.join(output_dir, f"{question_id}.py"), "w") as f:
                    f.write(code)
                break
    else:
        right += 1

print("total:", total)
print("right:", right)
print("repaired:", repaired)

    