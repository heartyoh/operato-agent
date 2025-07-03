# 번역 품질 향상 및 도메인 용어 일관성 확보 실전 가이드

---

## 1. 전체 번역 파이프라인 요약

### 1) 용어집(Glossary) 구축

- `/data/terminology/ko.json`, `en.json` 등 다국어 용어집 준비
- key 기준으로 다국어 Glossary 테이블(CSV/DB 등) 생성

### 2) 번역 파이프라인 설계

#### A. 전처리(Pre-processing)

- 입력 문장에서 도메인 용어(한글 등)를 특수 토큰(`__TERM_board__` 등) 또는 key로 치환
- (Aho-Corasick 등 고속 패턴 매칭 활용)

#### B. 번역(NMT/LLM)

- OpenNMT 등 NMT 엔진에 전처리된 문장 입력
- (또는 Google/DeepL API + Glossary 기능 활용)

#### C. 후처리(Post-processing)

- 번역 결과에서 특수 토큰을 목표 언어의 용어집에 따라 복원
- (문맥/복수형/관사 등은 품사 분석, LLM, 구문 단위 Glossary로 보정)

### 3) 품질 검증/QA

- 실제 유저 질문/문장으로 번역 품질, 용어 일관성, 자연스러움 테스트
- Glossary/파이프라인/모델 반복 개선

---

## 2. 실전 적용 전략

- **Glossary만으로는 한계**
  - 전처리/후처리, 문맥 보정, QA 등 추가 작업 필요
- **대규모 Glossary**
  - Aho-Corasick 등 고속 매칭, 긴 용어 우선, 형태소 분석 등 적용
- **최고 품질 원할 때**
  - LLM/AI 기반 후처리, 구문 단위 Glossary, 상용 번역 API 병행 고려
- **OpenNMT 등 오픈소스 NMT**
  - 전처리/후처리 파이프라인 직접 구현 필요

---

## 3. 솔루션 선택 가이드

- **온프레미스/커스텀**: OpenNMT + 직접 Glossary/파이프라인
- **자동화/최고 품질**: Google/DeepL API + Glossary 기능
- **엔터프라이즈 통합**: SYSTRAN, KantanMT, memoQ 등 상용 TMS

---

## 4. 핵심 요약

1. **Glossary 구축**
2. **전처리(치환)**
3. **NMT/LLM 번역**
4. **후처리(복원/문맥 보정)**
5. **QA/반복 개선**

---

### 추가 안내

- 구체적 코드, 자동화, 품질 관리, 솔루션 도입 등 실행 단계별로 추가 안내가 필요하면 언제든 요청해 주세요!
