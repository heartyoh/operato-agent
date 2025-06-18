# rag/retriever.py

from rag.embedder import get_vectordb
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config import settings


def translate_to_english(text: str) -> str:
    llm = ChatOpenAI(
        temperature=0,
        model=settings["llm"]["model"],
        openai_api_key=settings["llm"]["openai_api_key"]
    )

    prompt = (
        "Translate the following Korean sentence to English. "
        "Keep it concise and suitable for semantic search.\n\n"
        f"Text: {text}"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def retrieve_relevant_dsl(user_input: str, k: int = 3) -> list:
    vectordb = get_vectordb()

    # 자동 번역: 한국어 → 영어
    translated_input = translate_to_english(user_input)
    print(f"Translated input: {translated_input}")

    docs = vectordb.similarity_search(translated_input, k=k)
    
    # 디버그: 각 문서의 모든 속성 출력
    for i, doc in enumerate(docs):
        print(f"\n=== Document {i+1} ===")
        print(f"Document object: {doc}")
        print(f"Document type: {type(doc)}")
        print(f"Document dict: {doc.__dict__}")

    return [
        {
            "dsl_name": doc.metadata.get("name", ""),
            "type": doc.metadata.get("type", ""),
            "variables": doc.metadata.get("variables", ""),
            "related_types": doc.metadata.get("related_types", ""),
            "text": doc.page_content,
        }
        for doc in docs
    ]
