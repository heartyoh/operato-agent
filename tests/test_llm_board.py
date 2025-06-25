import pytest
import yaml
import os
from llm.query_generator import generate_graphql_query
from llm.llm_client import load_llm

def load_dsl_file(filename):
    """실제 DSL 파일을 로드"""
    dsl_path = os.path.join("generated_dsl", "graphql_dsl", filename)
    if os.path.exists(dsl_path):
        with open(dsl_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        raise FileNotFoundError(f"DSL 파일을 찾을 수 없습니다: {dsl_path}")

def create_dsl_chunk_for_query_generator(dsl_data):
    """query_generator가 기대하는 형태로 DSL chunk 변환"""
    return {
        "skeleton": dsl_data.get("query_template", ""),
        "variables": ", ".join(dsl_data.get("variables", [])),
        "description": dsl_data.get("description", ""),
        "dsl_name": dsl_data.get("name", ""),
        "type": dsl_data.get("type", ""),
        "related_types": ", ".join(dsl_data.get("related_types", []))
    }

def print_test_result(test_name, user_input, dsl_info, generated_query):
    """테스트 결과를 보기 좋게 출력"""
    print("\n" + "="*80)
    print(f"🧪 테스트: {test_name}")
    print("="*80)
    print(f"📝 사용자 입력: {user_input}")
    print(f"📋 사용된 DSL: {dsl_info['dsl_name']} ({dsl_info['type']})")
    print(f"📄 DSL 설명: {dsl_info['description']}")
    print(f"🔧 DSL 템플릿: {dsl_info['skeleton']}")
    print(f"📊 DSL 변수: {dsl_info['variables']}")
    print("-"*80)
    print("🎯 생성된 GraphQL 쿼리:")
    print("-"*80)
    print("```graphql")
    print(generated_query)
    print("```")
    print("-"*80)

def test_board_list_query():
    """보드 목록 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    boards_dsl = load_dsl_file("query_boards.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(boards_dsl)
    
    test_cases = [
        {
            "input": "보드 목록 조회",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "모든 보드 보여줘",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "보드 리스트 가져오기",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "보드 목록 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "boards(" in query, f"boards 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인 (일부만)
        for var in case["expected_variables"][:2]:  # 처음 2개 변수만 확인
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_board_single_query():
    """단일 보드 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    board_dsl = load_dsl_file("query_board.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(board_dsl)
    
    test_cases = [
        {
            "input": "특정 보드 정보 조회",
            "expected_variables": ["id"],
            "expected_operation": "query"
        },
        {
            "input": "보드 상세 정보 보여줘",
            "expected_variables": ["id"],
            "expected_operation": "query"
        },
        {
            "input": "보드 ID로 조회",
            "expected_variables": ["id"],
            "expected_operation": "query"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "단일 보드 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "board(" in query, f"board 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_board_template_query():
    """보드 템플릿 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    board_templates_dsl = load_dsl_file("query_boardTemplates.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(board_templates_dsl)
    
    test_cases = [
        {
            "input": "보드 템플릿 목록 조회",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "모든 보드 템플릿 보여줘",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "보드 템플릿 리스트 가져오기",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "보드 템플릿 목록 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "boardTemplates(" in query, f"boardTemplates 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인 (일부만)
        for var in case["expected_variables"][:2]:  # 처음 2개 변수만 확인
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_board_created_by_me_query():
    """내가 만든 보드 목록 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    boards_created_by_me_dsl = load_dsl_file("query_boardsCreatedByMe.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(boards_created_by_me_dsl)
    
    test_cases = [
        {
            "input": "내가 만든 보드 목록",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "내가 생성한 보드들 보여줘",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "내 보드 목록 조회",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "내가 만든 보드 목록 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "boardsCreatedByMe(" in query, f"boardsCreatedByMe 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인 (일부만)
        for var in case["expected_variables"][:2]:  # 처음 2개 변수만 확인
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_board_mutation():
    """보드 수정 뮤테이션 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    board_mutation_dsl = load_dsl_file("mutation_updateBoard.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(board_mutation_dsl)
    
    test_cases = [
        {
            "input": "보드 정보를 수정해주세요",
            "expected_variables": ["id", "patch"],
            "expected_operation": "mutation"
        },
        {
            "input": "보드 이름과 설명을 업데이트해주세요",
            "expected_variables": ["id", "patch"],
            "expected_operation": "mutation"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "보드 수정 뮤테이션",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "mutation" in query.lower(), f"mutation 키워드 없음: {query}"
        assert "updateBoard(" in query, f"updateBoard 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_board_query_generation_with_different_inputs():
    """다양한 보드 입력에 대한 쿼리 생성 테스트"""
    # 보드 조회 DSL 사용
    board_dsl = load_dsl_file("query_board.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(board_dsl)
    llm = load_llm()
    
    test_inputs = [
        "보드 정보 조회",
        "보드 찾기",
        "보드 데이터 가져오기",
        "보드 상세 조회"
    ]
    
    for user_input in test_inputs:
        # 쿼리 생성
        query = generate_graphql_query(user_input, dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "다양한 보드 입력 테스트",
            user_input,
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {user_input}"
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "board(" in query, f"board 함수 없음: {query}"

if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    test_board_list_query()
    test_board_single_query()
    test_board_template_query()
    test_board_created_by_me_query()
    test_board_mutation()
    test_board_query_generation_with_different_inputs()
    print("\n✅ 모든 보드 테스트 완료!") 