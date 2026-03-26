import json
import os
import sys

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from lcb_runner.benchmarks.code_generation import CodeGenerationProblem
# from lcb_runner.evaluation.testing_util import run_test
from lcb_runner.evaluation.compute_code_generation_metrics import check_correctness

from utils import load_dataset_from_local_files


code_dir = "/data0/xjh/LiveCodeBench/custom_generation/qwen1.5b_generations"

dataset = load_dataset_from_local_files()
print(f"load {len(dataset)} problems")

for sample in dataset:
    if not sample.metadata.get("func_name"):
        continue
    question_id = sample.question_id
    with open(os.path.join(code_dir, f"{question_id}.py"), "r") as f:
        code = f.read()

    eval_sample = sample.get_evaluation_sample()
    results, metadata = check_correctness(eval_sample, code, timeout=6)
    print("-" * 10)
    print("question id:", question_id)
    print("results", results)
    print("metadata:", metadata)

    break