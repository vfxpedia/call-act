# M-2 단계3: 상담 흐름 인식 (Flow Prediction)

## 개요

상담 중 고객이 다음에 물어볼 가능성이 높은 주제를 실시간 예측하여, "다음 단계" 패널에 미리 관련 문서를 표시합니다.

**근거 데이터**: 6,533건 하나카드 상담 → 488건(7.5%) 다중 카테고리 통화 → 83개 전이 패턴

## 핵심 전이 패턴 (상위 10)

| 현재 카테고리 | 다음 예측 | 빈도 |
|---|---|---|
| 이용내역 안내 | 포인트/마일리지 안내 | 41 |
| 이용내역 안내 | 결제대금 안내 | 38 |
| 선결제/즉시출금 | 한도 안내 | 26 |
| 선결제/즉시출금 | 이용내역 안내 | 20 |
| 분실/도난 신청/해제 | 긴급 배송 신청 | 16 |
| 선결제/즉시출금 | 결제일 안내/변경/취소 | 16 |
| 한도상향 접수/처리 | 결제대금 안내 | 15 |
| 정부지원 바우처 | 이용방법 안내 | 14 |
| 승인취소/매출취소 안내 | 결제일 안내/변경/취소 | 14 |
| 이용방법 안내 | 서비스 이용방법 안내 | 10 |

## 아키텍처

```
[WebSocket/API]
  → run_rag(query, session_state={})
    → run_search()
      → route_query()  // actions, weak_intents 추출
      → retrieve_docs()  // 기존 벡터+역색인 검색
      → update_flow(session_state, routing)  // 카테고리 감지 + 세션 갱신
      → predict_next_docs(session_state, top_k=2)  // 전이 확률 기반 예측
    → pipeline.py
      → build_card_response()  // currentSituation + nextStep (검색 결과)
      → flow_docs → build_rule_cards()  // 예측 문서 → 카드 변환
      → nextStep += flow_cards  // 검색 nextStep에 예측 카드 추가
```

## 파일 구조

| 파일 | 역할 |
|---|---|
| `backend/app/rag/flow/flow_model.py` | 전이 모델 데이터 + 카테고리 감지 + 예측 함수 |
| `backend/app/rag/flow/flow_tracker.py` | 세션 추적 + 문서 예측 + 키워드 인덱스/벡터 검색 |
| `backend/app/rag/pipeline/search.py` | 통합점: `FLOW_PREDICTION_ENABLED`, `SearchResult.flow_docs` |
| `backend/app/rag/pipeline/pipeline.py` | 통합점: flow_docs → nextStep 병합 |

## 환경 변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `RAG_FLOW_PREDICTION` | `1` | `0`으로 비활성화 |

## 프론트엔드 연동

예측 카드에는 아래 필드가 추가됨 (프론트엔드에서 UI 차별화에 활용 가능):

```json
{
  "_from_flow_prediction": true,
  "_predicted_category": "긴급 배송 신청"
}
```

## 테스트 결과

- 단위 테스트 (flow_model.py): 18/18 통과
- 통합 테스트 (run_rag): "카드 분실 신고" → nextStep에 예측 2건 병합 확인
  - [SEARCH] 해외여행 시 IC카드 이용 팁
  - [PRED] 배송 조회 (→긴급 배송 신청)
  - [PRED] 카드 추가 및 삭제 안내 (→카드재발급)

## 한계 및 개선 방향

1. **키워드 인덱스 문서 품질**: 일부 카테고리에서 범용 문서 매칭됨 → M-3에서 relevance 필터 강화
2. **전이 데이터 커버리지**: 18개 출발 카테고리만 전이 데이터 보유 → 데이터 축적 시 확장
3. **프론트엔드 UI**: 예측 카드 시각적 차별화 필요 (배지, 색상 등) → Frontend 세션 작업
