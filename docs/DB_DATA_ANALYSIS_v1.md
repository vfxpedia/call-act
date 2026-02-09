# CALL:ACT 데이터/검색 품질 분석 보고서 v1.0

> **작성**: DB/데이터 사이언티스트 담당
> **날짜**: 2026-02-09
> **대상**: Frontend, Backend, DB 전체 팀
> **목적**: 검색 품질 저하 근본 원인 분석 및 고도화 로드맵

---

## 1. 현황 요약

| 데이터셋 | 건수 | 임베딩 | 키워드 채움률 |
|----------|------|--------|-------------|
| 카드 상품 (card_products) | 398 | 100% | **51%** (203/398) |
| 서비스 가이드 (service_guide_documents) | 1,273 | 100% | 100% |
| 공지사항 (notices) | 52 | 100% | 100% |
| 상담 이력 (consultation_documents) | 6,533 | 100% | 100% |
| 키워드 사전 (keyword_dictionary) | 1,157 | N/A | N/A |
| 고객 (customers) | 2,500 | N/A | N/A |
| 상담사 (employees) | 70 | N/A | N/A |

---

## 2. 핵심 문제점 (Root Causes)

### RC-1: 카드 상품 49%가 키워드 없음 (CRITICAL)

```
전체 카드 상품: 398건
키워드 있음:    203건 (51%)
키워드 없음:    195건 (49%)  ← 키워드 검색에 완전히 보이지 않음
```

**영향**: "할부 되는 카드 뭐 있어?" → 카드 상품에서 0건 반환
**원인**: 전처리 시 keywords 추출 로직이 일부 상품에만 적용됨
**예시**: `#Pay 테디카드`, `AK PLAZA 테디카드 Plus` 등 195건의 상품이 풍부한 `structured` 데이터(mainBenefits, benefitDetails, detailContent)를 갖고 있지만 keywords 배열이 비어있음

### RC-2: 키워드 사전-실데이터 불일치 (CRITICAL)

| 지표 | 수치 |
|------|------|
| 사전 키워드 수 | 1,157개 |
| 실제 사용되는 키워드 | 218개 (**17.4%**) |
| 사전에 없는데 데이터에 있는 키워드 | 1,567개 |
| 사전에 있는데 데이터에 없는 키워드 | 939개 (81.2%) |

**결론**: 키워드 사전이 실제 데이터와 **완전히 동기화되지 않음**. 사전은 설명용이지, 실제 태깅 가이드가 아님.

### RC-3: 가이드-상품 간 키워드 단절 (CRITICAL)

| 소스 | 고유 키워드 수 |
|------|-------------|
| 서비스 가이드에만 있는 키워드 | 1,740개 |
| 카드 상품에만 있는 키워드 | 28개 |
| **양쪽 모두에 있는 키워드** | **17개** |

**영향**: 가이드에서 "결제"를 검색하면 290건이 나오지만, 카드 상품에서는 **0건**

| 핵심 토픽 | 가이드 문서 수 | 카드 상품 수 | 갭 |
|-----------|-------------|-----------|-----|
| 결제 | 290 | **0** | CRITICAL |
| 가맹점 | 156 | **0** | CRITICAL |
| 대출 | 140 | **0** | CRITICAL |
| 할부 | 78 | **0** | CRITICAL |
| 해지 | 176 | **0** | CRITICAL |

### RC-4: RAG 파이프라인 과도한 필터링 (HIGH)

```
RAG_REQUIRE_VOCAB_MATCH=1 (기본값 ON)
→ 전체 사용자 쿼리의 약 25-35%가 검색 전에 차단됨
```

**차단되는 쿼리 유형**:

| 유형 | 예시 | 차단률 |
|------|------|--------|
| 일반 질문 | "이 카드 좋나요?", "뭐가 좋아?" | 60-80% |
| 카드명만 언급 | "XX카드 뭐야?" | 80-100% |
| 구어체/짧은 쿼리 | "뭐?", "응?" | 100% |
| 간접적 의도 | "비밀번호 까먹었어요" | 40-60% |
| 표준 액션 쿼리 | "발급해주세요", "분실했어요" | 10-20% |

**원인**:
- `RAG_MATCH_CARD_NAMES=0` (기본값) → 카드명만으로는 vocab match 안됨
- 약한 의도(weak intent) 5개만 정의: 혜택, 발급, 신청, 사용, 사용처
- 퍼지 매칭 최소 길이 3자 → 짧은 쿼리 차단

### RC-5: 과도한 문서 억제 규칙 (MEDIUM)

- 분실/도난 쿼리 시 **모든 K-패스 문서** 제거 → K-패스 분실 정보도 같이 삭제됨
- Apple Pay 문서도 분실/대출 쿼리에서 일괄 제거
- "발급" 라우팅 모호성: card_info vs card_usage 경계 불명확

