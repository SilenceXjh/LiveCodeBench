import os
import json
from utils import get_data

code_dir = "/data0/xjh/LiveCodeBench/custom_generation/qwen1.5b_generations"
output_file_path = "/data0/xjh/LiveCodeBench/custom_generation/qwen1.5b_outputs.json"

data = get_data()

outputs = []

for sample in data:
    question_id = sample["question_id"]
    with open(os.path.join(code_dir, f"{question_id}.py"), "r") as f:
        code = f.read()
    outputs.append({
        "question_id": question_id,
        "code_list": [code]
    })

with open(output_file_path, "w") as f:
    json.dump(outputs, f, indent=2)