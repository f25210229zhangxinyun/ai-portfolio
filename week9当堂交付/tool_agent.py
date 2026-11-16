import os
import csv
import json
import re
import datetime
import ast
import operator
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
VOCAB = "data/生词表.csv"

# ---------------- 安全白名单AST计算器，禁止eval ----------------
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("只允许数字与 + - * / ** % 运算")

def calc(expr: str) -> str:
    """安全四则计算器，不使用eval，仅支持加减乘除、幂、取模"""
    try:
        tree = ast.parse(expr, mode="eval")
        return str(_eval_node(tree))
    except ZeroDivisionError:
        return "错误：除数为0"
    except Exception as e:
        return f"拒绝计算: {e}"

def get_time() -> str:
    """获取当前系统时间"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def hsk_level(word: str) -> str:
    """查询单词对应的HSK等级，从data/生词表.csv读取"""
    with open(VOCAB, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["词汇"].strip() == word.strip():
                return f"{word} 是 {row['HSK等级']} 级"
    return f"未找到 {word}"

# 工具注册表
TOOLS = {
    "get_time": get_time,
    "calc": calc,
    "hsk_level": hsk_level,
}

# 系统提示词SYS
SYS = """你是国际中文助教。可用工具只有这3个：
get_time (查看当前时间，无参数)
calc (四则运算，如 calc("35*24") )
hsk_level (查生词HSK等级，如 hsk_level("把") )
如需调用，只输出一行JSON，格式：{"tool":"工具名","args":["参数"]}
一次只调用一个工具，绝不编造不存在的工具名；无需工具时直接回答。
"""

def parse_calls(txt: str):
    """容错解析：去掉```json围栏、提取JSON，兼容模型乱输出"""
    s = (txt or "").strip().replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
        return [obj] if isinstance(obj, dict) else []
    except Exception:
        calls = []
        for blk in re.findall(r"\{.*?\}", s, re.S):
            try:
                obj = json.loads(blk)
                if isinstance(obj, dict):
                    calls.append(obj)
            except Exception:
                continue
        return calls

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
)
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

def run(user_msg, max_calls=2):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user_msg}]
    for _ in range(max_calls):
        resp = client.chat.completions.create(model=MODEL, messages=msgs)
        txt = resp.choices[0].message.content
        calls = [c for c in parse_calls(txt) if isinstance(c, dict) and c.get("tool") in TOOLS]
        if not calls:
            return txt
        results = []
        for call in calls:
            args = call.get("args", [])
            if not isinstance(args, list):
                results.append("工具参数格式错误")
                continue
            try:
                res = TOOLS[call["tool"]](*args)
                results.append(f"{call['tool']} → {res}")
            except Exception as e:
                results.append(f"工具执行失败: {e}")
        msgs.append({"role": "assistant", "content": txt})
        msgs.append({"role": "user", "content": f"工具返回：{'; '.join(results)}。请据此作答。"})
    return client.chat.completions.create(model=MODEL, messages=msgs).choices[0].message.content

if __name__ == "__main__":
    # 课堂复合问句：你可以直接运行这句
    print(run("请依次查询两件事：1. '把'字的HSK等级是多少？ 2. 现在的时间是多少？"))