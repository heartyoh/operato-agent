#!/usr/bin/env python3
"""
GraphQL과 OpenAPI를 모두 지원하는 통합 쿼리 생성기
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

class IntegratedQueryGenerator:
    """통합 쿼리 생성기"""
    
    def __init__(self, openai_api_key: str, rag_index_path: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        
        # RAG 인덱스 로드
        self.vectorstore = Chroma(
            persist_directory=rag_index_path,
            embedding_function=self.embeddings
        )
        
        # 프로토콜 감지 프롬프트
        self.protocol_detection_prompt = ChatPromptTemplate.from_template("""
다음 사용자 요청을 분석하여 어떤 API 프로토콜(GraphQL 또는 REST/OpenAPI)이 적합한지 판단하세요.

사용자 요청: {user_query}

판단 기준:
- GraphQL: 복잡한 데이터 조회, 중첩된 관계, 단일 엔드포인트, 타입 시스템 활용
- REST/OpenAPI: 간단한 CRUD 작업, 리소스 중심, 표준 HTTP 메서드

응답 형식:
```json
{{
  "protocol": "graphql|rest",
  "reasoning": "선택 이유 설명",
  "confidence": 0.0-1.0
}}
```
""")
        
        # GraphQL 쿼리 생성 프롬프트
        self.graphql_prompt = ChatPromptTemplate.from_template("""
다음 GraphQL 스키마 정보를 바탕으로 사용자 요청에 맞는 GraphQL 쿼리를 생성하세요.

GraphQL 스키마 정보:
{context}

사용자 요청: {user_query}

요구사항:
1. 유효한 GraphQL 쿼리 구문 사용
2. 필요한 필드만 선택
3. 적절한 인자 사용
4. 에러 처리 고려

생성된 GraphQL 쿼리:
""")
        
        # REST API 요청 생성 프롬프트
        self.rest_prompt = ChatPromptTemplate.from_template("""
다음 OpenAPI 스펙 정보를 바탕으로 사용자 요청에 맞는 REST API 요청을 생성하세요.

OpenAPI 스펙 정보:
{context}

사용자 요청: {user_query}

요구사항:
1. 적절한 HTTP 메서드 선택
2. 올바른 엔드포인트 사용
3. 필요한 헤더 포함
4. 요청 본문 구성 (필요시)
5. 쿼리 파라미터 사용 (필요시)

