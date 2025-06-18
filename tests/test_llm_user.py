from llm.query_generator import generate_graphql_query
from llm.llm_client import load_llm

def test_user_queries():
    """사용자 관련 GraphQL 쿼리 생성 테스트"""
    test_cases = [
        {
            "input": "사용자 목록 조회",
            "expected_fields": ["id", "name", "email", "role"],
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "특정 사용자 정보 조회",
            "expected_fields": ["id", "name", "email", "role", "profile"],
            "expected_variables": ["id"]
        }
    ]
    
    for case in test_cases:
        llm = load_llm()
        query = generate_graphql_query(case["input"], {}, llm)
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        
        # 필드 존재 확인
        for field in case["expected_fields"]:
            assert field in query, f"필드 없음: {field}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: {var}" 