import pytest
import yaml
import os
from llm.query_generator import generate_graphql_query
from llm.llm_client import load_llm

def load_dsl_file(filename):
    """실제 DSL 파일을 로드"""
    dsl_path = os.path.join("generated_dsls", filename)
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

def test_scenario_list_query():
    """시나리오 목록 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    scenarios_dsl = load_dsl_file("query_scenarios.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(scenarios_dsl)
    
    test_cases = [
        {
            "input": "시나리오 목록 조회",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "모든 시나리오 보여줘",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "시나리오 리스트 가져오기",
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
            "시나리오 목록 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "scenarios(" in query, f"scenarios 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인 (일부만)
        for var in case["expected_variables"][:2]:  # 처음 2개 변수만 확인
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_scenario_single_query():
    """단일 시나리오 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    scenario_dsl = load_dsl_file("query_scenario.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(scenario_dsl)
    
    test_cases = [
        {
            "input": "특정 시나리오 정보 조회",
            "expected_variables": ["id"],
            "expected_operation": "query"
        },
        {
            "input": "시나리오 상세 정보 보여줘",
            "expected_variables": ["id"],
            "expected_operation": "query"
        },
        {
            "input": "시나리오 ID로 조회",
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
            "단일 시나리오 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "scenario(" in query, f"scenario 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_scenario_instance_query():
    """시나리오 인스턴스 조회 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    scenario_instances_dsl = load_dsl_file("query_scenarioInstances.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(scenario_instances_dsl)
    
    test_cases = [
        {
            "input": "시나리오 인스턴스 목록 조회",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "시나리오 실행 인스턴스 보여줘",
            "expected_variables": ["filters", "pagination"],
            "expected_operation": "query"
        },
        {
            "input": "시나리오 인스턴스 리스트 가져오기",
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
            "시나리오 인스턴스 목록 조회",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "scenarioInstances(" in query, f"scenarioInstances 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인 (일부만)
        for var in case["expected_variables"][:2]:  # 처음 2개 변수만 확인
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_scenario_execution_mutation():
    """시나리오 실행 뮤테이션 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    scenario_execution_dsl = load_dsl_file("mutation_runScenario.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(scenario_execution_dsl)
    
    test_cases = [
        {
            "input": "시나리오 실행",
            "expected_variables": ["scenarioName", "variables"],
            "expected_operation": "mutation"
        },
        {
            "input": "시나리오 시작",
            "expected_variables": ["scenarioName", "variables"],
            "expected_operation": "mutation"
        },
        {
            "input": "시나리오를 실행해주세요",
            "expected_variables": ["scenarioName", "variables"],
            "expected_operation": "mutation"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "시나리오 실행 뮤테이션",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "mutation" in query.lower(), f"mutation 키워드 없음: {query}"
        assert "runScenario(" in query, f"runScenario 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_scenario_mutation():
    """시나리오 수정 뮤테이션 쿼리 생성 테스트"""
    # 실제 DSL 파일 로드
    scenario_mutation_dsl = load_dsl_file("mutation_updateScenario.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(scenario_mutation_dsl)
    
    test_cases = [
        {
            "input": "시나리오 정보를 수정해주세요",
            "expected_variables": ["name", "patch"],
            "expected_operation": "mutation"
        },
        {
            "input": "시나리오 이름과 설명을 업데이트해주세요",
            "expected_variables": ["name", "patch"],
            "expected_operation": "mutation"
        }
    ]
    
    llm = load_llm()
    
    for case in test_cases:
        # 쿼리 생성
        query = generate_graphql_query(case["input"], dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "시나리오 수정 뮤테이션",
            case["input"],
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {case['input']}"
        assert len(query.strip()) > 0, f"빈 쿼리 생성됨: {case['input']}"
        
        # GraphQL 문법 검증
        assert "mutation" in query.lower(), f"mutation 키워드 없음: {query}"
        assert "updateScenario(" in query, f"updateScenario 함수 없음: {query}"
        assert "{" in query, f"중괄호 없음: {query}"
        assert "}" in query, f"중괄호 없음: {query}"
        
        # 변수 존재 확인
        for var in case["expected_variables"]:
            assert f"${var}" in query, f"변수 없음: ${var} in {query}"

def test_scenario_query_generation_with_different_inputs():
    """다양한 시나리오 입력에 대한 쿼리 생성 테스트"""
    # 시나리오 조회 DSL 사용
    scenario_dsl = load_dsl_file("query_scenario.yaml")
    dsl_chunk = create_dsl_chunk_for_query_generator(scenario_dsl)
    llm = load_llm()
    
    test_inputs = [
        "시나리오 정보 조회",
        "시나리오 찾기",
        "시나리오 데이터 가져오기",
        "시나리오 상세 조회"
    ]
    
    for user_input in test_inputs:
        # 쿼리 생성
        query = generate_graphql_query(user_input, dsl_chunk, llm)
        
        # 결과 출력
        print_test_result(
            "다양한 시나리오 입력 테스트",
            user_input,
            dsl_chunk,
            query
        )
        
        # 기본 검증
        assert query is not None, f"쿼리 생성 실패: {user_input}"
        assert "query" in query.lower(), f"query 키워드 없음: {query}"
        assert "scenario(" in query, f"scenario 함수 없음: {query}"

if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    test_scenario_list_query()
    test_scenario_single_query()
    test_scenario_instance_query()
    test_scenario_execution_mutation()
    test_scenario_mutation()
    test_scenario_query_generation_with_different_inputs()
    print("\n✅ 모든 시나리오 테스트 완료!") 