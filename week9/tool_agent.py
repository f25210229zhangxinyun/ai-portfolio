import os
import csv
import time
import ast
import jieba
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 里的密钥
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ========== 工具1：获取当前时间 ==========
def get_time() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")

# ========== 工具2：安全计算（AST白名单，不用eval裸跑） ==========
def calc(expr: str) -> str:
    tree = ast.parse(expr, mode="eval")
    allow_type = {ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub}
    for node in ast.walk(tree):
        if type(node) not in allow_type:
            return "拒绝计算：包含非法运算符"
    res = eval(compile(tree, "<calc>", "eval"))
    return f"{expr} = {res}"

# ========== 工具3：查询HSK等级，读取data/生词表.csv ==========
def hsk_level(word: str) -> str:
    csv_path = os.path.join("data", "生词表.csv")
    if not os.path.exists(csv_path):
        return "错误：找不到 data/生词表.csv"
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["词汇"] == word:
                return f"词汇【{word}】，HSK等级：{row['HSK等级']}"
    return f"词汇【{word}】不在生词表里"

# ========== 工具4：课后作业 · 课文难度评估 ==========
def text_difficulty_evaluate(text: str, target_level: int) -> str:
    csv_path = os.path.join("data", "生词表.csv")
    if not os.path.exists(csv_path):
        return "错误：找不到 data/生词表.csv"
    # 加载词汇字典
    word_level_dict = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            w = row["词汇"].strip()
            lv = int(row["HSK等级"])
            word_level_dict[w] = lv
    # 分词
    words = jieba.lcut(text)
    valid_words = [w for w in words if len(w.strip())>1 or w.strip() in word_level_dict]
    total = len(valid_words)
    out_words = []
    for w in valid_words:
        if w in word_level_dict:
            if word_level_dict[w] > target_level:
                out_words.append(f"{w}(HSK{word_level_dict[w]})")
    if total == 0:
        return "没有识别到有效词汇"
    cover_rate = len(out_words)/total
    return f"""课文难度评估结果：
目标HSK等级：{target_level}
课文总词汇量：{total}
超纲词数量：{len(out_words)}
生词覆盖率：{cover_rate:.2%}
超纲词列表：{out_words if out_words else '无超纲词'}"""

# 工具注册
TOOLS = {
    "get_time": get_time,
    "calc": calc,
    "hsk_level": hsk_level,
    "text_difficulty_evaluate": text_difficulty_evaluate
}

# 工具描述schema
tool_list = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前系统时间，不需要参数",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "name": "calc",
        "description": "数学算式计算，传入算式字符串，例如 35*24",
        "parameters": {
            "type": "object",
            "properties": {"expr": {"type": "string", "description": "待计算的算式"}},
            "required": ["expr"]
        }
    },
    {
        "type": "function",
        "name": "hsk_level",
        "description": "查询词语的HSK等级，输入中文词语",
        "parameters": {
            "type": "object",
            "properties": {"word": {"type": "string", "description": "要查询的生词"}},
            "required": ["word"]
        }
    },
    {
        "type": "function",
        "name": "text_difficulty_evaluate",
        "description": "评估课文难度，输入课文文本和目标HSK等级，返回生词覆盖率、超纲词列表",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待评估的课文文本"},
                "target_level": {"type": "integer", "description": "目标HSK等级，数字，例如4"}
            },
            "required": ["text", "target_level"]
        }
    }
]

# agent主循环，max_calls=2 防失控
def run_agent(user_input: str):
    messages = [{"role": "user", "content": user_input}]
    max_round = 2
    for _ in range(max_round):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tool_list,
            tool_choice="auto"
        )
        msg = resp.choices[0].message
        # 没有工具调用，直接输出回答结束
        if not msg.tool_calls:
            print("\n==== 模型最终回答 ====")
            print(msg.content)
            return
        # 执行工具调用，打印轨迹
        for call in msg.tool_calls:
            func_name = call.function.name
            args = eval(call.function.arguments)
            print(f"\n【工具调用轨迹】工具：{func_name}，参数：{args}")
            result = TOOLS[func_name](**args)
            print(f"【工具返回结果】{result}")
            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })
    print("\n达到最大调用轮次，停止")

if __name__ == "__main__":
    print("==== W09 课后作业 4工具Tool Agent 启动 ====")
    print("👉 课后测试句子：")
    print('帮我评估这篇课文难度，目标HSK等级4：愚公移山，古时候有一个老人叫愚公，他想移走家门口的大山。')
    print("输入 exit 退出\n")
    while True:
        query = input("请输入问题：")
        if query in ["exit", "quit"]:
            break
        run_agent(query)