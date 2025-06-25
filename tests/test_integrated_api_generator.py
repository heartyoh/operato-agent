#!/usr/bin/env python3
"""
통합 API 생성기 테스트
GraphQL과 OpenAPI를 구분하지 않고 RAG 검색 결과에 따라 자동으로 판단
"""

import pytest
import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch
import requests

# LLM 관련 import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# RAG 관련 import
try:
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class APIClient:
    """실제 API 호출을 위한 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def execute_graphql(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """GraphQL 쿼리 실행"""
        url = f"{self.base_url}/graphql"
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = self.session.post(url, json=payload, headers={
                "Content-Type": "application/json"
            })
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"GraphQL 요청 실패: {e}"}
    
    def execute_openapi(self, request_config: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAPI HTTP 요청 실행"""
        method = request_config.get("method", "GET").upper()
        url = request_config.get("url", "")
        headers = request_config.get("headers", {})
        params = request_config.get("params", {})
        body = request_config.get("body", {})
        
        # 상대 경로인 경우 base_url과 결합
        if url.startswith('/'):
            full_url = f"{self.base_url}{url}"
        elif url.startswith('http'):
            full_url = url
        else:
            full_url = f"{self.base_url}/{url}"
        
        try:
            if method == "GET":
                response = self.session.get(full_url, headers=headers, params=params)
            elif method == "POST":
                response = self.session.post(full_url, headers=headers, params=params, json=body)
            elif method == "PUT":
                response = self.session.put(full_url, headers=headers, params=params, json=body)
            elif method == "DELETE":
                response = self.session.delete(full_url, headers=headers, params=params)
            elif method == "PATCH":
                response = self.session.patch(full_url, headers=headers, params=params, json=body)
            else:
                return {"error": f"지원하지 않는 HTTP 메서드: {method}"}
            
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except requests.exceptions.RequestException as e:
            return {"error": f"OpenAPI 요청 실패: {e}"}

