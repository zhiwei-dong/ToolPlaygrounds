import logging
import json
import time
import os
from utils.setup_logging import setup_logging
from tqdm import tqdm
from aoai_utils.aoai import aoai_instance as judgement
from concurrent.futures import ThreadPoolExecutor, as_completed


class BasePlayground:
    def __init__(self, model, judge_prompt, data_file):
        self.model = model
        self.judge_model = os.getenv('JUDGE_MODEL', 'gpt-4o-2024-05-13-ptu')
        self.judge_threads = int(os.getenv('JUDGE_THREADS', 16))
        self.judge_prompt = judge_prompt
        self.data_file = data_file

    def build_judge_prompt(self, model_input, model_output):
        return [{'role': 'user', 'content': self.judge_prompt + 'Next are the model conversation history:\n' + model_input  + 'Next are the model output:\n' + model_output}]

    def load_datasets(self):
        datasets = []
        try:
            with open(self.data_file, 'r', encoding='utf-8') as file:
                for line in file:
                    data = json.loads(line.strip())
                    datasets.append(data)
            logging.info("Datasets loaded successfully.")
        except Exception as e:
            print(datasets[-1])
            logging.error(f"Error loading datasets: {e}")
        return datasets

    def eval_metric(self, judgement_result):
        try:
            judgement_result = json.loads(
                judgement_result.choices[0].message.content)
        except (json.JSONDecodeError, KeyError):
            logging.error("Critical: Error parsing judgement result.")
            return False
        return judgement_result['result'] == '1'  # 返回 True 表示正确，False 表示错误

    def process_item(self, item):
        max_retries = 5

        for attempt in range(max_retries):
            try:
                model_output = self.model.get_response(
                    item["messages"], item["functions"])
                logging.info(f"Model output: {model_output}")
                break
            except Exception as e:
                print(item)
                if attempt < max_retries - 1:
                    time.sleep(10)
                    logging.warning(
                        f"Model failed to generate output (attempt {attempt + 1}): {e}, sleeping for 10 seconds and retrying.")
                else:
                    logging.error(
                        f"Model failed to generate output after {max_retries} attempts. Setting is_correct to False.")
                    return {
                        "prompt": item,
                        "model_output": None,
                        "judgement": None,
                        "is_correct": False
                    }

        judgement_prompt = self.build_judge_prompt(str(item), str(model_output))

        for attempt in range(max_retries):
            try:
                judgement_result = judgement.get_response(
                    self.judge_model, judgement_prompt, response_format={"type": "json_object"})
                logging.info(f"Judgement result: {judgement_result}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(10)
                    logging.warning(
                        f"Judgement failed to generate output (attempt {attempt + 1}): {e}, sleeping for 10 seconds and retrying.")
                else:
                    logging.error(
                        f"Judgement failed to generate output after {max_retries} attempts. Setting is_correct to False.")
                    return {
                        "prompt": item,
                        "model_output": str(model_output),
                        "judgement": None,
                        "is_correct": False
                    }

        is_correct = self.eval_metric(judgement_result)

        if is_correct:
            self.save_successful_items(item)

        return {
            "prompt": item,
            "model_output": str(model_output),
            "judgement": str(judgement_result),
            "is_correct": is_correct
        }

    def eval_pipeline(self, model_test_name):
        self.model_test_name = model_test_name
        setup_logging(model_test_name)
        datasets = self.load_datasets()

        results = []
        correct_count = 0

        with ThreadPoolExecutor(max_workers=self.judge_threads) as executor:
            futures = {executor.submit(
                self.process_item, item): item for item in datasets}

            for future in tqdm(as_completed(futures), total=len(futures), desc="Evaluating", unit="item"):
                result = future.result()
                results.append(result)

                if result['is_correct']:
                    correct_count += 1

        accuracy = correct_count / len(datasets) if datasets else 0.0
        self.save_results(results, model_test_name)

        return accuracy

    def save_results(self, results, model_test_name):
        base_name = self.__class__.__name__
        results_dir = f"results/{model_test_name}"
        os.makedirs(results_dir, exist_ok=True)

        result_file_path = os.path.join(results_dir, base_name + ".json")
        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            json.dump(results, result_file, ensure_ascii=False, indent=4)

        logging.info(f"Results saved to {result_file_path}")

    def save_successful_items(self, successful_item):
        base_name = self.__class__.__name__
        results_dir = f"results/{self.model_test_name}"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        result_file_path = os.path.join(results_dir, f"{base_name}_success.jsonl")

        with open(result_file_path, 'a', encoding='utf-8') as result_file:
            result_file.write(json.dumps(successful_item, ensure_ascii=False) + "\n")
