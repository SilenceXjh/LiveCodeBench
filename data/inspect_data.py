import pickle
import sys
import os

# current_file = os.path.abspath(__file__)
# current_dir = os.path.dirname(current_file)
# project_root = os.path.dirname(current_dir)
# sys.path.append(project_root)
# from lcb_runner.benchmarks.code_generation import CodeGenerationProblem

import json
import ast
import zlib
import base64

data = []
with open("test.jsonl", "r") as f:
    for line in f.readlines()[:100]:
        obj = json.loads(line.strip())
        public_test_cases_str = obj["public_test_cases"]
        public_test_cases = ast.literal_eval(public_test_cases_str)
        obj["public_test_cases"] = public_test_cases
        private_test_cases_str = obj["private_test_cases"]
        try:
            private_test_cases = json.loads(private_test_cases_str)  # type: ignore
        except:
            private_test_cases = json.loads(
                pickle.loads(
                    zlib.decompress(
                        base64.b64decode(private_test_cases_str.encode("utf-8"))  # type: ignore
                    )
                )
            )
        obj["private_test_cases"] = private_test_cases
        target_keys = ["question_id", "question_content", "starter_code", "public_test_cases", "private_test_cases"]
        new_obj = {key: obj[key] for key in target_keys if key in obj}
        data.append(obj)

print("-----sample 0------")
print(json.dumps(data[0], indent=2))

print("------sample with metadata------")
for sample in data:
    if sample["metadata"] != "{}":
        print(sample["metadata"])
        print(type(sample["metadata"]))
        print(json.dumps(sample, indent=2))
        break
