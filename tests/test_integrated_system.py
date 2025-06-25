#!/usr/bin/env python3
"""
GraphQL과 OpenAPI 통합 시스템 테스트
"""

import os
import sys
import json
import pytest
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dsl_registry.integrated_rag_builder import IntegratedRAGBuilder
from dsl_registry.integrated_query_generator import IntegratedQueryGenerator

class TestIntegratedSystem:
    """통합 시스템 테스트"""
    
    @pytest.fixture(scope="class")
    def openai_api_key(self):
        """OpenAI API 키 확인"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return api_key
    
    @pytest.fixture(scope="class")
    def rag_builder(self, openai_api_key):
        """RAG 빌더 초기화"""
        return IntegratedRAGBuilder(openai_api_key)
    
    @pytest.fixture(scope="class")
    def query_generator(self, openai_api_key):
        """쿼리 생성기 초기화"""
        rag_index_path = "rag_index/integrated"
        return IntegratedQueryGenerator(openai_api_key, rag_index_path)
    
    def test_openapi_dsl_generation(self):
        """OpenAPI DSL 생성 테스트"""
        from dsl_registry.openapi_to_dsl import main as generate_openapi_dsl
        
        # OpenAPI DSL 생성
        generate_openapi_dsl()
        
        # 생성된 파일 확인
        dsl_dir = Path("dsl_registry/openapi_dsl")
        assert dsl_dir.exists(), "OpenAPI DSL 디렉토리가 생성되지 않았습니다."
        
        # 메인 DSL 파일 확인
        main_dsl_file = dsl_dir / "openapi_dsl.json"
        assert main_dsl_file.exists(), "메인 DSL 파일이 생성되지 않았습니다."
        
        # DSL 내용 확인
        with open(main_dsl_file, 'r', encoding='utf-8') as f:
            dsl_data = json.load(f)
        
        assert 'operations' in dsl_data, "DSL에 operations가 없습니다."
        assert len(dsl_data['operations']) > 0, "DSL에 작업이 없습니다."
        
        # 개별 작업 파일 확인
        operations_dir = dsl_dir / "operations"
        assert operations_dir.exists(), "작업 디렉토리가 생성되지 않았습니다."
        
        operation_files = list(operations_dir.glob("*.md"))
        assert len(operation_files) > 0, "작업 파일이 생성되지 않았습니다."
        
        print(f"✅ OpenAPI DSL 생성 테스트 통과: {len(dsl_data['operations'])}개 작업")
    
    def test_integrated_rag_building(self, rag_builder):
        """통합 RAG 인덱스 구축 테스트"""
        graphql_dsl_dir = "dsl_registry/graphql_dsl"
        openapi_dsl_dir = "dsl_registry/openapi_dsl"
        output_dir = "rag_index/integrated"
        
        # 기존 인덱스 삭제 (테스트용)
        import shutil
        if Path(output_dir).exists():
            shutil.rmtree(output_dir)
        
        # 통합 인덱스 구축
        vectorstore = rag_builder.build_integrated_index(
            graphql_dsl_dir, openapi_dsl_dir, output_dir
        )
        
        # 인덱스 파일 확인
        assert Path(output_dir).exists(), "RAG 인덱스 디렉토리가 생성되지 않았습니다."
        
        # 통계 파일 확인
        stats_file = Path(output_dir) / "index_stats.json"
        assert stats_file.exists(), "통계 파일이 생성되지 않았습니다."
        
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        assert stats['total_documents'] > 0, "문서가 인덱스에 없습니다."
        assert stats['graphql_documents'] > 0, "GraphQL 문서가 없습니다."
        assert stats['openapi_documents'] > 0, "OpenAPI 문서가 없습니다."
        
        print(f"✅ 통합 RAG 인덱스 구축 테스트 통과:")
        print(f"   총 문서: {stats['total_documents']}개")
        print(f"   GraphQL 문서: {stats['graphql_documents']}개")
        print(f"   OpenAPI 문서: {stats['openapi_documents']}개")
        print(f"   분할된 문서: {stats['split_documents']}개")
    
    def test_protocol_detection(self, query_generator):
        """프로토콜 감지 테스트"""
        test_cases = [
            {
                "query": "모든 시나리오 목록을 가져와주세요",
                "expected_protocol": "rest",
                "description": "간단한 목록 조회"
            },
            {
                "query": "보드 데이터를 조회하고 관련 시나리오도 함께 가져와주세요",
                "expected_protocol": "graphql",
                "description": "복잡한 관계 조회"
            },
            {
                "query": "새로운 시나리오를 실행해주세요",
                "expected_protocol": "rest",
                "description": "액션 실행"
            },
            {
                "query": "특정 보드의 모든 정보와 관련된 시나리오, 사용자 정보를 한 번에 가져와주세요",
                "expected_protocol": "graphql",
                "description": "복잡한 중첩 조회"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 프로토콜 감지 테스트 {i}: {test_case['description']}")
            
            result = query_generator.detect_protocol(test_case["query"])
            
            detected_protocol = result["protocol"]
            confidence = result["confidence"]
            
            print(f"   예상: {test_case['expected_protocol']}")
            print(f"   감지: {detected_protocol} (신뢰도: {confidence:.2f})")
            print(f"   근거: {result['reasoning']}")
            
            # 신뢰도가 높은 경우에만 정확성 검증
            if confidence > 0.7:
                assert detected_protocol == test_case["expected_protocol"], \
                    f"프로토콜 감지 실패: 예상 {test_case['expected_protocol']}, 실제 {detected_protocol}"
            
            assert confidence >= 0.0 and confidence <= 1.0, "신뢰도가 유효하지 않습니다."
        
        print("✅ 프로토콜 감지 테스트 통과")
    
    def test_query_generation(self, query_generator):
        """쿼리 생성 테스트"""
        test_queries = [
            "시나리오 목록을 가져와주세요",
            "보드 정보와 관련 시나리오를 함께 조회해주세요",
            "새로운 시나리오를 실행해주세요"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 쿼리 생성 테스트 {i}: {query}")
            
            result = query_generator.generate_query(query)
            
            # 기본 구조 확인
            assert "user_query" in result, "결과에 user_query가 없습니다."
            assert "detected_protocol" in result, "결과에 detected_protocol이 없습니다."
            assert "generated_query" in result, "결과에 generated_query가 없습니다."
            assert "confidence" in result, "결과에 confidence가 없습니다."
            
            # 생성된 쿼리 확인
            generated_query = result["generated_query"]
            assert len(generated_query.strip()) > 0, "생성된 쿼리가 비어있습니다."
            
            print(f"   프로토콜: {result['detected_protocol']}")
            print(f"   신뢰도: {result['confidence']:.2f}")
            print(f"   생성된 쿼리: {generated_query[:100]}...")
            print(f"   참조 소스: {len(result['context_sources'])}개")
        
        print("✅ 쿼리 생성 테스트 통과")
    
    def test_context_search(self, query_generator):
        """컨텍스트 검색 테스트"""
        test_queries = [
            ("시나리오 관련", "rest"),
            ("보드 조회", "graphql"),
            ("API 엔드포인트", "rest")
        ]
        
        for query, expected_type in test_queries:
            print(f"\n🔍 컨텍스트 검색 테스트: {query} (예상 타입: {expected_type})")
            
            context_docs = query_generator.search_relevant_context(query, expected_type)
            
            assert len(context_docs) > 0, f"'{query}'에 대한 컨텍스트를 찾을 수 없습니다."
            
            # 타입 필터링 확인
            for doc in context_docs:
                doc_type = doc.metadata.get('type', 'Unknown')
                print(f"   문서 타입: {doc_type}, 소스: {doc.metadata.get('source', 'Unknown')}")
            
            print(f"   찾은 문서: {len(context_docs)}개")
        
        print("✅ 컨텍스트 검색 테스트 통과")
    
    def test_end_to_end_workflow(self, query_generator):
        """전체 워크플로우 테스트"""
        print("\n🚀 전체 워크플로우 테스트")
        
        # 실제 사용 시나리오 테스트
        scenarios = [
            {
                "name": "시나리오 관리",
                "queries": [
                    "모든 시나리오 목록을 가져와주세요",
                    "특정 시나리오의 상세 정보를 조회해주세요",
                    "새로운 시나리오를 실행해주세요"
                ]
            },
            {
                "name": "보드 관리",
                "queries": [
                    "보드 목록을 조회해주세요",
                    "보드 정보와 관련 시나리오를 함께 가져와주세요"
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📋 시나리오: {scenario['name']}")
            
            for query in scenario['queries']:
                print(f"  🔍 질문: {query}")
                
                result = query_generator.generate_query(query)
                
                print(f"    📡 프로토콜: {result['detected_protocol']}")
                print(f"    💯 신뢰도: {result['confidence']:.2f}")
                print(f"    📝 쿼리: {result['generated_query'][:80]}...")
                
                # 기본 검증
                assert result['detected_protocol'] in ['graphql', 'rest'], "잘못된 프로토콜"
                assert result['confidence'] >= 0.0 and result['confidence'] <= 1.0, "잘못된 신뢰도"
                assert len(result['generated_query'].strip()) > 0, "빈 쿼리"
        
        print("✅ 전체 워크플로우 테스트 통과")

def main():
    """메인 테스트 실행"""
    print("🧪 GraphQL과 OpenAPI 통합 시스템 테스트 시작")
    
    # 테스트 실행
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])

if __name__ == "__main__":
    main() 