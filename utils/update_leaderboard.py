import pandas as pd
import plotly.figure_factory as ff

def generate_leaderboard_html(input_csv, output_html):
    # 从CSV文件中读取数据
    data = pd.read_csv(input_csv)

    # 计算平均分数
    data['Average Score'] = data.iloc[:, 2:].mean(axis=1, skipna=True)  # 计算每个模型的平均分数，排除NaN
    data['Average Score'].fillna(0, inplace=True)  # 将NaN替换为0

    # 将分数转换为百分比格式，并保留两位小数
    for col in data.columns[2:]:  # 从第三列开始处理分数列
        data[col] = (data[col] * 100).round(2)  # 转换为百分比格式

    data['Average Score'] = (data['Average Score']).round(2)  # 转换为百分比格式

    # 按照 Average Score 降序排序
    data.sort_values(by='Average Score', ascending=False, inplace=True)

    # 计算排名
    data['Rank'] = range(1, len(data) + 1)  # 生成连续的排名

    # 添加奖牌 emoji
    def rank_to_medal(rank):
        if rank == 1:
            return '🥇'  # 第一名
        elif rank == 2:
            return '🥈'  # 第二名
        elif rank == 3:
            return '🥉'  # 第三名
        else:
            return str(rank)  # 其他名次显示为数字

    data['Medal'] = data['Rank'].apply(rank_to_medal)  # 根据排名生成奖牌列

    # 移动“Average Score”列到第3列
    columns = data.columns.tolist()
    columns.insert(2, columns.pop(columns.index('Average Score')))
    data = data[columns]

    # 将排名列设置为索引
    data.set_index('Rank', inplace=True)

    # 将奖牌列移到第一列
    data.insert(0, 'Medal', data.pop('Medal'))

    # 使用 Plotly 创建一个 HTML 表格
    fig = ff.create_table(data)

    # 获取Plotly表格的HTML
    plotly_table_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # 创建完整的HTML结构
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.0/css/bootstrap.min.css" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro" />
    <title>FunctionCall Playgrounds Leaderboard</title>
    <style>
        body {{
            background-color: #f5f5f5;  /* 浅灰色背景 */
            font-family: 'Source Sans Pro', sans-serif;
            color: #212121;  /* 深色文本 */
            font-size: 18px;  /* 增大默认字体大小 */
        }}
        .navbar {{
            position: absolute;
            top: 0;
            right: 20px;
            padding: 10px;
            z-index: 100;
            font-size: 18px;
        }}
        .highlight-clean {{
            padding-bottom: 10px;
            background-color: #ffffff;  /* 白色背景 */
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);  /* 轻微阴影 */
            border-radius: 5px;  /* 圆角 */
            margin-bottom: 20px;  /* 底部间距 */
        }}
        .table-container {{
            background: #ffffff;  /* 白色背景 */
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);  /* 阴影效果 */
        }}
        h1, h2 {{
            color: #1976d2;  /* 主要蓝色 */
            font-size: 24px;  /* 增大标题字体大小 */
        }}
        h2 {{
            margin-top: 20px;  /* 顶部间距 */
        }}
        .table {{
            box-shadow: none;  /* 取消表格阴影 */
        }}
        .detail-header {{
            background-color: #1976d2;  /* 表头背景色 */
            color: white;  /* 表头文本颜色 */
        }}
        .summary-small-header {{
            background-color: #e3f2fd;  /* 淡蓝色 */
            color: #1976d2;  /* 深蓝色 */
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <a href="#leaderboard">Leaderboard</a>
    </div>

    <div class="highlight-clean text-center">
        <h1>FunctionCall Playgrounds Leaderboard</h1>
        <p>The leaderboard evaluates the LLM's ability to call functions accurately.</p>
    </div>

    <div class="container">
        <div class="table-container">
            <div>{plotly_table_html}</div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-autocolors"></script>
</body>
</html>
"""

    # 将完整的HTML写入文件
    with open(output_html, 'w') as f_combined:
        f_combined.write(full_html)

    print(f"Leaderboard HTML file created successfully at {output_html}!")

if __name__ == "__main__":
    generate_leaderboard_html('leaderboard.csv', 'leaderboard.html')
