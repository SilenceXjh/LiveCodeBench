import json
import ast
import zlib
import base64
import pickle

data = []

for i in range(1, 7):
    if i == 1:
        file_name = "test.jsonl"
    else:
        file_name = f"test{i}.jsonl"

    with open(file_name, "r") as f:
        for line in f.readlines():
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
            target_keys = ["question_id", "question_content", "starter_code", "public_test_cases"]
            new_obj = {key: obj[key] for key in target_keys if key in obj}
            data.append(new_obj)

print(f"load {len(data)} problems")
with open("total.json", "w") as f:
    json.dump(data, f, indent=2)