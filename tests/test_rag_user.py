from rag.retriever import retrieve_relevant_dsl

def test_search_user_queries():
    """사용자 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "사용자 목록 조회",
            "expected_dsl": "users",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "admin@hatiolab.com 이메일을 가진 특정 사용자 정보 조회",
            "expected_dsl": "user",
            "expected_variables": ["email"]
        }
    ]
    
    for case in test_cases:
        print(f"\n=== 테스트 케이스: {case['input']} ===")
        chunks = retrieve_relevant_dsl(case["input"])
        print(f"검색 결과 수: {len(chunks)}")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n결과 {i}:")
            print(f"DSL 이름: {chunk['dsl_name']}")
            print(f"타입: {chunk['type']}")
            print(f"변수: {chunk['variables']}")
            print(f"관련 타입: {chunk['related_types']}")
            print(f"내용: {chunk['text'][:200]}...")  # 내용이 길 수 있으므로 앞부분만 출력
        
        assert len(chunks) > 0, f"검색 결과 없음: {case['input']}"
        assert chunks[0]["dsl_name"] == case["expected_dsl"], \
            f"예상 DSL 불일치: {chunks[0]['dsl_name']} != {case['expected_dsl']}"
        assert all(var in chunks[0]["variables"] for var in case["expected_variables"]), \
            f"예상 변수 불일치: {chunks[0]['variables']} != {case['expected_variables']}" 