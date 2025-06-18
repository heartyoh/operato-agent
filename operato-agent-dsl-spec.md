# 📘 Operato Agent DSL 스키마 설명 (YAML 기반)

Operato Agent는 GraphQL 쿼리 생성을 위한 도메인 특화 언어(DSL)를 `.yml` 파일로 정의하고 사용합니다. 이 문서는 각 DSL 항목의 구조를 YAML 형식으로 정리하여 설명합니다.

---

## ✅ DSL YAML 구조 개요

```yaml
# dsl_registry/query_appliances_with_filters.yml

dsl_name: query_appliances_with_filters # DSL의 고유 식별자 (파일명과 일치)
type: query # GraphQL 오퍼레이션 타입: query | mutation
description: 에어컨 장비 목록을 필터로 조회한다
query_template: |
  query ($filters: [Filter!], $pagination: Pagination) {
    appliances(filters: $filters, pagination: $pagination) {
      id
      name
      model
    }
  }
variables:
  - filters
  - pagination
related_types:
  - Appliance
  - Filter
  - Pagination
return_type: ApplianceList # 최종 반환 타입
```

---

## 🧩 필드 설명

| 필드명           | 타입           | 설명                                                  |
| ---------------- | -------------- | ----------------------------------------------------- |
| `dsl_name`       | `string`       | DSL 고유 이름, 파일명과 동일해야 함                   |
| `type`           | `string`       | GraphQL 연산 타입 (`query` 또는 `mutation`)           |
| `description`    | `string`       | DSL 설명 (자연어 프롬프트 힌트 역할)                  |
| `query_template` | `string`       | 실제 GraphQL 쿼리 형태, 변수는 `$변수명`으로 표기     |
| `variables`      | `list<string>` | 사용하는 변수 이름 목록                               |
| `related_types`  | `list<string>` | 관련된 GraphQL 타입 목록 (Schema 내 사용된 타입 포함) |
| `return_type`    | `string`       | 응답으로 반환되는 최종 GraphQL 타입                   |

---

## 🛠️ 예시 DSL 목록

- `query_appliances_with_filters.yml`
- `mutation_update_equipment_status.yml`
- `query_events_by_range.yml`

---

## 📁 저장 위치

모든 DSL 파일은 다음 경로에 저장됩니다:

```
dsl_registry/
├── query_appliances_with_filters.yml
├── mutation_update_equipment_status.yml
└── ...
```

---

## 🔄 사용 흐름 요약

1. GraphQL 스키마를 기반으로 DSL `.yml` 파일 자동 생성 (`gql_schema_to_dsl.py`)
2. Chroma 인덱싱 (`index_builder.py`)을 통해 검색 가능하게 구성
3. 자연어 입력 → DSL 검색 → 관련 타입과 템플릿을 LLM에 전달하여 쿼리 생성
