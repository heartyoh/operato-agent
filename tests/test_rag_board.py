import pytest
import yaml
import os
from rag.retriever import retrieve_relevant_dsl

def load_dsl_file(filename):
    """실제 DSL 파일을 로드"""
    dsl_path = os.path.join("generated_dsls", filename)
    if os.path.exists(dsl_path):
        with open(dsl_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        raise FileNotFoundError(f"DSL 파일을 찾을 수 없습니다: {dsl_path}")

def print_test_result(test_name, user_input, retrieved_dsls):
    """테스트 결과를 보기 좋게 출력"""
    print("\n" + "="*80)
    print(f"🧪 테스트: {test_name}")
    print("="*80)
    print(f"📝 사용자 입력: {user_input}")
    print(f"🔍 검색된 DSL 수: {len(retrieved_dsls)}")
    print("-"*80)
    
    for i, dsl in enumerate(retrieved_dsls, 1):
        print(f"📋 DSL {i}: {dsl['dsl_name']} ({dsl['type']})")
        print(f"📄 설명: {dsl.get('description', 'N/A')}")
        print(f"🔧 템플릿: {dsl.get('skeleton', 'N/A')}")
        print(f"📊 변수: {dsl.get('variables', 'N/A')}")
        print(f"🏷️ 관련 타입: {dsl.get('related_types', 'N/A')}")
        print(f"📝 내용: {dsl.get('text', 'N/A')[:200]}...")
        print("-"*40)

def test_board_list_queries():
    """보드 목록 조회 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "보드 목록 조회",
            "expected_dsl": "boards",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "모든 보드 보여줘",
            "expected_dsl": "boards",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "보드 리스트 가져오기",
            "expected_dsl": "boards",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "내가 만든 보드 목록",
            "expected_dsl": "boardsCreatedByMe",
            "expected_variables": ["filters", "pagination"]
        }
    ]
    
    for case in test_cases:
        print_test_result("보드 목록 조회", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 보드 관련 DSL이 검색되었는지 확인
        board_dsls = [dsl for dsl in retrieved_dsls if 'board' in dsl['dsl_name'].lower()]
        assert len(board_dsls) > 0, f"보드 관련 DSL 없음: {case['input']}"
        
        # 가장 첫 번째 결과가 기대하는 DSL과 정확히 일치해야 함
        assert retrieved_dsls[0]["dsl_name"] == case["expected_dsl"], (
            f"가장 첫 번째 DSL이 예상과 다릅니다: {retrieved_dsls[0]['dsl_name']} != {case['expected_dsl']}\n"
            f"전체 결과: {[dsl['dsl_name'] for dsl in retrieved_dsls]}"
        )

def test_board_single_queries():
    """단일 보드 조회 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "특정 보드 정보 조회",
            "expected_dsl": "board",
            "expected_variables": ["id"]
        },
        {
            "input": "보드 상세 정보 보여줘",
            "expected_dsl": "board",
            "expected_variables": ["id"]
        },
        {
            "input": "보드 ID로 조회",
            "expected_dsl": "board",
            "expected_variables": ["id"]
        },
        {
            "input": "보드 이름으로 조회",
            "expected_dsl": "boardByName",
            "expected_variables": ["name"]
        }
    ]
    
    for case in test_cases:
        print_test_result("단일 보드 조회", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 보드 관련 DSL이 검색되었는지 확인
        board_dsls = [dsl for dsl in retrieved_dsls if 'board' in dsl['dsl_name'].lower()]
        assert len(board_dsls) > 0, f"보드 관련 DSL 없음: {case['input']}"
        
        # 가장 첫 번째 결과가 기대하는 DSL과 정확히 일치해야 함
        assert retrieved_dsls[0]["dsl_name"] == case["expected_dsl"], (
            f"가장 첫 번째 DSL이 예상과 다릅니다: {retrieved_dsls[0]['dsl_name']} != {case['expected_dsl']}\n"
            f"전체 결과: {[dsl['dsl_name'] for dsl in retrieved_dsls]}"
        )

def test_board_template_queries():
    """보드 템플릿 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "보드 템플릿 목록 조회",
            "expected_dsl": "boardTemplates",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "보드 템플릿 정보 보여줘",
            "expected_dsl": "boardTemplate",
            "expected_variables": ["id"]
        },
        {
            "input": "내가 만든 보드 템플릿",
            "expected_dsl": "boardTemplatesCreatedByMe",
            "expected_variables": ["filters", "pagination"]
        }
    ]
    
    for case in test_cases:
        print_test_result("보드 템플릿 조회", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 보드 관련 DSL이 검색되었는지 확인
        board_dsls = [dsl for dsl in retrieved_dsls if 'board' in dsl['dsl_name'].lower()]
        assert len(board_dsls) > 0, f"보드 관련 DSL 없음: {case['input']}"
        
        # 가장 첫 번째 결과가 기대하는 DSL과 정확히 일치해야 함
        assert retrieved_dsls[0]["dsl_name"] == case["expected_dsl"], (
            f"가장 첫 번째 DSL이 예상과 다릅니다: {retrieved_dsls[0]['dsl_name']} != {case['expected_dsl']}\n"
            f"전체 결과: {[dsl['dsl_name'] for dsl in retrieved_dsls]}"
        )

def test_board_version_queries():
    """보드 버전 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "보드 버전 목록 조회",
            "expected_dsl": "boardVersions",
            "expected_variables": ["boardId"]
        },
        {
            "input": "보드 버전 정보",
            "expected_dsl": "boardVersions",
            "expected_variables": ["boardId"]
        },
        {
            "input": "보드 버전 히스토리",
            "expected_dsl": "boardVersions",
            "expected_variables": ["boardId"]
        }
    ]
    
    for case in test_cases:
        print_test_result("보드 버전 조회", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 보드 관련 DSL이 검색되었는지 확인
        board_dsls = [dsl for dsl in retrieved_dsls if 'board' in dsl['dsl_name'].lower()]
        assert len(board_dsls) > 0, f"보드 관련 DSL 없음: {case['input']}"
        
        # 가장 첫 번째 결과가 기대하는 DSL과 정확히 일치해야 함
        assert retrieved_dsls[0]["dsl_name"] == case["expected_dsl"], (
            f"가장 첫 번째 DSL이 예상과 다릅니다: {retrieved_dsls[0]['dsl_name']} != {case['expected_dsl']}\n"
            f"전체 결과: {[dsl['dsl_name'] for dsl in retrieved_dsls]}"
        )

def test_board_published_queries():
    """보드 발행 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "발행된 보드 목록",
            "expected_dsl": "boardPublished",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "공개된 보드 조회",
            "expected_dsl": "boardPublished",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "발행된 보드 정보",
            "expected_dsl": "boardPublished",
            "expected_variables": ["filters", "pagination"]
        }
    ]
    
    for case in test_cases:
        print_test_result("보드 발행 조회", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 보드 관련 DSL이 검색되었는지 확인
        board_dsls = [dsl for dsl in retrieved_dsls if 'board' in dsl['dsl_name'].lower()]
        assert len(board_dsls) > 0, f"보드 관련 DSL 없음: {case['input']}"
        
        # 가장 첫 번째 결과가 기대하는 DSL과 정확히 일치해야 함
        assert retrieved_dsls[0]["dsl_name"] == case["expected_dsl"], (
            f"가장 첫 번째 DSL이 예상과 다릅니다: {retrieved_dsls[0]['dsl_name']} != {case['expected_dsl']}\n"
            f"전체 결과: {[dsl['dsl_name'] for dsl in retrieved_dsls]}"
        )

def test_board_complex_queries():
    """복합 보드 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "보드 목록과 템플릿 함께 조회",
            "expected_keywords": ["board", "template"]
        },
        {
            "input": "보드 정보와 버전 히스토리 조회",
            "expected_keywords": ["board", "version"]
        },
        {
            "input": "내가 만든 보드와 템플릿 목록",
            "expected_keywords": ["board", "created", "template"]
        }
    ]
    
    for case in test_cases:
        print_test_result("복합 보드 쿼리", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 보드 관련 DSL이 검색되었는지 확인
        board_dsls = [dsl for dsl in retrieved_dsls if 'board' in dsl['dsl_name'].lower()]
        assert len(board_dsls) > 0, f"보드 관련 DSL 없음: {case['input']}"

def test_board_search_accuracy():
    """보드 검색 정확도 테스트"""
    # 보드 관련 DSL 파일들 확인
    board_dsls = [
        "query_boards.yaml",
        "query_board.yaml",
        "query_boardByName.yaml",
        "query_boardPublished.yaml",
        "query_boardTemplate.yaml",
        "query_boardTemplates.yaml",
        "query_boardTemplatesCreatedByMe.yaml",
        "query_boardVersions.yaml",
        "query_boardsCreatedByMe.yaml"
    ]
    
    for dsl_file in board_dsls:
        try:
            dsl_data = load_dsl_file(dsl_file)
            print(f"✅ DSL 파일 로드 성공: {dsl_file}")
            print(f"   - 이름: {dsl_data.get('name', 'N/A')}")
            print(f"   - 타입: {dsl_data.get('type', 'N/A')}")
            print(f"   - 설명: {dsl_data.get('description', 'N/A')}")
        except FileNotFoundError:
            print(f"❌ DSL 파일 없음: {dsl_file}")

if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    test_board_list_queries()
    test_board_single_queries()
    test_board_template_queries()
    test_board_version_queries()
    test_board_published_queries()
    test_board_complex_queries()
    test_board_search_accuracy()
    print("\n✅ 모든 보드 테스트 완료!") 