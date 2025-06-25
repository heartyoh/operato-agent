#!/usr/bin/env python3
"""
DSL Description 개선 스크립트
한글 키워드와 더 구체적인 설명을 추가하여 RAG 검색 정확도를 향상시킵니다.
"""

import os
import yaml
import glob

def improve_dsl_descriptions():
    """DSL 파일들의 description을 개선"""
    
    # 개선할 DSL 매핑
    improvements = {
        "query_boards.yaml": {
            "description": "보드 목록 조회 (boards list, multiple boards, 모든 보드, 보드 리스트)",
            "keywords": ["목록", "리스트", "모든", "multiple", "list", "boards"]
        },
        "query_board.yaml": {
            "description": "단일 보드 조회 (single board, 특정 보드, 보드 상세, board detail)",
            "keywords": ["단일", "특정", "상세", "single", "detail", "board"]
        },
        "query_boardTemplates.yaml": {
            "description": "보드 템플릿 목록 조회 (board templates list, 템플릿 목록, 모든 템플릿)",
            "keywords": ["템플릿", "목록", "templates", "list", "multiple"]
        },
        "query_boardTemplate.yaml": {
            "description": "단일 보드 템플릿 조회 (single board template, 템플릿 상세, template detail)",
            "keywords": ["템플릿", "단일", "상세", "template", "single", "detail"]
        },
        "query_boardPublished.yaml": {
            "description": "발행된 보드 목록 조회 (published boards, 공개된 보드, 발행 보드 목록)",
            "keywords": ["발행", "공개", "published", "public", "목록", "list"]
        },
        "query_boardsCreatedByMe.yaml": {
            "description": "내가 만든 보드 목록 (boards created by me, 내 보드, 내가 생성한 보드)",
            "keywords": ["내가", "만든", "생성", "created", "my", "boards"]
        },
        "query_boardTemplatesCreatedByMe.yaml": {
            "description": "내가 만든 보드 템플릿 목록 (board templates created by me, 내 템플릿)",
            "keywords": ["내가", "만든", "템플릿", "created", "my", "templates"]
        }
    }
    
    dsl_dir = "generated_dsl"
    
    for filename, improvement in improvements.items():
        filepath = os.path.join(dsl_dir, filename)
        
        if os.path.exists(filepath):
            print(f"개선 중: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                dsl_data = yaml.safe_load(f)
            
            # description 개선
            dsl_data['description'] = improvement['description']
            
            # keywords 필드 추가 (RAG 검색에 도움)
            dsl_data['keywords'] = improvement['keywords']
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(dsl_data, f, allow_unicode=True, sort_keys=False)
            
            print(f"  ✅ {filename} 개선 완료")
        else:
            print(f"  ❌ {filename} 파일 없음")

if __name__ == "__main__":
    improve_dsl_descriptions()
    print("\n🎉 DSL Description 개선 완료!")
    print("다음 단계: RAG 인덱스 재빌드") 