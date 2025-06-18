from rag.chunker import load_dsls
from rag.embedder import get_vectordb

def build_index():
    chunks = load_dsls()
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [c["id"] for c in chunks]

    vectordb = get_vectordb()
    vectordb.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    print(f"✅ {len(texts)} chunks indexed.")

if __name__ == "__main__":
    build_index()
