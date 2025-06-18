from rag.retriever import retrieve_relevant_dsl

def test_search_appliance_queries():
    """장비 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "어플라이언스 장치 목록 보여줘",
            "expected_dsl": "appliances",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "특정 어플라이언스 상세 조회",
            "expected_dsl": "appliance",
            "expected_variables": ["id"]
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