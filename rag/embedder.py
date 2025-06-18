from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def get_embedder():
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def get_vectordb(persist_dir="rag_data/chroma_db"):
    embedder = get_embedder()
    return Chroma(persist_directory=persist_dir, embedding_function=embedder)
