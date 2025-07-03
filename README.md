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
python -m venv .venv
source .venv/bin/activate
```

4. pip-tools 설치 및 의존성 설치

#### 운영 환경

```bash
make install
```

#### 개발/테스트 환경

```bash
make dev-install
```

5. 의존성 업데이트

```bash
make update
```

- `requirements.in`, `dev-requirements.in`에서 직접 의존성을 관리하세요.
- `requirements.txt`, `dev-requirements.txt`는 자동 생성됩니다.
- `setup.py`의 install_requires는 requirements.in을 자동 반영합니다.

6. 주요 파일 설명

- `requirements.in`: 운영(프로덕션) 의존성
- `dev-requirements.in`: 개발/테스트용 추가 의존성
- `requirements.txt`, `dev-requirements.txt`: pip-compile로 자동 생성(고정 버전)
- `Makefile`: 설치/업데이트 자동화 명령어
- `setup.py`: 패키지화 및 install_requires 자동 연동

7. 참고

- 의존성 추가/변경 시 반드시 `make update`로 txt 파일을 갱신하세요.
- 가상환경을 항상 활성화한 상태에서 작업하세요.
- pip-tools 미설치 시 `pip install pip-tools`로 직접 설치 가능

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
