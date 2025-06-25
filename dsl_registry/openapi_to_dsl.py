#!/usr/bin/env python3
"""
OpenAPI 명세를 DSL로 변환하는 스크립트
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

def load_openapi_spec(spec_path: str) -> Dict[str, Any]:
    """OpenAPI 명세 파일 로드"""
    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_operation_info(operation: Dict[str, Any], method: str, path: str) -> Dict[str, Any]:
    """OpenAPI 작업에서 정보 추출"""
    return {
        'method': method.upper(),
        'path': path,
        'operationId': operation.get('operationId', ''),
        'summary': operation.get('summary', ''),
        'description': operation.get('description', ''),
        'tags': operation.get('tags', []),
        'parameters': operation.get('parameters', []),
        'requestBody': operation.get('requestBody', {}),
        'responses': operation.get('responses', {})
    }

def generate_dsl_from_openapi(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """OpenAPI 명세를 DSL로 변환"""
    
    dsl = {
        'version': '1.0',
        'name': openapi_spec.get('info', {}).get('title', 'OpenAPI Service'),
        'description': openapi_spec.get('info', {}).get('description', ''),
        'baseUrl': openapi_spec.get('servers', [{}])[0].get('url', '/'),
        'operations': [],
        'schemas': {},
        'tags': {}
    }
    
    # 태그 정보 수집
    for tag in openapi_spec.get('tags', []):
        dsl['tags'][tag['name']] = {
            'description': tag.get('description', ''),
            'operations': []
        }
    
    # 경로별 작업 처리
    for path, path_item in openapi_spec.get('paths', {}).items():
        for method, operation in path_item.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                op_info = extract_operation_info(operation, method, path)
                dsl['operations'].append(op_info)
                
                # 태그별 작업 분류
                for tag in op_info.get('tags', []):
                    if tag in dsl['tags']:
                        dsl['tags'][tag]['operations'].append(op_info['operationId'])
    
    # 스키마 정보 추가
    if 'components' in openapi_spec and 'schemas' in openapi_spec['components']:
        dsl['schemas'] = openapi_spec['components']['schemas']
    
    return dsl

def create_operation_yaml(operation: Dict[str, Any]) -> Dict[str, Any]:
    """개별 작업을 위한 YAML 데이터 생성"""
    
    yaml_data = {
        'operationId': operation['operationId'],
        'method': operation['method'],
        'path': operation['path'],
        'description': operation.get('description', ''),
        'summary': operation.get('summary', ''),
        'tags': operation.get('tags', [])
    }
    
    # 파라미터 정보
    if operation.get('parameters'):
        yaml_data['parameters'] = []
        for param in operation['parameters']:
            param_info = {
                'name': param['name'],
                'in': param.get('in', ''),
                'required': param.get('required', False),
                'type': param.get('schema', {}).get('type', 'string'),
                'description': param.get('description', '')
            }
            yaml_data['parameters'].append(param_info)
    
    # 요청 본문
    if operation.get('requestBody'):
        yaml_data['requestBody'] = {}
        content = operation['requestBody'].get('content', {})
        for content_type, content_info in content.items():
            yaml_data['requestBody']['contentType'] = content_type
            schema = content_info.get('schema', {})
            if schema.get('properties'):
                yaml_data['requestBody']['properties'] = {}
                for prop_name, prop_info in schema['properties'].items():
                    yaml_data['requestBody']['properties'][prop_name] = {
                        'type': prop_info.get('type', 'object'),
                        'description': prop_info.get('description', '')
                    }
    
    # 응답 정보
    if operation.get('responses'):
        yaml_data['responses'] = {}
        for status_code, response in operation['responses'].items():
            yaml_data['responses'][status_code] = {
                'description': response.get('description', '')
            }
    
    return yaml_data

def save_dsl_files(dsl: Dict[str, Any], output_dir: str):
    """DSL 파일들을 저장"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 메인 DSL YAML 파일
    with open(output_path / 'openapi_dsl.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(dsl, f, indent=2, allow_unicode=True, sort_keys=False)
    
    # 개별 작업별 YAML 파일들
    operations_dir = output_path / 'operations'
    operations_dir.mkdir(exist_ok=True)
    
    for operation in dsl['operations']:
        if operation['operationId']:
            operation_yaml = create_operation_yaml(operation)
            filename = f"{operation['operationId']}.yaml"
            with open(operations_dir / filename, 'w', encoding='utf-8') as f:
                yaml.dump(operation_yaml, f, indent=2, allow_unicode=True, sort_keys=False)
    
    # 태그별 요약 파일
    tags_dir = output_path / 'tags'
    tags_dir.mkdir(exist_ok=True)
    
    for tag_name, tag_info in dsl['tags'].items():
        tag_content = {
            'name': tag_name,
            'description': tag_info['description'],
            'operations': tag_info['operations']
        }
        
        with open(tags_dir / f"{tag_name}.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(tag_content, f, indent=2, allow_unicode=True, sort_keys=False)

def main():
    """메인 함수"""
    # 입력 파일 경로
    openapi_spec_path = "data/openapi/unstable/scenario.yaml"
    dsl_output_dir = "generated_dsl/openapi_dsl"
    
    print(f"OpenAPI 명세 로드 중: {openapi_spec_path}")
    
    # OpenAPI 명세 로드
    openapi_spec = load_openapi_spec(openapi_spec_path)
    
    print(f"발견된 경로: {len(openapi_spec.get('paths', {}))}개")
    
    # DSL 생성
    print("DSL 생성 중...")
    dsl = generate_dsl_from_openapi(openapi_spec)
    
    print(f"생성된 작업: {len(dsl['operations'])}개")
    print(f"생성된 태그: {len(dsl['tags'])}개")
    
    # DSL 파일 저장
    print(f"DSL 파일 저장 중: {dsl_output_dir}")
    save_dsl_files(dsl, dsl_output_dir)
    
    print("✅ OpenAPI DSL 생성 완료!")
    print(f"생성된 작업 DSL 파일: {len(dsl['operations'])}개")

if __name__ == "__main__":
    main() 