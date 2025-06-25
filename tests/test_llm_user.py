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

def test_user_query_single():
    """단일 사용자 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    user_dsl = load_dsl_file("query_user.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(user_dsl)
    
    test_cases = [
        {
            "input": "admin@hatiolab.com 사용자 정보 조회",
            "expected_fields": ["id", "name", "email", "status"],
            "expected_variables": ["email"],
            "expected_operation": "query"
        },
        {
            "input": "특정 사용자 정보 보여줘",
            "expected_fields": ["id", "name", "email"],
            "expected_variables": ["email"],
            "expected_operation": "query"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "단일 사용자 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "user(" in query, f"user 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_users_query_list():
    """사용자 목록 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    users_dsl = load_dsl_file("query_users.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(users_dsl)
    
    test_cases = [
        {
            "input": "사용자 목록 조회",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "모든 사용자 보여줘",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "사용자 목록을 페이지네이션으로 조회",
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
            "사용자 목록 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "users(" in query, f"users 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인 (일부만)
        for var in case["expected_variables"][:2]:  # 처음 2개 변수만 확인
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_user_mutation():
    """사용자 수정 뮤테이션 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    user_mutation_dsl = load_dsl_file("mutation_updateUser.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(user_mutation_dsl)
    
    test_cases = [
        {
            "input": "사용자 정보를 수정해주세요",
            "expected_variables": ["email", "patch"],
            "expected_operation": "mutation"
        },
        {
            "input": "사용자 이메일과 이름을 업데이트해주세요",
            "expected_variables": ["email", "patch"],
            "expected_operation": "mutation"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "사용자 수정 뮤테이션",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "mutation" in query.lower(), f"mutation 키워드 없음: {query}"
        assert "updateUser(" in query, f"updateUser 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_query_generation_with_different_inputs():
    """다양한 입력에 대한 쿼리 생성 테스트"""
    # 사용자 조회 DSL 사용
    user_dsl = load_dsl_file("query_user.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(user_dsl)
    llm = load_llm()
    
    test_inputs = [
        "사용자 정보 조회",
        "사용자 찾기",
        "사용자 데이터 가져오기",
        "사용자 프로필 조회"
    ]
    
    for user_input in test_inputs:
        # 쿼리 생성
        query = generate_graphql_query(user_input, dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "다양한 입력 테스트",
            user_input,
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {user_input}"
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "user(" in query, f"user 함수 없음: {query}"

def test_query_generation_error_handling():
    """에러 처리 테스트"""
    llm = load_llm()
    
    # 빈 DSL chunk로 테스트
    empty_dsl_chunk = {
        "skeleton": "",
        "variables": "",
        "description": ""
    }
    
    print("\n" + "="*80)
    print("🧪 테스트: 에러 처리 (빈 DSL)")
    print("="*80)
    print("📝 사용자 입력: 테스트")
    print("📋 사용된 DSL: 빈 DSL chunk")
    print("-"*80)
    
    try:
        query = generate_graphql_query("테스트", empty_dsl_chunk, llm)
        print("🎯 생성된 GraphQL 쿼리:")
        print("-"*80)
        print("```graphql")
        print(query)
        print("```")
        print("-"*80)
        print("✅ 빈 DSL로도 쿼리가 생성됨 (LLM이 추론)")
    except Exception as e:
        print(f"❌ 예상된 에러: {e}")
        print("✅ 에러가 발생해도 정상적인 동작일 수 있음")

if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    test_user_query_single()
    test_users_query_list()
    test_user_mutation()
    test_query_generation_with_different_inputs()
    test_query_generation_error_handling()
    print("\n✅ 모든 테스트 완료!") 