---

## 3. 데이터 구조 상세 분석

### 3.1 카드 상품 structured 필드 (미활용 자원)

키워드가 없는 195건의 상품도 `structured` 필드에 풍부한 정보를 갖고 있음:

```json
{
  "structured": {
    "cardName": "#Pay 테디카드",
    "mainBenefits": ["고객센터", "단기/장기 카드대출", "MF대출서비스"],
    "benefitDetails": {
      "pointAccrual": "...",
      "conditions": "...",
      "limit": "..."
    },
    "performanceConditions": "전월 실적 30만원 이상",
    "usageGuide": "...",
    "detailContent": "금융소비자는 신용카드 발급이...",
    "fullTerms": "..."
  }
}
```

**이 데이터를 활용하면 자동으로 키워드 추출이 가능**

### 3.2 서비스 가이드 소스 분포

| source 타입 | 설명 | 용도 |
|------------|------|------|
| merged | 여러 하위 문서 통합 | 종합 안내 |
| general | 일반 안내 문서 | 기본 검색 |
| terms | 약관/규정 문서 | 심층 검색 |

일부 가이드는 10개 이상 하위 문서가 병합됨 → 검색 특이성 저하 가능성

### 3.3 벡터 인덱스 설정

| 테이블 | 차원 | 인덱스 | 파라미터 |
|--------|------|--------|---------|
| consultation_documents | 1536 | HNSW | m=16, ef_construction=64 |
| service_guide_documents | 1536 | HNSW | m=16, ef_construction=64 |
| card_products | 1536 | HNSW | m=16, ef_construction=64 |
| notices | 1536 | HNSW | m=16, ef_construction=64 |

모델: OpenAI `text-embedding-3-small` (1536차원)

---

## 4. RAG 파이프라인 흐름 및 병목 지점

```
사용자 쿼리
    │
    ▼
[GATE 1] has_vocab_match() ─── 25-35% 차단 ──→ "검색 불가" 반환
    │ (통과)
    ▼
[ROUTING] 신호 추출 (카드명/액션/결제수단/패턴)
    │
    ▼
[GATE 2] search_gating() ─── 짧은 쿼리/인사말 차단
    │ (통과)
    ▼
[RETRIEVAL] 벡터 + 텍스트 검색
    │  ├─ 벡터: embedding <=> 코사인 거리
    │  ├─ 텍스트: trigram + ILIKE
    │  └─ 카드명: 정규화 매칭
    │
    ▼
[RANKING] RRF + 다중 부스팅/페널티
    │  ├─ 카드 매칭: +0.35
    │  ├─ 의도 매칭: +0.20
    │  ├─ 분실 보너스: +0.35
    │  └─ K-패스 페널티: -0.25
    │
    ▼
[FILTER] 후처리 필터링
    │  ├─ K-패스 억제 (분실/대출 쿼리)
    │  ├─ Apple Pay 억제 (분실/대출 쿼리)
    │  └─ 중복 제거
    │
    ▼
검색 결과 반환
```

**병목 지점**: GATE 1 (vocab match)과 FILTER (과도한 억제)

---

## 5. 고도화 액션 플랜

### Phase 1: 데이터 품질 개선 (즉시 ~ 1주)

| # | 작업 | 담당 | 영향도 | 난이도 |
|---|------|------|--------|--------|
| D-1 | **카드 상품 195건 키워드 자동 추출** | DB | CRITICAL | 중 |
| | structured.mainBenefits + detailContent에서 키워드 추출 | | | |
| D-2 | **키워드 사전 동기화** | DB | HIGH | 중 |
| | 실데이터 기반으로 사전 재구축 (939개 미사용 제거, 1,567개 누락 추가) | | | |
| D-3 | **가이드-상품 키워드 정렬** | DB | HIGH | 상 |
| | 핵심 토픽(결제, 할부, 대출, 해지) 카드 상품에도 태깅 | | | |
| D-4 | **키워드 태깅 규칙 문서화** | DB | MEDIUM | 하 |
| | 어떤 기준으로 키워드를 부여하는지 명확한 가이드 작성 | | | |

### Phase 2: 검색 파이프라인 튜닝 (1~2주)

| # | 작업 | 담당 | 영향도 | 난이도 |
|---|------|------|--------|--------|
| P-1 | **RAG_MATCH_CARD_NAMES=1 활성화** | Backend | HIGH | 하 |
| | 카드명만으로도 vocab match 통과 | | | |
| P-2 | **weak_intent 확장** | Backend | HIGH | 하 |
| | 조회, 비교, 환불, 문의, 정보, 한도 추가 | | | |
| P-3 | **K-패스 억제 규칙 완화** | Backend | MEDIUM | 중 |
| | 분실 쿼리에서도 K-패스 분실 관련 문서는 유지 | | | |
| P-4 | **퍼지 매칭 임계값 조정** | Backend | MEDIUM | 하 |
| | RAG_ROUTER_FUZZY_THRESHOLD: 85→75 | | | |
| P-5 | **RAG_REQUIRE_VOCAB_MATCH 장기적 비활성화 검토** | Backend/DB | HIGH | 상 |
| | soft gating (domain_score) + 개선된 ranking으로 대체 | | | |

