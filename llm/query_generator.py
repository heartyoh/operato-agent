from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage

def generate_graphql_query(user_input: str, dsl_chunk: Dict[str, Any], llm: BaseLanguageModel = None) -> str:
    """
    DSL chunk와 사용자 자연어 입력을 기반으로 GraphQL 쿼리를 생성하는 함수.

    Parameters:
    - user_input: 자연어 명령
    - dsl_chunk: RAG로 검색된 DSL 문맥 (예: skeleton, variables, description 포함)
    - llm: LangChain LLM 객체 (필수)

    Returns:
    - GraphQL 쿼리 문자열
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a GraphQL expert assistant. You will receive a DSL schema skeleton, variable definitions, and a user instruction.\n"
                   "Use this to write a valid GraphQL query or mutation."),
        ("human", "## DSL Skeleton\n{dsl}\n\n"
                  "## Variables\n{variables}\n\n"
                  "## Description\n{description}\n\n"
                  "## User Request (in Korean or English)\n{user_input}\n\n"
                  "Please generate only the GraphQL query, no extra explanation.")
    ])

    inputs = {
        "dsl": dsl_chunk.get("skeleton", ""),
        "variables": dsl_chunk.get("variables", ""),
        "description": dsl_chunk.get("description", ""),
        "user_input": user_input,
    }

    chain = prompt | llm
    result = chain.invoke(inputs)

    # ✅ AIMessage 객체일 경우 content 추출
    if isinstance(result, AIMessage):
        return result.content.strip()

    # LangChain 0.1.x 이상에서는 string 자체일 수도 있음
    return str(result).strip()

def test_dsl_to_query_with_various_inputs():
    test_cases = [
        "사용자 목록을 조회해주세요",
        "특정 사용자의 정보를 보여주세요",
        "사용자 권한을 수정해주세요"
    ]
    for query in test_cases:
        result = execute_query(query)
        assert result is not None

def test_dsl_to_query_with_invalid_input():
    query = "잘못된 쿼리"
    try:
        result = execute_query(query)
        assert False, "에러가 발생해야 합니다"
    except Exception as e:
        assert isinstance(e, ValueError)

def test_dsl_to_query_performance():
    import time
    start_time = time.time()
    result = execute_query("사용자 목록을 조회해주세요")
    end_time = time.time()
    assert end_time - start_time < 1.0  # 1초 이내 실행
