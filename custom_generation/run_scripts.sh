#!/bin/bash

echo "开始执行第一条指令（Qwen2.5-Coder-7B-Instruct）..."
python repair.py /data0/xjh/LiveCodeBench/custom_generation/qwen7b_test_first_generations /data1/model/qwen/Qwen/Qwen2.5-Coder-7B-Instruct/ /data0/xjh/LiveCodeBench/custom_generation/qwen7b_repairs

echo "开始执行第二条指令（Qwen2.5-Coder-1.5B-Instruct）..."
python repair.py /data0/xjh/LiveCodeBench/custom_generation/qwen1.5b_generations /data1/model/qwen/Qwen/Qwen2.5-Coder-1.5B-Instruct/ /data0/xjh/LiveCodeBench/custom_generation/qwen1.5b_repairs