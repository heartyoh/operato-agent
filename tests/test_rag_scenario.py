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

def test_scenario_list_queries():
    """시나리오 목록 조회 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "시나리오 목록 조회",
            "expected_dsl": "scenarios",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "모든 시나리오 보여줘",
            "expected_dsl": "scenarios",
            "expected_variables": ["filters", "pagination"]
        },
        {
            "input": "시나리오 리스트 가져오기",
            "expected_dsl": "scenarios",
            "expected_variables": ["filters", "pagination"]
        }
    ]
    
    for case in test_cases:
        print_test_result("시나리오 목록 조회", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 시나리오 관련 DSL이 검색되었는지 확인
        scenario_dsls = [dsl for dsl in retrieved_dsls if 'scenario' in dsl['dsl_name'].lower()]
        assert len(scenario_dsls) > 0, f"시나리오 관련 DSL 없음: {case['input']}"
        
        # 가장 첫 번째 결과가 기대하는 DSL과 정확히 일치해야 함
        assert retrieved_dsls[0]["dsl_name"] == case["expected_dsl"], (
            f"가장 첫 번째 DSL이 예상과 다릅니다: {retrieved_dsls[0]['dsl_name']} != {case['expected_dsl']}\n"
            f"전체 결과: {[dsl['dsl_name'] for dsl in retrieved_dsls]}"
        )

def test_scenario_single_queries():
    """단일 시나리오 조회 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "특정 시나리오 정보 조회",
            "expected_dsl": "scenario",
            "expected_variables": ["id"]
        },
        {
            "input": "시나리오 상세 정보 보여줘",
            "expected_dsl": "scenario",
            "expected_variables": ["id"]
        },
        {
            "input": "시나리오 ID로 조회",
            "expected_dsl": "scenario",
            "expected_variables": ["id"]
        }
    ]
    
    for case in test_cases:
        print_test_result("단일 시나리오 조회", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 시나리오 관련 DSL이 검색되었는지 확인
        scenario_dsls = [dsl for dsl in retrieved_dsls if 'scenario' in dsl['dsl_name'].lower()]
        assert len(scenario_dsls) > 0, f"시나리오 관련 DSL 없음: {case['input']}"
        
        # 예상 DSL이 검색 결과에 포함되어 있는지 확인 (순서 무관)
        found_expected = any(case["expected_dsl"] in dsl["dsl_name"] for dsl in retrieved_dsls)
        assert found_expected, f"예상 DSL '{case['expected_dsl']}'이 검색 결과에 없음: {[dsl['dsl_name'] for dsl in retrieved_dsls]}"

def test_scenario_execution_queries():
    """시나리오 실행 관련 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "시나리오 실행",
            "expected_keywords": ["scenario", "run", "execute"]
        },
        {
            "input": "시나리오 시작",
            "expected_keywords": ["scenario", "start"]
        },
        {
            "input": "시나리오 인스턴스 조회",
            "expected_keywords": ["scenario", "instance"]
        }
    ]
    
    for case in test_cases:
        print_test_result("시나리오 실행", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 시나리오 관련 DSL이 검색되었는지 확인
        scenario_dsls = [dsl for dsl in retrieved_dsls if 'scenario' in dsl['dsl_name'].lower()]
        assert len(scenario_dsls) > 0, f"시나리오 관련 DSL 없음: {case['input']}"

def test_scenario_complex_queries():
    """복합 시나리오 쿼리 검색 테스트"""
    test_cases = [
        {
            "input": "시나리오 목록과 실행 상태 조회",
            "expected_keywords": ["scenario", "list", "status"]
        },
        {
            "input": "시나리오 정보와 인스턴스 함께 조회",
            "expected_keywords": ["scenario", "instance"]
        },
        {
            "input": "시나리오 스케줄과 실행 이력 조회",
            "expected_keywords": ["scenario", "schedule"]
        }
    ]
    
    for case in test_cases:
        print_test_result("복합 시나리오 쿼리", case["input"], [])
        
        # RAG 검색 실행
        retrieved_dsls = retrieve_relevant_dsl(case["input"])
        
        print(f"🔍 검색 결과:")
        for i, dsl in enumerate(retrieved_dsls, 1):
            print(f"  {i}. {dsl['dsl_name']} ({dsl['type']})")
        
        # 검증
        assert len(retrieved_dsls) > 0, f"검색 결과 없음: {case['input']}"
        
        # 시나리오 관련 DSL이 검색되었는지 확인
        scenario_dsls = [dsl for dsl in retrieved_dsls if 'scenario' in dsl['dsl_name'].lower()]
        assert len(scenario_dsls) > 0, f"시나리오 관련 DSL 없음: {case['input']}"

def test_scenario_search_accuracy():
    """시나리오 검색 정확도 테스트"""
    # 시나리오 관련 DSL 파일들 확인
    scenario_dsls = [
        "query_scenarios.yaml",
        "query_scenario.yaml", 
        "query_scenarioInstance.yaml",
        "query_scenarioInstances.yaml"
    ]
    
    for dsl_file in scenario_dsls:
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
    test_scenario_list_queries()
    test_scenario_single_queries()
    test_scenario_execution_queries()
    test_scenario_complex_queries()
    test_scenario_search_accuracy()
    print("\n✅ 모든 시나리오 테스트 완료!") 