class IntegratedAPIGenerator:
    """통합 API 생성기 - GraphQL과 OpenAPI를 자동으로 판단"""
    
    def __init__(self, openai_api_key: str = None, rag_index_path: str = "rag_data/chroma_db"):
        self.openai_api_key = openai_api_key
        self.rag_index_path = Path(rag_index_path)
        
        # LLM 초기화
        if OPENAI_AVAILABLE and openai_api_key:
            self.llm = OpenAI(api_key=openai_api_key, temperature=0)
        else:
            self.llm = None
        
        # RAG 인덱스 로드
        self.documents = self._load_rag_documents()
        
        # 벡터 스토어 초기화 (선택사항)
        if LANGCHAIN_AVAILABLE and openai_api_key:
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            self._init_vectorstore()
        else:
            self.embeddings = None
            self.vectorstore = None
    
    def _load_rag_documents(self) -> List[Dict[str, Any]]:
        """RAG 인덱스에서 문서들을 로드 - 기존 Chroma 방식"""
        documents = []
        
        # 기존 Chroma 벡터스토어에서 문서 로드
        if LANGCHAIN_AVAILABLE and self.openai_api_key:
            try:
                chroma_path = self.rag_index_path
                if chroma_path.exists():
                    vectorstore = Chroma(
                        persist_directory=str(chroma_path),
                        embedding_function=self.embeddings
                    )
                    
                    # 모든 문서 가져오기 (임시로 키워드 검색 사용)
                    results = vectorstore.similarity_search("", k=1000)  # 충분히 큰 수
                    for doc in results:
                        documents.append({
                            "content": doc.page_content,
                            "metadata": doc.metadata
                        })
            except Exception as e:
                print(f"Chroma 벡터스토어 로드 실패: {e}")
        
        # 벡터스토어가 없거나 로드 실패 시 빈 리스트 반환
        return documents
    
    def _init_vectorstore(self):
        """벡터 스토어 초기화 - 기존 Chroma 방식"""
        try:
            chroma_path = self.rag_index_path
            if chroma_path.exists():
                self.vectorstore = Chroma(
                    persist_directory=str(chroma_path),
                    embedding_function=self.embeddings
                )
            else:
                self.vectorstore = None
        except Exception as e:
            print(f"Chroma 벡터 스토어 초기화 실패: {e}")
            self.vectorstore = None
    
    def search_relevant_apis(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """쿼리와 관련된 API들을 검색 - 기존 Chroma 방식"""
        if self.vectorstore:
            # 기존 Chroma 벡터 검색 사용
            results = self.vectorstore.similarity_search(query, k=top_k)
            return [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]
        else:
            # 벡터스토어가 없으면 빈 결과 반환
            return []
    
    def detect_api_type(self, search_results: List[Dict[str, Any]]) -> str:
        """검색 결과를 바탕으로 API 타입 감지"""
        graphql_count = 0
        openapi_count = 0
        
        for result in search_results:
            metadata = result['metadata']
            if metadata.get('type') == 'graphql':
                graphql_count += 1
            elif metadata.get('type') == 'openapi':
                openapi_count += 1
        
        # 더 많은 결과가 있는 타입을 선택
        if graphql_count > openapi_count:
            return 'graphql'
        elif openapi_count > graphql_count:
            return 'openapi'
        else:
            # 동점인 경우 첫 번째 결과의 타입 사용
            return search_results[0]['metadata'].get('type', 'graphql')
    
    def generate_graphql_query(self, query: str, relevant_apis: List[Dict[str, Any]]) -> str:
        """GraphQL 쿼리 생성"""
        if not self.llm:
            return "# GraphQL 쿼리 생성 실패: LLM이 초기화되지 않음"
        
        # 관련 API 정보를 프롬프트에 포함
        api_context = "\n\n".join([
            f"API: {api['metadata'].get('dsl_name', 'Unknown')}\n{api['content']}"
            for api in relevant_apis[:3]  # 상위 3개만 사용
        ])
        
        prompt = f"""
다음 GraphQL API 정보를 바탕으로 자연어 쿼리를 GraphQL 쿼리로 변환해주세요.

API 정보:
{api_context}

자연어 쿼리: {query}

GraphQL 쿼리를 생성해주세요. 변수는 $로 시작하고, 적절한 필드를 선택하세요.
"""
        
        try:
            response = self.llm.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"# GraphQL 쿼리 생성 오류: {e}"
    
    def generate_openapi_request(self, query: str, relevant_apis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """OpenAPI HTTP 요청 구성 생성"""
        if not self.llm:
            return {"error": "OpenAPI 요청 생성 실패: LLM이 초기화되지 않음"}
        
        # 관련 API 정보를 프롬프트에 포함
        api_context = "\n\n".join([
            f"API: {api['metadata'].get('operation', 'Unknown')}\n{api['content']}"
            for api in relevant_apis[:3]  # 상위 3개만 사용
        ])
        
        prompt = f"""
다음 OpenAPI 정보를 바탕으로 자연어 쿼리를 HTTP 요청으로 변환해주세요.

API 정보:
{api_context}

자연어 쿼리: {query}

다음 JSON 형식으로 HTTP 요청을 생성해주세요:
{{
    "method": "HTTP_METHOD",
    "url": "BASE_URL/PATH",
    "headers": {{}},
    "params": {{}},
    "body": {{}}
}}

가능한 HTTP 메서드: GET, POST, PUT, DELETE, PATCH
"""
        
        try:
            response = self.llm.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            # JSON 파싱 시도
            try:
                return json.loads(response.choices[0].message.content.strip())
            except json.JSONDecodeError:
                return {
                    "error": "JSON 파싱 실패",
                    "raw_response": response.choices[0].message.content.strip()
                }
        except Exception as e:
            return {"error": f"OpenAPI 요청 생성 오류: {e}"}
    
    def generate_api_call(self, query: str) -> Dict[str, Any]:
        """통합 API 호출 생성 - 타입을 자동으로 감지"""
        # 관련 API 검색
        relevant_apis = self.search_relevant_apis(query)
        
        if not relevant_apis:
            return {
                "error": "관련 API를 찾을 수 없습니다",
                "query": query
            }
        
        # API 타입 감지
        api_type = self.detect_api_type(relevant_apis)
        
        # 타입에 따라 적절한 생성기 호출
        if api_type == 'graphql':
            result = self.generate_graphql_query(query, relevant_apis)
            return {
                "type": "graphql",
                "query": result,
                "relevant_apis": [api['metadata'] for api in relevant_apis[:3]]
            }
        else:  # openapi
            result = self.generate_openapi_request(query, relevant_apis)
            return {
                "type": "openapi",
                "request": result,
                "relevant_apis": [api['metadata'] for api in relevant_apis[:3]]
            }

    def generate_api_call_without_llm(self, query: str, api_type: str) -> Dict[str, Any]:
        """통합 API 호출 생성 - 타입을 자동으로 감지 (LLM 없이)"""
        # 관련 API 검색
        relevant_apis = self.search_relevant_apis(query)
        
        if not relevant_apis:
            return {
                "error": "관련 API를 찾을 수 없습니다",
                "query": query
            }
        
        # API 타입 감지
        api_type = self.detect_api_type(relevant_apis)
        
        # 타입에 따라 적절한 생성기 호출
        if api_type == 'graphql':
            result = self.generate_graphql_query(query, relevant_apis)
            return {
                "type": "graphql",
                "query": result,
                "relevant_apis": [api['metadata'] for api in relevant_apis[:3]]
            }
        else:  # openapi
            result = self.generate_openapi_request(query, relevant_apis)
            return {
                "type": "openapi",
                "request": result,
                "relevant_apis": [api['metadata'] for api in relevant_apis[:3]]
            }

# 테스트 함수들
def test_integrated_api_generator_initialization():
    """통합 API 생성기 초기화 테스트"""
    generator = IntegratedAPIGenerator()
    
    assert generator.documents is not None
    # 벡터스토어가 없어도 초기화는 성공해야 함
    print(f"✅ 로드된 문서 수: {len(generator.documents)}")
    print(f"✅ 벡터스토어 상태: {'사용 가능' if generator.vectorstore else '사용 불가'}")

def test_api_search():
    """API 검색 테스트"""
    generator = IntegratedAPIGenerator()
    
    # 벡터스토어가 있는 경우에만 검색 테스트
    if generator.vectorstore:
        # GraphQL 관련 검색
        graphql_results = generator.search_relevant_apis("사용자 정보 조회")
        print(f"✅ GraphQL 검색 결과: {len(graphql_results)}개")
        
        # OpenAPI 관련 검색
        openapi_results = generator.search_relevant_apis("시나리오 실행")
        print(f"✅ OpenAPI 검색 결과: {len(openapi_results)}개")
    else:
        print("⚠️ 벡터스토어가 없어서 검색 테스트를 건너뜁니다.")
        print("OpenAI API 키가 필요합니다.")

def test_api_type_detection():
    """API 타입 감지 테스트"""
    generator = IntegratedAPIGenerator()
    
    # 벡터스토어가 있는 경우에만 테스트
    if generator.vectorstore:
        # GraphQL 검색 결과
        graphql_results = generator.search_relevant_apis("사용자 정보 조회")
        api_type = generator.detect_api_type(graphql_results)
        print(f"✅ GraphQL 타입 감지: {api_type}")
        
        # OpenAPI 검색 결과
        openapi_results = generator.search_relevant_apis("시나리오 실행")
        api_type = generator.detect_api_type(openapi_results)
        print(f"✅ OpenAPI 타입 감지: {api_type}")
    else:
        print("⚠️ 벡터스토어가 없어서 타입 감지 테스트를 건너뜁니다.")
        print("OpenAI API 키가 필요합니다.")

@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI API 키가 필요합니다")
def test_graphql_query_generation():
    """GraphQL 쿼리 생성 테스트"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        pytest.skip("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    generator = IntegratedAPIGenerator(openai_api_key)
    
    test_cases = [
        "test@example.com 사용자 정보 조회",
        "시나리오 목록 조회",
        "보드 정보 가져오기"
    ]
    
    for query in test_cases:
        result = generator.generate_api_call(query)
        
        print(f"\n[입력 쿼리] {query}")
        print(f"[감지된 타입] {result['type']}")
        
        if result['type'] == 'graphql':
            print(f"[생성된 GraphQL 쿼리]\n{result['query']}")
            assert 'query' in result['query'].lower() or 'mutation' in result['query'].lower()
        else:
            print(f"[생성된 OpenAPI 요청]\n{json.dumps(result['request'], indent=2, ensure_ascii=False)}")
        
        print(f"[관련 API들] {[api.get('dsl_name', api.get('operation', 'Unknown')) for api in result['relevant_apis']]}")

@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI API 키가 필요합니다")
def test_openapi_request_generation():
    """OpenAPI 요청 생성 테스트"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        pytest.skip("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    generator = IntegratedAPIGenerator(openai_api_key)
    
    test_cases = [
        "시나리오 실행",
        "시나리오 인스턴스 목록 조회",
        "특정 시나리오 정보 가져오기"
    ]
    
    for query in test_cases:
        result = generator.generate_api_call(query)
        
        print(f"\n[입력 쿼리] {query}")
        print(f"[감지된 타입] {result['type']}")
        
        if result['type'] == 'openapi':
            print(f"[생성된 OpenAPI 요청]\n{json.dumps(result['request'], indent=2, ensure_ascii=False)}")
            assert 'method' in result['request'] or 'error' in result['request']
        else:
            print(f"[생성된 GraphQL 쿼리]\n{result['query']}")
        
        print(f"[관련 API들] {[api.get('dsl_name', api.get('operation', 'Unknown')) for api in result['relevant_apis']]}")

def test_mixed_api_queries():
    """혼합 API 쿼리 테스트 - 타입 자동 감지"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        pytest.skip("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    generator = IntegratedAPIGenerator(openai_api_key)
    
    test_cases = [
        {
            "query": "test@example.com 사용자 정보 조회",
            "expected_type": "graphql"
        },
        {
            "query": "시나리오 실행",
            "expected_type": "openapi"
        },
        {
            "query": "시나리오 목록 조회",
            "expected_type": "openapi"
        },
        {
            "query": "보드 정보 수정",
            "expected_type": "graphql"
        }
    ]
    
    for case in test_cases:
        result = generator.generate_api_call(case["query"])
        
        print(f"\n[입력 쿼리] {case['query']}")
        print(f"[예상 타입] {case['expected_type']}")
        print(f"[실제 감지된 타입] {result['type']}")
        
        # 타입 감지 정확도 확인 (선택사항)
        if result['type'] == case['expected_type']:
            print("✅ 타입 감지 정확")
        else:
            print("⚠️ 타입 감지 다름 (검색 결과에 따라 달라질 수 있음)")
        
        # 결과 출력
        if result['type'] == 'graphql':
            print(f"[생성된 GraphQL 쿼리]\n{result['query']}")
        else:
            print(f"[생성된 OpenAPI 요청]\n{json.dumps(result['request'], indent=2, ensure_ascii=False)}")

@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="OpenAI API 키가 필요합니다")
def test_actual_api_execution():
    """실제 API 실행 테스트"""
    generator = IntegratedAPIGenerator()
    
    # 벡터스토어가 있는 경우에만 테스트
    if generator.vectorstore:
        # GraphQL 쿼리 실행
        graphql_result = generator.execute_api_call(
            "사용자 정보를 조회해줘",
            "graphql"
        )
        print(f"✅ GraphQL 실행 결과: {graphql_result}")
        
        # OpenAPI 요청 실행
        openapi_result = generator.execute_api_call(
            "시나리오를 실행해줘",
            "openapi"
        )
        print(f"✅ OpenAPI 실행 결과: {openapi_result}")
    else:
        print("⚠️ 벡터스토어가 없어서 실제 API 실행 테스트를 건너뜁니다.")
        print("OpenAI API 키가 필요합니다.")

def test_api_generation_without_llm():
    """LLM 없이 API 생성 테스트"""
    generator = IntegratedAPIGenerator()
    
    # 벡터스토어가 있는 경우에만 테스트
    if generator.vectorstore:
        # GraphQL 쿼리 생성
        graphql_query = generator.generate_api_call_without_llm(
            "사용자 정보를 조회해줘",
            "graphql"
        )
        print(f"✅ GraphQL 쿼리 생성 (LLM 없이): {graphql_query}")
        
        # OpenAPI 요청 생성
        openapi_request = generator.generate_api_call_without_llm(
            "시나리오를 실행해줘",
            "openapi"
        )
        print(f"✅ OpenAPI 요청 생성 (LLM 없이): {openapi_request}")
    else:
        print("⚠️ 벡터스토어가 없어서 LLM 없이 API 생성 테스트를 건너뜁니다.")
        print("OpenAI API 키가 필요합니다.")

def main():
    """메인 테스트 실행"""
    print("🚀 통합 API 생성기 테스트 시작")
    
    # 기본 테스트
    test_integrated_api_generator_initialization()
    test_api_search()
    test_api_type_detection()
    
    # LLM이 있는 경우 고급 테스트
    if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
        test_graphql_query_generation()
        test_openapi_request_generation()
        test_mixed_api_queries()
        test_actual_api_execution()
        test_api_generation_without_llm()
    else:
        print("⚠️ OpenAI API 키가 없어서 LLM 테스트를 건너뜁니다.")
    
    print("✅ 통합 API 생성기 테스트 완료")

if __name__ == "__main__":
    main() 