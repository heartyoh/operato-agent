#!/usr/bin/env python3
"""
GraphQL과 OpenAPI DSL을 통합하여 RAG 인덱스를 구축하는 스크립트
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain이 설치되지 않았습니다. 문서 생성만 진행합니다.")

class IntegratedRAGBuilder:
    """통합 RAG 인덱스 빌더"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        
        if LANGCHAIN_AVAILABLE and openai_api_key:
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
        else:
            self.embeddings = None
            self.text_splitter = None
    
    def load_graphql_dsl(self, dsl_dir: str) -> List[Dict[str, Any]]:
        """GraphQL DSL 파일들을 로드"""
        documents = []
        dsl_path = Path(dsl_dir)
        
        # DSL JSON 파일들 처리
        for json_file in dsl_path.glob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                dsl_data = json.load(f)
            
            # DSL 데이터를 텍스트로 변환
            content = self._dsl_to_text(dsl_data, "GraphQL")
            metadata = {
                'source': str(json_file),
                'type': 'graphql',
                'dsl_name': dsl_data.get('name', 'Unknown')
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        # DSL YAML 파일들 처리
        for yaml_file in dsl_path.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                dsl_data = yaml.safe_load(f)
            
            # DSL 데이터를 텍스트로 변환
            content = self._dsl_to_text(dsl_data, "GraphQL")
            metadata = {
                'source': str(yaml_file),
                'type': 'graphql',
                'dsl_name': dsl_data.get('name', yaml_file.stem)
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        # DSL 마크다운 파일들 처리
        for md_file in dsl_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                'source': str(md_file),
                'type': 'graphql',
                'dsl_name': md_file.stem
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        return documents
    
    def load_openapi_dsl(self, dsl_dir: str) -> List[Dict[str, Any]]:
        """OpenAPI DSL 파일들을 로드"""
        documents = []
        dsl_path = Path(dsl_dir)
        
        # 메인 DSL JSON 파일 처리
        main_dsl_file = dsl_path / "openapi_dsl.json"
        if main_dsl_file.exists():
            with open(main_dsl_file, 'r', encoding='utf-8') as f:
                dsl_data = json.load(f)
            
            content = self._dsl_to_text(dsl_data, "OpenAPI")
            metadata = {
                'source': str(main_dsl_file),
                'type': 'openapi',
                'dsl_name': dsl_data.get('name', 'OpenAPI Service')
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        # 메인 DSL YAML 파일 처리
        main_dsl_yaml = dsl_path / "openapi_dsl.yaml"
        if main_dsl_yaml.exists():
            with open(main_dsl_yaml, 'r', encoding='utf-8') as f:
                dsl_data = yaml.safe_load(f)
            
            content = self._dsl_to_text(dsl_data, "OpenAPI")
            metadata = {
                'source': str(main_dsl_yaml),
                'type': 'openapi',
                'dsl_name': dsl_data.get('name', 'OpenAPI Service')
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        # 개별 작업 파일들 처리 (YAML)
        operations_dir = dsl_path / "operations"
        if operations_dir.exists():
            for op_file in operations_dir.glob("*.yaml"):
                with open(op_file, 'r', encoding='utf-8') as f:
                    op_data = yaml.safe_load(f)
                
                content = self._operation_to_text(op_data)
                metadata = {
                    'source': str(op_file),
                    'type': 'openapi',
                    'operation': op_data.get('operationId', op_file.stem)
                }
                
                documents.append({
                    'content': content,
                    'metadata': metadata
                })
        
        # 개별 작업 파일들 처리 (마크다운)
        if operations_dir.exists():
            for op_file in operations_dir.glob("*.md"):
                with open(op_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                metadata = {
                    'source': str(op_file),
                    'type': 'openapi',
                    'operation': op_file.stem
                }
                
                documents.append({
                    'content': content,
                    'metadata': metadata
                })
        
        return documents
    
    def _dsl_to_text(self, dsl_data: Dict[str, Any], dsl_type: str) -> str:
        """DSL 데이터를 텍스트로 변환"""
        lines = []
        
        if dsl_type == "GraphQL":
            lines.append(f"# {dsl_data.get('name', 'GraphQL Schema')}")
            lines.append(f"Description: {dsl_data.get('description', '')}")
            
            # 쿼리 정보
            if 'queries' in dsl_data:
                lines.append("\n## Queries:")
                for query_name, query_info in dsl_data['queries'].items():
                    lines.append(f"- {query_name}: {query_info.get('type', '')}")
                    if query_info.get('description'):
                        lines.append(f"  Description: {query_info['description']}")
            
            # 뮤테이션 정보
            if 'mutations' in dsl_data:
                lines.append("\n## Mutations:")
                for mutation_name, mutation_info in dsl_data['mutations'].items():
                    lines.append(f"- {mutation_name}: {mutation_info.get('type', '')}")
                    if mutation_info.get('description'):
                        lines.append(f"  Description: {mutation_info['description']}")
            
            # 타입 정보
            if 'types' in dsl_data:
                lines.append("\n## Types:")
                for type_name, type_info in dsl_data['types'].items():
                    lines.append(f"- {type_name}")
                    if type_info.get('description'):
                        lines.append(f"  Description: {type_info['description']}")
        
        elif dsl_type == "OpenAPI":
            lines.append(f"# {dsl_data.get('name', 'OpenAPI Service')}")
            lines.append(f"Description: {dsl_data.get('description', '')}")
            lines.append(f"Base URL: {dsl_data.get('baseUrl', '')}")
            
            # 작업 정보
            if 'operations' in dsl_data:
                lines.append("\n## Operations:")
                for operation in dsl_data['operations']:
                    lines.append(f"- {operation.get('operationId', 'Unknown')}")
                    lines.append(f"  Method: {operation.get('method', '')}")
                    lines.append(f"  Path: {operation.get('path', '')}")
                    if operation.get('description'):
                        lines.append(f"  Description: {operation['description']}")
                    
                    # 파라미터 정보
                    if operation.get('parameters'):
                        lines.append("  Parameters:")
                        for param in operation['parameters']:
                            required = "Required" if param.get('required', False) else "Optional"
                            lines.append(f"    - {param['name']} ({param.get('type', 'string')}, {required})")
            
            # 태그 정보
            if 'tags' in dsl_data:
                lines.append("\n## Tags:")
                for tag_name, tag_info in dsl_data['tags'].items():
                    lines.append(f"- {tag_name}: {tag_info.get('description', '')}")
        
        return '\n'.join(lines)
    
    def _operation_to_text(self, operation_data: Dict[str, Any]) -> str:
        """개별 OpenAPI 작업을 텍스트로 변환"""
        lines = []
        
        lines.append(f"# {operation_data.get('operationId', 'Unknown Operation')}")
        lines.append(f"Method: {operation_data.get('method', '')}")
        lines.append(f"Path: {operation_data.get('path', '')}")
        
        if operation_data.get('summary'):
            lines.append(f"Summary: {operation_data['summary']}")
        
        if operation_data.get('description'):
            lines.append(f"Description: {operation_data['description']}")
        
        if operation_data.get('tags'):
            lines.append(f"Tags: {', '.join(operation_data['tags'])}")
        
        # 파라미터 정보
        if operation_data.get('parameters'):
            lines.append("\n## Parameters:")
            for param in operation_data['parameters']:
                required = "Required" if param.get('required', False) else "Optional"
                lines.append(f"- {param['name']} ({param.get('type', 'string')}, {required})")
                if param.get('description'):
                    lines.append(f"  Description: {param['description']}")
        
        # 요청 본문
        if operation_data.get('requestBody'):
            lines.append("\n## Request Body:")
            if operation_data['requestBody'].get('contentType'):
                lines.append(f"Content-Type: {operation_data['requestBody']['contentType']}")
            
            if operation_data['requestBody'].get('properties'):
                lines.append("Properties:")
                for prop_name, prop_info in operation_data['requestBody']['properties'].items():
                    lines.append(f"- {prop_name} ({prop_info.get('type', 'object')})")
                    if prop_info.get('description'):
                        lines.append(f"  Description: {prop_info['description']}")
        
        # 응답 정보
        if operation_data.get('responses'):
            lines.append("\n## Responses:")
            for status_code, response in operation_data['responses'].items():
                lines.append(f"- {status_code}: {response.get('description', '')}")
        
        return '\n'.join(lines)
    
    def build_integrated_index(self, graphql_dsl_dir: str, openapi_dsl_dir: str, output_dir: str):
        """통합 RAG 인덱스 구축"""
        print("GraphQL DSL 로드 중...")
        graphql_docs = self.load_graphql_dsl(graphql_dsl_dir)
        print(f"GraphQL 문서: {len(graphql_docs)}개")
        
        print("OpenAPI DSL 로드 중...")
        openapi_docs = self.load_openapi_dsl(openapi_dsl_dir)
        print(f"OpenAPI 문서: {len(openapi_docs)}개")
        
        # 모든 문서 통합
        all_docs = graphql_docs + openapi_docs
        print(f"총 문서: {len(all_docs)}개")
        
        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 문서를 파일로 저장 (RAG 인덱스 대신)
        print("문서 저장 중...")
        for i, doc in enumerate(all_docs):
            doc_file = output_path / f"document_{i:03d}.json"
            with open(doc_file, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
        
        # 통계 정보 저장
        stats = {
            'total_documents': len(all_docs),
            'graphql_documents': len(graphql_docs),
            'openapi_documents': len(openapi_docs),
            'sources': {
                'graphql': [doc['metadata']['source'] for doc in graphql_docs],
                'openapi': [doc['metadata']['source'] for doc in openapi_docs]
            }
        }
        
        with open(output_path / 'index_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 통합 문서 저장 완료!")
        print(f"저장 위치: {output_dir}")
        print(f"통계 정보 저장: {output_path / 'index_stats.json'}")
        
        # LangChain이 사용 가능하고 API 키가 있으면 벡터 스토어 생성
        if LANGCHAIN_AVAILABLE and self.openai_api_key:
            print("벡터 스토어 생성 중...")
            self._create_vectorstore(all_docs, output_path)
        
        return stats
    
    def _create_vectorstore(self, documents: List[Dict[str, Any]], output_path: Path):
        """벡터 스토어 생성 (LangChain 사용)"""
        # Document 객체로 변환
        langchain_docs = []
        for doc in documents:
            langchain_docs.append(Document(
                page_content=doc['content'],
                metadata=doc['metadata']
            ))
        
        # 문서 분할
        split_docs = []
        for doc in langchain_docs:
            splits = self.text_splitter.split_documents([doc])
            split_docs.extend(splits)
        
        print(f"분할된 문서: {len(split_docs)}개")
        
        # 벡터 스토어 생성
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embeddings,
            persist_directory=str(output_path / "chroma")
        )
        
        # 인덱스 저장
        vectorstore.persist()
        print("✅ 벡터 스토어 생성 완료!")

def main():
    """메인 함수"""
    import os
    import yaml
    
    # 설정 파일 로드
    config_path = "config/settings.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # OpenAI API 키 확인 (설정 파일에서 우선, 환경변수는 백업)
    openai_api_key = config.get('llm', {}).get('openai_api_key') or os.getenv('OPENAI_API_KEY')
    
    # 경로 설정 - 설정 파일에서 읽기
    graphql_dsl_dir = "generated_dsl/graphql_dsl"
    openapi_dsl_dir = "generated_dsl/openapi_dsl"
    output_dir = config.get('chroma', {}).get('persist_directory', 'rag/chroma_db')
    
    print(f"설정 파일 로드: {config_path}")
    print(f"OpenAI API 키: {'설정됨' if openai_api_key else '없음'}")
    print(f"ChromaDB 경로: {output_dir}")
    
    # RAG 빌더 초기화
    builder = IntegratedRAGBuilder(openai_api_key)
    
    # 통합 인덱스 구축
    stats = builder.build_integrated_index(graphql_dsl_dir, openapi_dsl_dir, output_dir)
    
    print(f"\n📊 최종 통계:")
    print(f"   총 문서: {stats['total_documents']}개")
    print(f"   GraphQL 문서: {stats['graphql_documents']}개")
    print(f"   OpenAPI 문서: {stats['openapi_documents']}개")

if __name__ == "__main__":
    main() 