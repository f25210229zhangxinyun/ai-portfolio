# llm.py week06 双引擎封装
import requests
from openai import OpenAI

# 本地 Ollama 引擎
class LocalEngine:
    def __init__(self, model="qwen2"):
        self.url = "http://127.0.0.1:11434/api/generate"
        self.model = model

    def chat(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        resp = requests.post(self.url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()["response"]


# 远程API引擎（OpenAI兼容）
class APIEngine:
    def __init__(self):
        # ⚠️ 测试的时候填你的key，上传github之前可以改回占位符，不要明文泄露密钥！
        self.client = OpenAI(
            api_key="填你自己的API_KEY",
            base_url="填接口地址，例如 https://xxx/v1"
        )
        self.model = "gpt-3.5-turbo"

    def chat(self, prompt):
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content


# ✅统一入口 ask，双向回退，打印切换原因（作业核心！）
def ask(prompt, prefer="local"):
    local = LocalEngine()
    api = APIEngine()

    if prefer == "local":
        print("[优先尝试] LocalEngine 本地Ollama")
        try:
            return local.chat(prompt)
        except Exception as err:
            print(f"【回退日志】Local失败，错误信息：{err}，自动切换 APIEngine")
            return api.chat(prompt)

    elif prefer == "api":
        print("[优先尝试] APIEngine 远程接口")
        try:
            return api.chat(prompt)
        except Exception as err:
            print(f"【回退日志】API失败，错误信息：{err}，自动切换 LocalEngine")
            return local.chat(prompt)
    else:
        raise ValueError("prefer 参数只能是 local / api")


# ====== 主入口，已经取消注释，__name__双下划线正确 ======
if __name__ == "__main__":
    question = "请简单解释什么是国际中文教育"
    print("====测试1 prefer=local====")
    ans = ask(question, prefer="local")
    print(ans)

    print("\n====测试2 prefer=api====")
    ans = ask(question, prefer="api")
    print(ans)

    print("\n====测试3：关闭ollama，prefer=local，用来触发回退（最重要证据）====")
    ans = ask(question, prefer="local")
    print(ans)