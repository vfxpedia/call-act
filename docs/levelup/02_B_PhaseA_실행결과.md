# 02_B: Phase A 실행 결과

> **담당**: Backend
> **날짜**: 2026-02-10
> **상태**: 완료

---

## 변경 파일 목록

| 파일 | 변경 | 내용 |
|------|------|------|
| `backend/app/audio/whisper.py` | **수정** | S1: `prompt=WHISPER_PROMPT` 추가, S2+S3: 할루시네이션 필터 강화 |
| `backend/app/rag/vocab/keyword_dict.py` | **수정** | R1: weak_intent 5→20개 확장, "안내" STOPWORDS 제거 |
| `backend/tests/test_phase_a_verification.py` | **생성** | 검증 테스트 스크립트 |

---

## S1: WHISPER_PROMPT 적용 (whisper.py:63)

**문제**: `WHISPER_PROMPT`를 import만 하고 실제 API 호출에 전달하지 않음
**수정**: `prompt=WHISPER_PROMPT` 파라미터 추가

```python
# Before
transcript = self.client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ko",
)

# After
transcript = self.client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ko",
    prompt=WHISPER_PROMPT,  # ← 추가
)
```

**효과**: Whisper에 "한국 신용카드 고객센터 통화"라는 컨텍스트 제공 → YouTube/방송 관련 할루시네이션 대폭 감소

---

## S2+S3: 할루시네이션 필터 강화 (whisper.py)

### 키워드 확장 (12 → 22개)
```
추가: "구독 좋아요", "오늘도 맛있게", "잘 먹었습니다", "감사합니다 여러분",
      "다음 시간에", "그럼 다음", "시간에 만나요", "자막 제공", "자막 by", "한국어 자막"
```

### 반복 패턴 감지
```python
REPEAT_PATTERN = re.compile(r'(.{2,}?)\1{2,}')
# "아아아아아아" → 차단
# "네네네네네네" → 차단
```

### 최소 길이 체크
```python
MIN_TEXT_LENGTH = 2  # 1자("네", ".", etc.) 필터
```

### 통합 함수 `is_hallucination()`
```python
def is_hallucination(text: str) -> bool:
    if not text or not text.strip(): return True
    text = text.strip()
    if len(text) < MIN_TEXT_LENGTH: return True
    if any(kw in text for kw in HALLUCINATION_KEYWORDS): return True
    if REPEAT_PATTERN.search(text): return True
    return False
```

**참고**: `stt_engine.py`(Qwen3-ASR, faster-whisper)에는 이미 동일한 필터가 구현되어 있음

---

## R1: weak_intent 5 → 20개 확장 (keyword_dict.py)

### Before
```python
WEAK_INTENT_ROUTE_HINTS = {
    "혜택": ROUTE_CARD_INFO,
    "발급": ROUTE_CARD_USAGE,
    "신청": ROUTE_CARD_USAGE,
    "사용": ROUTE_CARD_USAGE,
    "사용처": ROUTE_CARD_USAGE,
}
```

### After
```python
WEAK_INTENT_ROUTE_HINTS = {
    # 기존 5개
    "혜택", "발급", "신청", "사용", "사용처",
    # 추가 15개
    "조회", "확인", "안내", "상담",
    "변경", "해지", "취소", "등록",
    "한도", "납부", "결제", "이체", "충전", "환불", "교환",
}
```

### 추가 조치
- `"안내"`를 `STOPWORDS`에서 제거 (weak_intent와 충돌 방지)

---

## 검증 테스트 결과

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [STT 할루시네이션 필터]
    정확도: 12/21 (57%) → 21/21 (100%)
    개선 항목: 9건

  [Vocab Gate]
    통과율: 12/21 (57%) → 18/21 (86%)
    정확도: 12/18 (67%) → 18/18 (100%)
    개선 항목: 6건

  전체 결과: ✅ PASS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Vocab Gate 개선 상세

| 쿼리 | Before | After |
|------|--------|-------|
| "한도 좀 올려주세요" | ❌ 차단 | ✅ 통과 |
| "납부일이 언제예요?" | ❌ 차단 | ✅ 통과 |
| "충전 방법이 어떻게 되나요?" | ❌ 차단 | ✅ 통과 |
| "조회가 안 되는데요" | ❌ 차단 | ✅ 통과 |
| "변경하고 싶어요" | ❌ 차단 | ✅ 통과 |
| "취소하고 싶습니다" | ❌ 차단 | ✅ 통과 |

경계 케이스 ("이거 어떻게 써요?", "그냥 좀 알아보려고요", "잘 안 되는데요")는 여전히 차단 → Phase B에서 형태소 분석 폴백으로 해결 예정

---

## 검증 실행 방법

```bash
cd backend
python -m tests.test_phase_a_verification
```

---

## 다음 단계 (Phase B)

| 항목 | 설명 | 담당 |
|------|------|------|
| Vocab Gate 형태소 분석 폴백 | 키워드 매칭 실패 시 명사 추출로 재검토 | Backend |
| card_products 벡터 검색 활성화 | retriever에서 card도 pgvector 사용 | Backend |
| referenced_documents 필드 확장 | documentType, content 추가 저장 | B+F 협업 |
| 문서 ID 체계 통일 | rag- prefix 제거 | B+F 협업 |
| card_products 키워드 채우기 | 49% 빈 배열 → Data 팀 | B+D 협업 |
