# 01_B: Frontend 질문 응답 + STT 할루시네이션 진단

> **담당**: Backend
> **날짜**: 2026-02-10
> **참조**: `docs/levelup/00_F_현상분석_문서시스템.md`

---

## Frontend 팀 질문에 대한 Backend 응답

### Q1. RAG 응답에 documentType, fullText 필드 포함 여부?

**✅ 둘 다 포함됨. camelCase로 전송.**

| 필드 | 타입 | 출처 | 비어있을 때 |
|------|------|------|------------|
| `documentType` | string | metadata.documentType → 테이블명 매핑 → `"general"` 폴백 | 빈 문자열 `""` (절대 null 아님) |
| `fullText` | string\|null | structured.detailContent → metadata.full_content → doc.content 순서 | `null` (명시적 nullable) |

**주의**: `fullText`가 `null`인 경우는 원본 문서에 `detailContent`, `full_content`, `content` 모두 비어있을 때.
실제로 card_products의 경우 `structured.detailContent`가 풍부하므로 대부분 값이 있음.
service_guide_documents는 `content` 필드에 본문이 있으므로 역시 대부분 값이 있음.

### Q2. 상담 저장 시 referenced_documents에 doc_type, full_text 저장 여부?

**❌ 저장하지 않음. 이것이 구조적 단절의 원인.**

현재 `ReferencedDocument` 모델 (consultations.py):
```
stepNumber  - RAG 조회 순서
documentId  - 문서 ID (예: "DOC-123")
title       - 제목
used        - 클릭 여부
viewCount   - 조회 횟수
```

**누락된 필드**: `documentType`, `fullText`, `content`, `keywords`

→ 상담 후 상세 내역에서 참조 문서를 다시 열 때, ID만으로 원본을 찾아야 함.
→ **조치 필요**: `documentType`, `content` (요약) 최소 추가 필요

### Q3. DB 문서 ID 체계 (프론트와 통일 필요)?

**Backend는 원본 DB ID를 그대로 전달함. `rag-` prefix는 Backend에 없음.**

| DB 테이블 | ID 형식 예시 |
|----------|-------------|
| card_products | `CARD-SHINHAN-#Pay-신한카드` |
| service_guide_documents | `신용도_관리방법_merged`, `narasarang_faq_005`, `sinhan_terms_credit_..._039` |
| consultation_documents | `hana_consultation_20593` |
| notices | `notice_01` |

**카드 파이프라인에서 ID 생성 로직** (card_generator.py):
```python
"id": str(doc.get("id") or meta.get("id") or "")
```

→ 변환 없이 DB 원본 ID 직통. `rag-` prefix는 Frontend에서 생성하는 것으로 추정.
→ **협의 필요**: Frontend가 `rag-` prefix를 붙이는 곳을 찾아서, DB ID를 그대로 쓰도록 통일

### Q4. FAQ 관련 문서 API 존재 여부?

**✅ 존재함. `GET /api/v1/frequent-inquiries`**

응답에 `relatedDocument` 포함:
```json
{
  "id": 1,
  "keyword": "카드 분실",
  "question": "...",
  "count": 45,
  "trend": "up",
  "relatedDocument": {
    "document_id": "...",    ← snake_case (주의!)
    "title": "...",
    "regulation": "...",
    "summary": "..."
  }
}
```

**주의**: FAQ 응답의 `relatedDocument.document_id`는 **snake_case**. RAG 카드의 `id`와 네이밍 불일치.
→ **조치 필요**: 프론트에서 변환하거나, 백엔드에서 camelCase로 통일

---

## STT 할루시네이션 진단

### 🔴 치명적 버그 발견: WHISPER_PROMPT가 적용되지 않고 있음

**파일**: `backend/app/audio/whisper.py` (현재 프로덕션 활성 코드)

```python
from app.core.prompt import WHISPER_PROMPT  # ← import는 했지만...

transcript = self.client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ko",
    # ← prompt= 파라미터가 없음! WHISPER_PROMPT 미사용!
)
```

**WHISPER_PROMPT 내용**:
```
한국 신용카드 고객센터 통화 녹취록입니다.
발화된 내용만 원문 그대로 출력하세요. 침묵은 무시하세요.
추가, 바꿔쓰기, 요약, 수정은 일절 금지합니다.
```

이 프롬프트가 Whisper에 전달되면:
- "이것은 카드 고객센터 통화다"라는 컨텍스트 제공
- **"침묵은 무시하세요"** → 침묵 구간에서의 할루시네이션 대폭 감소
- YouTube/방송 관련 텍스트 생성 확률 급감

**이것이 "좋아요 구독", "감사합니다" 할루시네이션의 직접적 원인입니다.**

### 🟡 2차 원인: 오디오 에너지 체크 없음

현재 흐름:
```
프론트 VAD → 오디오 전송 → [에너지 체크 없음] → Whisper API
```

프론트엔드 VAD가 통과시킨 오디오가 실제로는 노이즈/침묵일 수 있음.
백엔드에서 Whisper API 호출 전 RMS 에너지 체크를 추가하면 불필요한 API 호출 방지 가능.

### 🟡 3차 원인: 할루시네이션 키워드 부족

현재 프로덕션 (`whisper.py`): **12개**만 필터링
`stt_engine.py` (미활성): **22개** + 반복 패턴 + 최소 길이 체크

---

## Backend 자체 즉시 조치 (협업 불필요)

| # | 조치 | 파일 | 효과 | 위험도 |
|---|------|------|------|--------|
| **S1** | whisper.py에 `prompt=WHISPER_PROMPT` 추가 | whisper.py:63 | 할루시네이션 **대폭** 감소 | 🟢 매우 낮음 |
| **S2** | whisper.py 할루시네이션 키워드 12개→22+개 확장 | whisper.py:45 | 잔여 할루시네이션 필터 | 🟢 낮음 |
| **S3** | 반복 패턴 + 최소 길이 체크 추가 | whisper.py | 추가 안전장치 | 🟢 낮음 |
| **S4** | 백엔드 오디오 에너지 체크 추가 | whisper.py | 불필요한 API 호출 방지 | 🟡 중간 |

### 프론트 협업 필요 조치

| # | 조치 | 협업 대상 | 내용 |
|---|------|----------|------|
| **C1** | referenced_documents 필드 확장 | F+B | `documentType`, `content` 추가 저장 |
| **C2** | 문서 ID 체계 통일 | F+B | `rag-` prefix 제거, DB 원본 ID 사용 |
| **C3** | FAQ relatedDocument 네이밍 통일 | F+B | snake_case → camelCase 또는 변환 유틸 |
| **C4** | card_products 키워드 채우기 | D+B | 49% 빈 배열 해결 |
| **C5** | weak_intent 확장 | B+D | 5개 → 15+개 |

---

## 조치 우선순위 (권장 순서)

```
[즉시] S1: WHISPER_PROMPT 적용 → STT 할루시네이션 해결
[즉시] S2+S3: 할루시네이션 필터 강화
[1차] C5: weak_intent 확장 → RAG 차단률 감소
[1차] C1: referenced_documents 필드 확장 → 문서 재참조 가능
[2차] C2: ID 체계 통일 → 전체 문서 연결 정상화
[2차] C4: card_products 키워드 → 검색 커버리지 확대
```
