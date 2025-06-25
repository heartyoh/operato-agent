#!/usr/bin/env python3
"""
GraphQL 스키마를 OpenAPI 스펙으로 변환하는 스크립트
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any

def parse_graphql_schema(schema_path: str) -> Dict[str, Any]:
    """GraphQL 스키마 파일을 파싱"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 간단한 파싱 (실제로는 더 정교한 GraphQL 파서 사용 권장)
    schema_data = {
        'types': {},
        'queries': {},
        'mutations': {}
    }
    
    # 기본적인 타입 추출
    lines = content.split('\n')
    current_type = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('type ') and not line.startswith('type Query') and not line.startswith('type Mutation'):
            # 타입 정의 추출
            type_name = line.split()[1].split('{')[0].strip()
            schema_data['types'][type_name] = {
                'fields': {},
                'description': ''
            }
            current_type = type_name
        elif line.startswith('type Query'):
            current_type = 'Query'
        elif line.startswith('type Mutation'):
            current_type = 'Mutation'
        elif line.startswith('#'):
            # 주석을 설명으로 사용
            if current_type and current_type in schema_data['types']:
                schema_data['types'][current_type]['description'] = line[1:].strip()
        elif ':' in line and current_type and not line.startswith('{') and not line.startswith('}'):
            # 필드 정의 추출
            if current_type in ['Query', 'Mutation']:
                field_name = line.split(':')[0].strip()
                field_type = line.split(':')[1].split('(')[0].strip()
                if current_type == 'Query':
                    schema_data['queries'][field_name] = {
                        'type': field_type,
                        'description': ''
                    }
                else:
                    schema_data['mutations'][field_name] = {
                        'type': field_type,
                        'description': ''
                    }
    
    return schema_data

def generate_openapi_spec(graphql_schema: Dict[str, Any]) -> Dict[str, Any]:
    """GraphQL 스키마를 OpenAPI 스펙으로 변환"""
    
    openapi_spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Operato API',
            'description': 'Operato 서비스 API 스펙 (GraphQL에서 변환)',
            'version': '1.0.0'
        },
        'servers': [
            {
                'url': 'https://api.operato.com',
                'description': 'Operato API 서버'
            }
        ],
        'paths': {},
        'components': {
            'schemas': {},
            'parameters': {}
        }
    }
    
    # Query를 GET 엔드포인트로 변환
    for query_name, query_info in graphql_schema['queries'].items():
        # GraphQL 쿼리명을 REST 엔드포인트로 변환
        endpoint = f"/api/{query_name.lower()}"
        
        openapi_spec['paths'][endpoint] = {
            'get': {
                'summary': f"{query_name} 조회",
                'description': query_info.get('description', f'{query_name} 데이터를 조회합니다.'),
                'operationId': f"get{query_name}",
                'tags': ['queries'],
                'parameters': [
                    {
                        'name': 'filters',
                        'in': 'query',
                        'description': '필터 조건',
                        'required': False,
                        'schema': {
                            'type': 'string'
                        }
                    },
                    {
                        'name': 'pagination',
                        'in': 'query',
                        'description': '페이지네이션 정보',
                        'required': False,
                        'schema': {
                            'type': 'string'
                        }
                    }
                ],
                'responses': {
                    '200': {
                        'description': '성공',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'data': {
                                            'type': 'object',
                                            'description': f'{query_name} 데이터'
                                        }
                                    }
                                }
                            }
                        }
                    },
                    '400': {
                        'description': '잘못된 요청'
                    },
                    '500': {
                        'description': '서버 오류'
                    }
                }
            }
        }
    
    # Mutation을 POST/PUT/DELETE 엔드포인트로 변환
    for mutation_name, mutation_info in graphql_schema['mutations'].items():
        endpoint = f"/api/{mutation_name.lower()}"
        
        # 뮤테이션 타입에 따라 HTTP 메서드 결정
        if 'create' in mutation_name.lower() or 'add' in mutation_name.lower():
            method = 'post'
        elif 'update' in mutation_name.lower() or 'modify' in mutation_name.lower():
            method = 'put'
        elif 'delete' in mutation_name.lower() or 'remove' in mutation_name.lower():
            method = 'delete'
        else:
            method = 'post'
        
        openapi_spec['paths'][endpoint] = {
            method: {
                'summary': f"{mutation_name} 실행",
                'description': mutation_info.get('description', f'{mutation_name} 작업을 실행합니다.'),
                'operationId': f"{method}{mutation_name}",
                'tags': ['mutations'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'input': {
                                        'type': 'object',
                                        'description': '입력 데이터'
                                    }
                                }
                            }
                        }
                    }
                },
                'responses': {
                    '200': {
                        'description': '성공',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'data': {
                                            'type': 'object',
                                            'description': f'{mutation_name} 결과'
                                        }
                                    }
                                }
                            }
                        }
                    },
                    '400': {
                        'description': '잘못된 요청'
                    },
                    '500': {
                        'description': '서버 오류'
                    }
                }
            }
        }
    
    return openapi_spec

def save_openapi_spec(openapi_spec: Dict[str, Any], output_path: str):
    """OpenAPI 스펙을 파일로 저장"""
    output_file = Path(output_path)
    
    if output_file.suffix.lower() in ['.yaml', '.yml']:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

def main():
    """메인 함수"""
    # 입력 파일 경로
    graphql_schema_path = "data/graphql/schema.graphql"
    openapi_output_path = "data/openapi.yaml"
    
    print(f"GraphQL 스키마 파싱 중: {graphql_schema_path}")
    
    # GraphQL 스키마 파싱
    graphql_schema = parse_graphql_schema(graphql_schema_path)
    
    print(f"발견된 쿼리: {len(graphql_schema['queries'])}개")
    print(f"발견된 뮤테이션: {len(graphql_schema['mutations'])}개")
    
    # OpenAPI 스펙 생성
    print("OpenAPI 스펙 생성 중...")
    openapi_spec = generate_openapi_spec(graphql_schema)
    
    # 파일 저장
    print(f"OpenAPI 스펙 저장 중: {openapi_output_path}")
    save_openapi_spec(openapi_spec, openapi_output_path)
    
    print("✅ OpenAPI 스펙 생성 완료!")
    print(f"생성된 엔드포인트: {len(openapi_spec['paths'])}개")

if __name__ == "__main__":
    main() 