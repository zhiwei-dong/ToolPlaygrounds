def calculate_accuracy(results):
    total = len(results)
    passed = sum(results)
    accuracy = passed / total if total > 0 else 0
    return accuracy