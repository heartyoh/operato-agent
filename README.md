# Operato Agent

Operato Agent는 GraphQL API를 위한 RAG(Retrieval-Augmented Generation) 기반의 쿼리 생성 도구입니다.

## 요구사항

- Python 3.10 이상
- uv (Python 패키지 관리자)

## 설치 방법

1. uv 설치 (이미 설치되어 있지 않은 경우):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 프로젝트 클론:

```bash
git clone https://github.com/your-username/operato-agent.git
cd operato-agent
```

3. 가상환경 생성 및 활성화:

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# 또는
.venv\Scripts\activate  # Windows
```

4. 의존성 설치:

```bash
uv pip install -r requirements.txt
```

## 환경 설정

1. `.env` 파일 생성:

```bash
cp .env.example .env
```

2. `.env` 파일에 필요한 환경 변수 설정:

```
OPENAI_API_KEY=your_openai_api_key
```

## DSL 생성

GraphQL 스키마에서 DSL을 생성합니다:

```bash
python dsl_registry/gql_schema_to_dsl.py
```

이 명령은 `schema.graphql` 파일을 기반으로 `generated_dsl` 디렉토리에 DSL 정의 파일들을 생성합니다.

## RAG 인덱스 빌드

GraphQL 스키마를 기반으로 RAG 인덱스를 빌드합니다:

```bash
rm -rf rag_data/  # 또는 chroma_db/ 등 실제 인덱스 폴더명
python -m rag.index_builder
```

## 테스트 실행

전체 테스트 실행:

```bash
PYTHONPATH=. python -m pytest
```

특정 테스트 파일 실행:

```bash
PYTHONPATH=. python -m pytest tests/test_rag_user.py -v
```

## 주요 기능

1. GraphQL 스키마 분석
2. DSL(Domain Specific Language) 생성
3. RAG 기반 쿼리 생성
4. 자연어 질의를 GraphQL 쿼리로 변환

## 프로젝트 구조

```
operato-agent/
├── config/             # 설정 파일
├── graphql/           # GraphQL 관련 코드
├── llm/              # LLM 관련 코드
├── rag/              # RAG 관련 코드
├── tests/            # 테스트 코드
├── .env              # 환경 변수
├── requirements.txt  # 의존성 목록
└── README.md         # 프로젝트 문서
```

## 라이선스

MIT License