### Phase 3: 구조적 개선 (2~4주)

| # | 작업 | 담당 | 영향도 | 난이도 |
|---|------|------|--------|--------|
| S-1 | **자동 키워드 추출 파이프라인** | DB | HIGH | 상 |
| | 새 데이터 적재 시 자동으로 키워드 생성 | | | |
| S-2 | **다단계 vocab matching** | Backend | HIGH | 상 |
| | Exact → Fuzzy → Semantic Intent Classification 순차 적용 | | | |
| S-3 | **가이드 문서 세분화** | DB | MEDIUM | 중 |
| | 10개 이상 병합 문서를 토픽별로 재분리 | | | |
| S-4 | **검색 품질 모니터링 대시보드** | Frontend | MEDIUM | 중 |
| | 검색 적중률, 빈 결과 비율, 라우팅 분포 시각화 | | | |

---

## 6. 검증 방법

### 회귀 테스트 (기존 40건)
- 기본 12건: `backend_dev/app/rag/resources/regression_tests.json`
- 확장 40건: `backend_dev/app/rag/tests/test_suite.py`
- 실행: `python backend_dev/app/rag/scripts/run_regression.py`

### 신규 검증 기준 (추가 필요)
1. **키워드 커버리지**: 전체 상품의 키워드 채움률 → 목표 95%+
2. **사전-데이터 일치율**: 사전 키워드 중 실데이터에 존재하는 비율 → 목표 80%+
3. **교차 검색률**: 가이드 키워드로 카드 상품도 검색되는 비율 → 목표 50%+
4. **빈 결과 비율**: 전체 쿼리 중 결과 0건인 비율 → 목표 10% 이하

---

## 7. 파일 위치 참조

```
데이터:
  backend_dev/app/db/data/teddycard/keywords_dict_v2_with_patterns.json
  backend_dev/app/db/data/teddycard/teddycard_card_products_with_embeddings.json
  backend_dev/app/db/data/teddycard/teddycard_service_guides_with_embeddings.json
  backend_dev/app/db/data/teddycard/teddycard_notices_with_embeddings.json
  backend_dev/app/db/data/hana/hana_rdb_metadata.json
  backend_dev/app/db/data/hana/hana_vectordb_with_embeddings.json

RAG 파이프라인:
  backend_dev/app/rag/pipeline/pipeline.py      ← 메인 진입점
  backend_dev/app/rag/pipeline/search.py        ← 검색 오케스트레이션
  backend_dev/app/rag/router/signals.py         ← 신호 추출
  backend_dev/app/rag/router/rules.py           ← 라우팅 규칙
  backend_dev/app/rag/retriever/db.py           ← 벡터+텍스트 검색
  backend_dev/app/rag/retriever/rank.py         ← RRF 랭킹
  backend_dev/app/rag/retriever/terms.py        ← 검색 컨텍스트 빌드
  backend_dev/app/rag/retriever/config.py       ← 상수/설정
  backend_dev/app/rag/vocab/keyword_dict.py     ← 키워드 사전 로더
  backend_dev/app/rag/common/doc_source_filters.py ← 문서 소스 필터

DB 스크립트:
  backend_dev/app/db/scripts/01a_setup_callact_db.py  ← DB 셋업
  backend_dev/app/db/scripts/modules/load_keywords.py ← 키워드 적재
  backend_dev/app/db/scripts/modules/load_teddycard.py ← 테디카드 적재

테스트:
  backend_dev/app/rag/resources/regression_tests.json  ← 기본 테스트
  backend_dev/app/rag/tests/test_suite.py              ← 확장 테스트
  backend_dev/app/rag/scripts/run_regression.py        ← 테스트 실행
```

---

## 8. 다음 단계

1. **[DB 담당]** Phase 1 D-1 즉시 착수: 카드 상품 195건 키워드 자동 추출 스크립트 작성
2. **[Backend 담당]** Phase 2 P-1, P-2 즉시 착수: 환경변수 조정 + weak_intent 확장
3. **[Frontend 담당]** Phase 3 S-4 기획: 검색 품질 모니터링 UI 설계
4. **[전체]** 매 변경 후 회귀 테스트 실행 → 결과 공유

---

*이 문서는 고도화 진행에 따라 지속적으로 업데이트됩니다.*