생성된 REST API 요청:
""")
    
    def detect_protocol(self, user_query: str) -> Dict[str, Any]:
        """사용자 요청에 적합한 프로토콜 감지"""
        response = self.llm.invoke(
            self.protocol_detection_prompt.format(user_query=user_query)
        )
        
        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # 기본값으로 GraphQL 반환
            return {
                "protocol": "graphql",
                "reasoning": "JSON 파싱 실패로 기본값 사용",
                "confidence": 0.5
            }
    
    def search_relevant_context(self, user_query: str, protocol: str, k: int = 5) -> List[Document]:
        """관련 컨텍스트 검색"""
        # 프로토콜별 필터링을 위한 쿼리 수정
        if protocol == "graphql":
            search_query = f"{user_query} GraphQL schema types queries mutations"
        else:
            search_query = f"{user_query} REST API OpenAPI operations endpoints"
        
        results = self.vectorstore.similarity_search(search_query, k=k)
        
        # 프로토콜별 필터링
        filtered_results = [
            doc for doc in results 
            if doc.metadata.get('type') == protocol
        ]
        
        return filtered_results
    
    def generate_graphql_query(self, user_query: str, context_docs: List[Document]) -> str:
        """GraphQL 쿼리 생성"""
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        
        response = self.llm.invoke(
            self.graphql_prompt.format(
                context=context_text,
                user_query=user_query
            )
        )
        
        return response.content.strip()
    
    def generate_rest_request(self, user_query: str, context_docs: List[Document]) -> str:
        """REST API 요청 생성"""
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        
        response = self.llm.invoke(
            self.rest_prompt.format(
                context=context_text,
                user_query=user_query
            )
        )
        
        return response.content.strip()
    
    def generate_query(self, user_query: str) -> Dict[str, Any]:
        """통합 쿼리 생성"""
        print(f"🔍 사용자 요청 분석: {user_query}")
        
        # 프로토콜 감지
        protocol_result = self.detect_protocol(user_query)
        protocol = protocol_result["protocol"]
        confidence = protocol_result["confidence"]
        
        print(f"📡 감지된 프로토콜: {protocol} (신뢰도: {confidence:.2f})")
        print(f"💭 판단 근거: {protocol_result['reasoning']}")
        
        # 관련 컨텍스트 검색
        context_docs = self.search_relevant_context(user_query, protocol)
        print(f"📚 관련 컨텍스트: {len(context_docs)}개 문서")
        
        # 쿼리 생성
        if protocol == "graphql":
            generated_query = self.generate_graphql_query(user_query, context_docs)
        else:
            generated_query = self.generate_rest_request(user_query, context_docs)
        
        # 결과 구성
        result = {
            "user_query": user_query,
            "detected_protocol": protocol,
            "confidence": confidence,
            "reasoning": protocol_result["reasoning"],
            "generated_query": generated_query,
            "context_sources": [
                {
                    "source": doc.metadata.get('source', 'Unknown'),
                    "type": doc.metadata.get('type', 'Unknown'),
                    "content_preview": doc.page_content[:200] + "..."
                }
                for doc in context_docs
            ]
        }
        
        return result

def main():
    """메인 함수"""
    import os
    import yaml
    
    # 설정 파일 로드
    config_path = "config/settings.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        openai_api_key = config.get('llm', {}).get('openai_api_key')
        rag_index_path = config.get('chroma', {}).get('persist_directory', 'rag/chroma_db')
        
        if not openai_api_key:
            print("❌ 설정 파일에서 OpenAI API 키를 찾을 수 없습니다.")
            return
    else:
        # 환경변수에서 API 키 확인 (fallback)
        openai_api_key = os.getenv('OPENAI_API_KEY')
        rag_index_path = "rag/chroma_db"
        
        if not openai_api_key:
            print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            return
    
    print(f"✅ OpenAI API 키: 설정됨")
    print(f"📁 ChromaDB 경로: {rag_index_path}")
    
    # 통합 쿼리 생성기 초기화
    generator = IntegratedQueryGenerator(openai_api_key, rag_index_path)
    
    # 테스트 쿼리들
    test_queries = [
        "모든 시나리오 목록을 가져와주세요",
        "특정 시나리오의 상세 정보를 조회하고 싶습니다",
        "새로운 시나리오를 실행해주세요",
        "보드 데이터를 조회하고 관련 시나리오도 함께 가져와주세요",
        "시나리오 인스턴스를 중지해주세요"
    ]
    
    print("🚀 통합 쿼리 생성기 테스트 시작\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"=== 테스트 {i} ===")
        result = generator.generate_query(query)
        
        print(f"📝 생성된 쿼리:")
        print(f"프로토콜: {result['detected_protocol']}")
        print(f"신뢰도: {result['confidence']:.2f}")
        print(f"쿼리:\n{result['generated_query']}")
        print(f"참조 소스: {len(result['context_sources'])}개")
        print("-" * 50)
    
    # 인터랙티브 모드
    print("\n🎯 인터랙티브 모드 시작 (종료하려면 'quit' 입력)")
    while True:
        user_input = input("\n질문을 입력하세요: ").strip()
        if user_input.lower() in ['quit', 'exit', '종료']:
            break
        
        if user_input:
            result = generator.generate_query(user_input)
            print(f"\n📡 프로토콜: {result['detected_protocol']} (신뢰도: {result['confidence']:.2f})")
            print(f"💭 판단 근거: {result['reasoning']}")
            print(f"\n📝 생성된 쿼리:\n{result['generated_query']}")

if __name__ == "__main__":
    main() 