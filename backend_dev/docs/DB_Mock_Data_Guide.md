# CALL:ACT DB Mock 데이터 생성 가이드

## 메타데이터
- **작성일**: 2026-02-03
- **작성자**: CALL:ACT Team
- **버전**: v1.0
- **상태**: 완료
- **관련 문서**: [CALLACT_DB_종합_명세서.md](./CALLACT_DB_종합_명세서.md)

---

## 목적

이 문서는 `01b_populate_mock_data.py` 스크립트가 생성하는 Mock 데이터의 구조와 내용을 설명합니다.
기본 스키마 적재(`01a_setup_callact_db.py`) 후 실행하여 테이블의 확장 필드에 현실적인 Mock 데이터를 채웁니다.

---

## 실행 방법

```bash
cd backend_dev/app/db/scripts

# 1단계: 기본 스키마 및 데이터 적재
python 01a_setup_callact_db.py

# 2단계: Mock 데이터 생성
python 01b_populate_mock_data.py
```

**멱등성 보장**: `RANDOM_SEED=42`를 사용하여 누가 실행해도 동일한 결과를 보장합니다.

---

## 생성되는 데이터 (5단계)

### 1. Customers 5타입 매핑 (`populate_customers_types.py`)

**대상 필드**:
- `current_type_code`: 고객 페르소나 타입 (N1, N2, S1, S2, S3)
- `type_history`: 최근 3건의 상담과 연결된 타입 이력

**타입 분포**:
| 코드 | 유형명 | 분포 |
|------|--------|------|
| N1 | 일반친절형 | 50% |
| N2 | 조용한내성형 | 20% |
| S1 | 급한성격형 | 10% |
| S2 | 꼼꼼상세형 | 10% |
| S3 | 감정호소형 | 10% |

**type_history 예시**:
```json
[
  {
    "type_code": "N2",
    "consultation_id": "CS-EMP038-202601231059",
    "assigned_at": "2026-01-23"
  },
  {
    "type_code": "N1",
    "consultation_id": "CS-EMP006-202601231024",
    "assigned_at": "2026-01-23"
  },
  {
    "type_code": "N1",
    "consultation_id": "CS-EMP005-202601231004",
    "assigned_at": "2026-01-23"
  }
]
```

---

### 2. Consultations 확장 필드 (`populate_extended_fields.py`)

**대상 필드**:

| 필드 | 설명 | 생성 비율 |
|------|------|----------|
| `acw_duration` | 후처리 시간 (30-300초) | 100% |
| `transcript` | 상담 녹취록 (마스킹 처리) | 100% |
| `ai_summary` | AI 생성 요약 | 100% |
| `feedback_text` | 고객 피드백 텍스트 | ~60% |
| `feedback_emotions` | 감정 태그 배열 | ~60% |
| `follow_up_schedule` | 후속 조치 일정 | ~20% |
| `transfer_department` | 이관 부서 | ~5% |
| `transfer_notes` | 이관 사유 | ~5% |

**transcript 예시**:
```
[00:00] 상담사: 안녕하세요, 테디카드 고객센터입니다. 무엇을 도와드릴까요?
[00:05] 고객: 네, 카드 결제 관련해서 문의드립니다.
[00:10] 상담사: 네, 말씀해 주세요. 어떤 부분이 궁금하신가요?
...
```

**feedback_emotions 예시**:
```json
["satisfied", "grateful"]
```

**follow_up_schedule 예시**:
```json
{
  "scheduled_date": "2026-01-30",
  "scheduled_time": "14:00",
  "reason": "한도 상향 심사 결과 안내",
  "assigned_agent": "EMP-023"
}
```

---

### 3. Usage 통계 데이터 (`populate_usage_stats.py`)

#### service_guide_documents

| 필드 | 설명 | 범위 |
|------|------|------|
| `usage_count` | 문서 조회 횟수 | 0-500 |
| `last_used` | 마지막 사용일 | 최근 30일 내 |

**분포**:
- 10%: 인기 문서 (100-500회)
- 20%: 중간 (20-99회)
- 70%: 낮음 (0-19회)

#### consultation_documents

| 필드 | 설명 | 범위 |
|------|------|------|
| `usage_count` | 참조 횟수 | 0-100 |
| `effectiveness_score` | 효과성 점수 | 0.00-1.00 |
| `last_used` | 마지막 참조일 | 최근 30일 내 |

---

### 4. Simulation 데이터 (`populate_simulation_data.py`)

**대상 필드**:

