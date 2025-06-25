#!/usr/bin/env python3
"""
DSL Description 개선 스크립트 v2
더 구체적이고 정확한 한글 키워드와 설명을 추가하여 RAG 검색 정확도를 향상시킵니다.
"""

import os
import yaml

def improve_dsl_descriptions_v2():
    """DSL 파일들의 description을 더 구체적으로 개선"""
    
    # 개선할 DSL 매핑 (더 구체적이고 정확한 설명)
    improvements = {
        "query_boards.yaml": {
            "description": "보드 목록 조회 - 모든 보드의 목록을 페이지네이션으로 조회합니다 (boards list, multiple boards, 모든 보드, 보드 리스트, 보드 목록)",
            "keywords": ["목록", "리스트", "모든", "multiple", "list", "boards", "보드목록", "보드리스트"]
        },
        "query_board.yaml": {
            "description": "단일 보드 조회 - ID로 특정 보드 하나를 조회합니다 (single board, 특정 보드, 보드 상세, board detail, 보드 정보)",
            "keywords": ["단일", "특정", "상세", "single", "detail", "board", "보드정보", "보드상세"]
        },
        "query_boardTemplates.yaml": {
            "description": "보드 템플릿 목록 조회 - 모든 보드 템플릿의 목록을 조회합니다 (board templates list, 템플릿 목록, 모든 템플릿, 템플릿 리스트)",
            "keywords": ["템플릿", "목록", "templates", "list", "multiple", "보드템플릿", "템플릿목록"]
        },
        "query_boardTemplate.yaml": {
            "description": "단일 보드 템플릿 조회 - ID로 특정 보드 템플릿 하나를 조회합니다 (single board template, 템플릿 상세, template detail, 템플릿 정보)",
            "keywords": ["템플릿", "단일", "상세", "template", "single", "detail", "템플릿정보", "템플릿상세"]
        },
        "query_boardPublished.yaml": {
            "description": "발행된 보드 조회 - ID로 특정 보드의 최신 발행 버전을 조회합니다 (published board, 공개된 보드, 발행 보드, 보드 발행 버전)",
            "keywords": ["발행", "공개", "published", "public", "버전", "version", "발행보드", "공개보드"]
        },
        "query_boardsCreatedByMe.yaml": {
            "description": "내가 만든 보드 목록 - 현재 사용자가 생성한 보드들의 목록을 조회합니다 (boards created by me, 내 보드, 내가 생성한 보드, 내가 만든 보드)",
            "keywords": ["내가", "만든", "생성", "created", "my", "boards", "내보드", "내가만든", "내가생성한"]
        },
        "query_boardTemplatesCreatedByMe.yaml": {
            "description": "내가 만든 보드 템플릿 목록 - 현재 사용자가 생성한 보드 템플릿들의 목록을 조회합니다 (board templates created by me, 내 템플릿, 내가 만든 템플릿)",
            "keywords": ["내가", "만든", "템플릿", "created", "my", "templates", "내템플릿", "내가만든템플릿"]
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
            print(f"     새 설명: {improvement['description'][:50]}...")
        else:
            print(f"  ❌ {filename} 파일 없음")

if __name__ == "__main__":
    improve_dsl_descriptions_v2()
    print("\n🎉 DSL Description 개선 완료!")
    print("다음 단계: RAG 인덱스 재빌드") 