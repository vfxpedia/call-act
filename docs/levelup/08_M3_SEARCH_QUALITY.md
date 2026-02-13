# M-3: RAG 검색 품질 종합 개선

## 문제 진단

17개 쿼리 유형에 대한 종합 진단 결과, 5가지 핵심 이슈 발견:

### 1. Score 인플레이션 (Critical)
- **원인**: `keyword_doc_index.py`의 `IndexEntry.relevance`는 "키워드 소스 가중치"(keywords배열=1.0, 제목=0.7, intent=0.5)이지, **쿼리 관련도가 아님**
- **경로**: `search.py:140` `doc["score"] = idx_entry.relevance` → `card_generator.py:118` `relevanceScore = round(score * 100)`
- **결과**: 무관한 문서가 `relevanceScore=100`으로 표시

### 2. 범용 문서 오염
- "Gift 카드 안내", "카드상품별 거래조건" 등이 다수 키워드를 포함하여 모든 쿼리에서 매칭
- "한도 조회" → "Gift 카드 안내"(score=100) — 완전히 무관

### 3. 병합 순서 문제
- `_merge_index_and_vector_docs()`가 키워드 인덱스 문서를 무조건 우선 배치
- 더 좋은 벡터 검색 결과가 밀려남

### 4. 저품질 문서 미필터링
- score < 0.08인 문서도 카드로 변환되어 UI에 표시

---

## 수정 내역

### Fix-1: Score 정규화 (`search.py:144`)

```python
# Before:
doc["score"] = idx_entry.relevance  # 0.5~1.0 (소스 가중치)

# After:
doc["score"] = idx_entry.relevance * 0.45  # max 0.45 (벡터 검색 스케일)
```

**효과**: 키워드 인덱스 문서 최대 score = 0.45 (relevanceScore=45). 좋은 벡터 결과(0.5+)가 우선.

### Fix-2: Score 기반 병합 (`search.py:158-175`)

```python
# Before: 키워드 인덱스 우선
for doc in index_docs: ...  # 역색인 먼저
for doc in vector_docs: ...  # 벡터 나중

# After: score 순 통합
for doc in index_docs + vector_docs: ...
merged.sort(key=lambda d: d.get("score", 0.0), reverse=True)
```

### Fix-3: 최소 Relevance 임계값 (`search.py:354-356`)

```python
MIN_RELEVANCE_THRESHOLD = 0.08  # RAG_MIN_RELEVANCE 환경변수로 조정 가능

if docs and MIN_RELEVANCE_THRESHOLD > 0:
    above = [d for d in docs if d.get("score", 0.0) >= MIN_RELEVANCE_THRESHOLD]
    docs = above if above else docs[:1]  # 최소 1개 유지
```

### Fix-4: 제목-쿼리 관련성 감쇠 (`search.py:328-336`)

```python
# 쿼리 핵심 토큰 중 하나도 제목에 없는 키워드 인덱스 문서 → score * 0.15
# 범용 토큰("카드", "안내", "체크" 등) 제외
_TITLE_CHECK_STOPWORDS = {"카드", "안내", "체크", "신용", ...}

if _q_tokens and not any(t in title_lower for t in _q_tokens):
    doc["score"] *= 0.15  # 0.45 * 0.15 = 0.068 < MIN_RELEVANCE(0.08) → 자동 필터
```

**효과**: "한도 조회" → "Gift 카드"(score=0.068) → MIN_RELEVANCE 이하 → 제거됨

---

## 검증 결과

### M-3 전용 테스트 (11/11 통과)

| 쿼리 | Fix 전 | Fix 후 |
|------|--------|--------|
| 한도 조회 | Gift카드(score=100) 1위 | 배송조회(43), 이용한도(41) |
| 결제일 변경 | Gift카드(score=100) 1위 | 최소결제비율변경(49), 변경승인(48) |
| 나라사랑카드 분실 | Gift카드(score=100) 혼입 | 분실FAQ(56), 나라사랑카드(29) |
| 한도 좀 올려주세요 | Gift카드(score=100) 1위 | 한도약정(28), 해외이용(28) |
| 포인트 조회 | — | 포인트활용방법(59), 적립제외(56) |
| 연회비 얼마예요 | — | 연회비(66), 연회비안내(63) |

### 기존 케이스 회귀 (7개 핵심 케이스)

- 5/7 통과 (실패 2건은 라우팅 이슈, M-3 스코프 밖)
- 나라사랑 분실: 정확한 FAQ 매칭 유지 ✅
- K-패스 교통카드 혜택: 관련 K패스 FAQ 매칭 ✅
- 결제일 알려줘: 자동이체결제 약관 매칭 ✅

---

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `RAG_MIN_RELEVANCE` | `0.08` | 최소 relevance 임계값 (이하 필터링) |
| `RAG_KEYWORD_INDEX` | `1` | 키워드 역색인 활성화 |

---

## Score 체계 정리

| 소스 | 원본 범위 | 정규화 후 | 제목 미스매치 후 |
|------|-----------|-----------|----------------|
| 벡터 검색 | 0.2 ~ 0.6 | 0.2 ~ 0.6 (변경 없음) | N/A |
| 키워드(keywords 배열) | 1.0 | 0.45 | 0.068 |
| 키워드(제목 토큰) | 0.7 | 0.315 | 0.047 |
| 키워드(intent) | 0.5 | 0.225 | 0.034 |
| 흐름 예측 | 0.35 | 0.35 (변경 없음) | N/A |

→ 제목 미스매치 시 모든 키워드 인덱스 문서가 MIN_RELEVANCE(0.08) 이하로 자동 필터

---

## 수정 파일

| 파일 | 변경 |
|------|------|
| `backend/app/rag/pipeline/search.py` | Fix-1~4 전체 |
| `backend/tests/test_m3_search_quality.py` | M-3 전용 회귀 테스트 (11케이스) |

---

## 알려진 한계

1. **"리볼빙 해지"**: 벡터 검색에서 관련 문서 매칭이 약함 (콘텐츠 갭). 데이터 보강 필요.
2. **라우팅 정확도**: "테디카드 SOL트래블 수수료" → card_usage(오답). 라우팅 로직 별도 개선 필요.
3. **벡터 검색 기본 품질**: 임베딩 모델 한계로 한국어 세부 의미 구분 약함.
