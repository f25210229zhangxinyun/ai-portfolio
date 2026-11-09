# 学科智能问答助手 v1.0

## 功能
- 基于 RAG 的国际中文学科问答助手；
- 支持纯对话 / 基于知识库检索两种模式切换；
- 面向HSK3‑4中文学习者提供教学相关问答。

## 怎么装
- pip install -r requirements.txt
- ollama pull qwen2.5:0.5b && ollama pull nomic-embed-text
- 复制 .env.example 为 .env，填入 DEEPSEEK_API_KEY

## 怎么用
- 进入 week08_助手v1.0 目录运行：
- python assistant_v1.py

## 已知问题
- Ollama未启动时，local本地模式会报错，可以设置prefer="api"使用云端接口；
- 知识库内容有限，不在库内的问题会输出无相关资料；
- 向量库依赖chromadb，首次运行会生成持久化向量数据库文件。
