#!/bin/bash

# Favorite 模型及对应模型类
declare -A favorite_models=(
    ["GLM4-9B"]="GLM4"
    ["gpt-4o-2024-05-13-ptu"]="GPT"
    ["gpt-4o-2024-08-06"]="GPT"
    ["gpt-35-turbo-0125"]="GPT"
    ["gpt-4-turbo"]="GPT"
    ["gpt-4o-mini"]="GPT"
    ["ToolLLaMA-2-7b-v2"]="ToolLlama"
    ["gorilla-openfunctions-v2"]="Gorilla"
    ["functionary-small-v3.2"]="Functionary"
    ["functionary-medium-v3.2"]="Functionary"
    ["functionary-medium-v3.1"]="Functionary"
    ["xlam-7b-fc-r"]="XLAM"
    ["xlam-1b-fc-r"]="XLAM"
)

echo "Testing Favorite Models"
JUDGE_MODEL="${JUDGE_MODEL:-gpt-4o-2024-05-13-ptu}"
JUDGE_THREADS="${JUDGE_THREADS:-16}"
echo "JUDGE_MODEL: ${JUDGE_MODEL} with JUDGE_THREADS: ${JUDGE_THREADS}"
for model in "${!favorite_models[@]}"; do
    model_class=${favorite_models[$model]}
    echo "Testing model: $model with class: $model_class"
    python run.py --model-name "$model" --model-class "$model_class" --playgrounds tool-failover
    python run.py --model-name "$model" --model-class "$model_class" --playgrounds param-correction
    python run.py --model-name "$model" --model-class "$model_class" --playgrounds missing-interact
    python run.py --model-name "$model" --model-class "$model_class" --playgrounds internal-zh
    python run.py --model-name "$model" --model-class "$model_class" --playgrounds internal-en
done

echo "All favorite models have been tested."