| 필드 | 설명 |
|------|------|
| `similarity_score` | 유사도 점수 (0-100) |
| `keyword_match_score` | 키워드 매칭 점수 (0-100) |
| `document_match_score` | 문서 매칭 점수 (0-100) |
| `sequence_match_score` | 시퀀스 정확도 점수 (0-100) |
| `time_comparison` | 시간 비교 정보 (JSONB) |
| `ai_customer_reactions` | AI 고객 반응 (JSONB) |
| `recording_file_path` | 녹취 파일 경로 |
| `recording_transcript` | 녹취 전문 (JSONB) |

**난이도별 점수 범위**:
- 초급(easy): 70-90점 기반
- 중급(medium): 50-80점 기반
- 고급(hard): 30-70점 기반

**time_comparison 예시**:
```json
{
  "original_duration_sec": 420,
  "simulation_duration_sec": 485,
  "time_difference_sec": 65,
  "efficiency_ratio": 0.87
}
```

**ai_customer_reactions 예시**:
```json
[
  {"reaction": "satisfied", "message": "네, 잘 이해했습니다.", "step": 1, "timestamp": "2:30"},
  {"reaction": "grateful", "message": "빠르게 처리해 주셔서 감사해요.", "step": 2, "timestamp": "5:15"}
]
```

---

### 5. Keyword 동의어/변형어 (`populate_keyword_extensions.py`)

**대상 필드**:
- `synonyms`: 동의어 배열
- `variations`: 변형어 배열

**정의된 키워드 수**: 56개 핵심 키워드

**예시**:

| 키워드 | synonyms | variations |
|--------|----------|------------|
| 결제 | 지불, 납부, 페이먼트, 페이 | 결제하다, 결제금, 결제액, 결제일 |
| 분실 | 잃어버림, 유실, 도난 | 분실하다, 분실신고, 분실접수 |
| 한도 | 이용한도, 사용한도, 리밋 | 한도조회, 한도상향, 한도증액 |
| 포인트 | 적립금, 리워드, 마일리지 | 포인트적립, 포인트사용, 포인트조회 |
| 승인 | 허가, 인가, 확인 | 승인하다, 승인번호, 승인취소 |

**카테고리별 키워드**:
- 결제/승인: 결제, 승인, 취소, 거절
- 카드: 카드, 발급, 갱신, 등록
- 분실/도난: 분실, 도난, 정지, 해지
- 한도: 한도, 상향, 변경
- 이용내역: 내역, 조회, 명세서
- 포인트/혜택: 포인트, 혜택, 적립, 할인
- 대출: 대출, 상환, 이자, 연체
- 계좌: 계좌, 이체, 출금, 입금
- 신청/문의: 신청, 문의, 상담, 접수
- 보안: 비밀번호, 인증, 보안
- 금액: 금액, 수수료, 연회비, 청구
- 서비스: 서비스, 앱, 어플, 알림
- 해외: 해외, 환율, 달러

---

## 최종 통계

| 테이블 | 레코드 수 | 채워진 필드 |
|--------|----------|-------------|
| customers | 2,500 | current_type_code, type_history |
| consultations | 6,533 | transcript, ai_summary, feedback 등 |
| service_guide_documents | 1,273 | usage_count, last_used |
| consultation_documents | 6,533 | usage_count, effectiveness_score |
| simulation_results | 148 | 점수, 녹취, AI 반응 |
| keyword_dictionary | 2,881 | synonyms (562건), variations (562건) |

---

## 파일 구조

```
backend_dev/app/db/scripts/
├── 01a_setup_callact_db.py      # 스키마 + 기본 데이터 적재
├── 01b_populate_mock_data.py    # Mock 데이터 생성 (오케스트레이터)
└── modules/
    ├── populate_customers_types.py      # [1/5] 고객 타입
    ├── populate_extended_fields.py      # [2/5] 상담 확장 필드
    ├── populate_usage_stats.py          # [3/5] 사용 통계
    ├── populate_simulation_data.py      # [4/5] 시뮬레이션
    ├── populate_keyword_extensions.py   # [5/5] 키워드 확장
    └── keyword_synonyms_data.py         # 키워드 동의어/변형어 정의
```

---

## 주의사항

1. **실행 순서**: 반드시 `01a_setup_callact_db.py` → `01b_populate_mock_data.py` 순서로 실행
2. **멱등성**: 여러 번 실행해도 동일한 결과 (RANDOM_SEED=42)
3. **인코딩**: Windows 환경에서는 UTF-8 설정 필요
4. **DB 연결**: `.env` 파일에 DB_PORT=5555 확인

---

## 결론

`01b_populate_mock_data.py`는 5단계로 모든 테이블의 확장 필드에 현실적인 Mock 데이터를 채웁니다.
이 데이터를 통해 RAG 검색, 시뮬레이션 교육, 고객 페르소나 기반 상담 지원 기능을 테스트할 수 있습니다.
