# 官方RAG流水线 ↔ 我的 rag_qa.py / assistant_v1.py

| 官方流水线 | llm‑universe对应章节 | 我的项目实现 |
|---|---|---|
| Load + Split 加载与分块 | C3 数据处理：读取、清洗与切片 | TextLoader + RecursiveCharacterTextSplitter，加载HSK学科资料做文本切分 |
| Embed + Store 向量化入库 | C3 词向量及向量知识库 | OllamaEmbeddings(nomic‑embed‑text) + Chroma本地持久化向量库 |
| Retrieve 检索 | C4 基于LangChain搭建检索问答链 | retrieve() 获取top‑k片段；use_rag=True触发检索流程 |
| Prompt + Generate 拼词与生成 | C4 将LLM接入LangChain | build_prompt拼接system提示词+检索上下文+问题，调用llm.ask生成回答 |
| Deploy + Evaluate 部署与评估 | C5 系统评估与优化 | W7幻觉对照表做评估；v1.0暂未web部署，后续迭代完成 |
