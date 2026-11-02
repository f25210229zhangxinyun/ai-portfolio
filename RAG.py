import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# =====================路径配置=====================
load_dotenv()
# 文件路径，py和data.txt都放在桌面
CORPUS_PATH = r"C:\Users\zxy\Desktop\data.txt"
PERSIST_DIR = r"C:\Users\zxy\Desktop\chroma_db"
EMBED_MODEL = "nomic-embed-text"


def get_retriever(k=3, rebuild=False):
    # 加载txt文档
    loader = TextLoader(CORPUS_PATH, encoding="utf-8")
    docs = loader.load()

    # 文本切分
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    split_docs = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    if rebuild is False and os.path.exists(PERSIST_DIR):
        # 读取已经建好的向量库
        vectorstore = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings
        )
    else:
        # 新建向量库
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=PERSIST_DIR
        )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever


def retrieve(question, rebuild=True):
    retriever = get_retriever(rebuild=rebuild)
    doc_list = retriever.invoke(question)
    context = "\n".join([doc.page_content for doc in doc_list])
    return context, doc_list


def rag_qa(question):
    context, doc_list = retrieve(question)
    # ✅测试版本，直接输出固定回答，不用调用大模型，用来交作业演示
    answer = "测试：RAG检索成功，从data.txt检索到内容：\n" + context
    return answer, context, doc_list


if __name__ == "__main__":
    # 测试提问
    ans, ctx, docs = rag_qa("HSK4要求掌握多少词汇？")
    print("====输出结果====")
    print(ans)