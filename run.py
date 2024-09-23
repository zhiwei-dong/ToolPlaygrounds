import os
import csv
import argparse
import importlib  # 用于动态导入模块
from models import *
from playgrounds import *  # 导入所有playgrounds模块
import models  # 导入models包
from utils.update_leaderboard import generate_leaderboard_html  # 导入生成排行榜的函数


def load_playgrounds(playground_mapping, playground_names):
    playgrounds = {}

    if playground_names == "all":
        # 返回所有的 playground 名称和对应的类
        playgrounds = playground_mapping
    else:
        # 返回指定的 playground 名称
        for name in playground_names.split(','):  # 允许多个名称以逗号分隔
            class_name = playground_mapping.get(name.strip())
            if class_name:
                playgrounds[name.strip()] = class_name  # 将名称和类名添加到字典中
            else:
                print(f"Warning: Playground '{name}' not found in mapping.")

    return playgrounds


def update_leaderboard(leaderboard, model_class_name, model_name, playground, score):
    # 查找是否已有该模型的记录
    for entry in leaderboard:
        if (entry['model_class_name'] == model_class_name and
                entry['model_name'] == model_name):
            # 如果找到匹配的模型，更新对应的 playground 字段
            if playground in entry:
                # 如果当前得分为空，则直接更新为新得分
                if entry[playground] is None:
                    entry[playground] = score
                elif entry[playground] - 0 > 1e-6:
                    # 如果已有得分，计算平均值
                    current_score = entry[playground]
                    entry[playground] = (current_score + score) / 2  # 计算平均值
                elif entry[playground] - 0 < 1e-6:
                    # 如果得分为 0，直接更新为新得分
                    entry[playground] = score
            else:
                # 如果 playground 字段不存在，直接添加得分
                entry[playground] = score
            return  # 更新完毕，退出函数

    # 如果没有找到匹配的模型，创建新的记录
    entry = {
        'model_class_name': model_class_name,
        'model_name': model_name,
        playground: score  # 使用具体的模块名作为列名
    }
    leaderboard.append(entry)


def save_leaderboard(leaderboard, filename='leaderboard.csv'):
    # 动态获取所有列名
    fieldnames = ['model_class_name', 'model_name'] + list(set(
        k for d in leaderboard for k in d.keys() if k not in ['model_class_name', 'model_name', 'score']))

    # 保存结果到CSV文件
    with open(filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leaderboard)
    print(f"Leaderboard saved to {filename}")


def load_leaderboard(filename='leaderboard.csv'):
    leaderboard = []
    if os.path.exists(filename):
        with open(filename, mode='r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leaderboard.append({
                    'model_class_name': row['model_class_name'],
                    'model_name': row['model_name'],
                    **{
                        k: float(v) if v else 0  # 将空值处理为 0
                        for k, v in row.items()
                        if k not in ['model_class_name', 'model_name']
                    }
                })
    return leaderboard


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(
        description="Run evaluations on specified playgrounds with a given model.")
    parser.add_argument('--playgrounds', type=str, required=True,
                        help='Name of the playground to evaluate or "all" to evaluate all.')
    parser.add_argument('--model-class', type=str, required=True,
                        help='Name of the model class to use for evaluation.')
    parser.add_argument('--model-name', type=str, required=True,
                        help='Specific name of the model instance to evaluate.')
    parser.add_argument('--output-csv', type=str, default='leaderboard.csv',
                        help='Output CSV file name for the leaderboard.')
    parser.add_argument('--output-html', type=str, default='leaderboard.html',
                        help='Output HTML file path for the leaderboard.')

    args = parser.parse_args()

    playground_mapping = {
        "param-correction": ParamCorrectionPlayground,
        "missing-interact": MissingInteractPlayground,
        "tool-failover": ToolFailoverPlayground,
        "context-depend": ContextDependPlayground,
        "internal-zh": InternalZHPlayground,
        "internal-en": InternalENPlayground
    }

    # 加载现有的leaderboard
    leaderboard = load_leaderboard(args.output_csv)

    # 加载指定的playgrounds
    playgrounds = load_playgrounds(playground_mapping, args.playgrounds)

    for playground_name, playground in playgrounds.items():
        print(
            f"Running evaluation for playground: {playground_name} with model: {args.model_name}")

        # 获取指定的模型类
        model_class = getattr(models, args.model_class)  # 从models包中获取模型类

        # 实例化模型
        model = model_class(model_name=args.model_name)  # 假设模型类接受模型名称作为参数

        # 运行评估
        try:
            module = playground(model)
            score = module.eval_pipeline(args.model_name)  # 传入模型和模型名称

            # 更新leaderboard
            update_leaderboard(leaderboard, args.model_class,
                               args.model_name, playground_name, score)

        except Exception as e:
            print(f"Error running playground {playground}: {e}")

    # 保存最终的leaderboard到CSV文件
    save_leaderboard(leaderboard, args.output_csv)

    # 生成排行榜的HTML文件
    generate_leaderboard_html(args.output_csv, args.output_html)


if __name__ == "__main__":
    main()
