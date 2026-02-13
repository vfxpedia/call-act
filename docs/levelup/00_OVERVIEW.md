# CALL:ACT 고도화 작업 개요

> **마지막 업데이트**: 2026-02-10

---

## 원칙

1. **본질**: 하나의 DB 문서가 모든 화면에서 일관되고 올바르게 보여야 한다
2. **단계적**: 하나씩 문제를 해결하되, 근본적인 방향을 잃지 않는다
3. **검증**: 매 단계마다 현재 상태 기록, 변경 결과 비교, 회귀 테스트 실행
4. **롤백 가능**: 원본 백업 후 작업, 언제든 이전 상태로 복원 가능
5. **공유**: 세 세션(DB/Backend/Frontend) 간 작업 내용 항시 공유

---

## 작업 현황

| # | DB (D) | Backend (B) | Frontend (F) | 협업 논의 | 상태 |
|---|--------|-------------|-------------|----------|------|
| 01 | [문서 정체성 + 키워드](01_D_document_identity_and_keywords.md) | [RAG 타입 연동](01_B_rag_pipeline_document_type.md) | [타입 표시 통일](01_F_document_type_display.md) | [3팀 논의](01_DISCUSSION.md) | **Phase A-C 완료** |
| 02 | fullText 전처리, Mock 피드백 | [메모] 프롬프트, 참조문서 조사 | UI/UX 6건 완료, 포커싱, 정렬 | [Level02 논의](02_LEVEL02_DISCUSSION.md) | **Phase 1 완료, Phase 2 대기** |

---

## 진행 흐름

```
Phase A: 각 팀 자체 작업 (병렬)
  [DB]       document_type 분류 + 키워드 추출 + FAQ 매핑
  [Backend]  RAG_MATCH_CARD_NAMES=1 + weak_intent 확장
  [Frontend] 변환 유틸리티 중앙화 + graceful UI

Phase B: 합의 사항 결정
  결정 1: 문서 ID 방침 (현 ID 유지 + sourceTable)
  결정 2: referenced_documents 스키마 확장
  결정 3: FAQ API snake_case 수정

Phase C: 연동 작업
  [Backend]  RAG sourceTable + API 확장
  [Frontend] documentType/sourceTable 적용
  [전체]     통합 테스트 + 회귀 테스트

[02_*] 다음 단계 (검색 품질 심화, 랭킹 튜닝 등)
```

---

## 핵심 진단 (2026-02-10 기준)

### 데이터 문제 (DB)
| 문제 | 영향도 | 해결 |
|------|--------|------|
| 카드 상품 49% 키워드 없음 | CRITICAL | 01_D Step 2 |
| 문서 타입 DB에 의미있는 값 없음 | CRITICAL | 01_D Step 1 |
| FAQ 문서 연결이 mock ID | HIGH | 01_D Step 3 |
| 가이드-상품 키워드 교집합 17개뿐 | HIGH | 01_D Step 2 |

### 파이프라인 문제 (Backend)
| 문제 | 영향도 | 해결 |
|------|--------|------|
| RAG vocab match 25-35% 차단 | HIGH | 01_B 환경변수 |
| K-패스 과도한 억제 | MEDIUM | 01_B 규칙 완화 |

### 표시 문제 (Frontend)
| 문제 | 영향도 | 해결 |
|------|--------|------|
| 문서 ID 체계 단절 | CRITICAL | 3팀 합의 |
| DocumentType 추론 취약 | HIGH | DB 값 우선 |
| fullText 빈 모달 | MEDIUM | graceful UI |

---

## 참조 문서

- [전체 데이터 분석 보고서](../DB_DATA_ANALYSIS_v1.md)
- [프론트엔드 현상 분석](00_F_현상분석_문서시스템.md)
- 회귀 테스트: `backend_dev/app/rag/resources/regression_tests.json`
- DB 스키마: `backend_dev/app/db/scripts/db_setup.sql`
