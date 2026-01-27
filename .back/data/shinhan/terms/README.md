# 신한카드 약관 데이터 전처리 완료 보고서

**작성일**: 2026-01-08
**프로젝트**: CALL-ACT 카드사 상담 지원 시스템
**담당**: 데이터 전처리 팀

---

## 1. 작업 개요

### 목표
신한카드 약관 TXT 파일 86개를 RAG 검색에 최적화된 JSON 형식으로 변환하여 RDB 및 VectorDB에 저장 가능한 데이터 생성

### 작업 기간
2026-01-08 (1일 완료)

### 작업 결과
- **처리 완료**: 86개 파일 100% 성공
- **생성 청크**: 993개 (중복 제거 후)
- **평균 청크 크기**: 489자
- **데이터 품질**: 검증 완료, 프로덕션 준비 완료

---

## 2. 처리 파이프라인

### 5단계 파이프라인 구조

```
[Stage 1-2] 파싱
   ↓ parse_sinhan_terms.py
   ↓ 86개 TXT → 구조화된 JSON (장/조/항/호)
   ↓
[Stage 3] 청크 생성
   ↓ chunk_sinhan_terms.py
   ↓ 조(條) 단위 청크 분할
   ↓
[Stage 3-통합] 배치 처리
   ↓ batch_process_sinhan_terms.py
   ↓ 86개 파일 자동 처리 + 통계 생성
   ↓
[Stage 4] 검증
   ↓ validate_sinhan_terms.py
   ↓ 품질 검증 + 중복 제거
   ↓
[Stage 5] 최종 생성
   ↓ finalize_sinhan_terms.py
   ↓ RDB/VectorDB용 JSON 생성
   ↓
[완료] 3개 최종 파일 출력
```

---

## 3. 출력 파일

### 3.1 최종 출력 (final/)

| 파일명 | 용도 | 크기 | 설명 |
|--------|------|------|------|
| `sinhan_terms_final.json` | 통합 데이터 | 2.7MB | 모든 필드 포함 (백업/분석용) |
| `sinhan_terms_for_rdb.json` | RDB 적재 | 1.5MB | service_guide_documents 테이블용 |
| `sinhan_terms_for_vectordb.json` | 임베딩 생성 | 1.5MB | OpenAI 임베딩 입력용 |
| `final_metadata.json` | 메타데이터 | 3KB | 통계 및 처리 정보 |

### 3.2 중간 파일 (intermediate/)

| 파일명 | 설명 |
|--------|------|
| `parsed_structure_prototype.json` | 프로토타입 파싱 결과 |
| `chunks_raw_prototype.json` | 프로토타입 청크 결과 |
| `chunks_all.json` | 전체 청크 (중복 포함) |
| `chunks_validated.json` | 검증 완료 청크 (중복 제거) |

### 3.3 리포트 (reports/)

| 파일명 | 설명 |
|--------|------|
| `file_metadata.json` | 파일별 처리 통계 |
| `processing_report.json` | 배치 처리 결과 |
| `validation_report.json` | 검증 상세 리포트 |

---

## 4. 데이터 구조

### 4.1 RDB 형식 (PostgreSQL)

```json
{
  "id": "sinhan_terms_credit_신용카드_개인회원_약관_001",
  "title": "제1조(목적)",
  "content": "이 약관은 회원의 권익보호...",
  "metadata": {
    "category1": "신용카드",
    "category2": "총칙",
    "source": "신한카드 약관",
    "processed_date": "2026-01-08T01:11:58.326858"
  },
  "source_type": "sinhan_terms"
}
```

**테이블**: `service_guide_documents`
- `id`: TEXT PRIMARY KEY
- `title`: TEXT
- `content`: TEXT
- `metadata`: JSONB
- `source_type`: TEXT
- `embedding`: vector(1536) [추후 임베딩 생성 후 업데이트]

### 4.2 VectorDB 형식 (pgvector)

```json
{
  "id": "sinhan_terms_credit_신용카드_개인회원_약관_001",
  "text": "제1조(목적)\n이 약관은 회원의 권익보호...",
  "metadata": {
    "title": "제1조(목적)",
    "category1": "신용카드",
    "category2": "총칙",
    "category1_code": "credit",
    "text_length": 633,
    "source_type": "sinhan_terms"
  }
}
```

---

## 5. 데이터 통계

### 5.1 전체 통계

- **총 청크 수**: 993개
- **원본 파일 수**: 86개
- **평균 청크 크기**: 489자
- **최소 청크 크기**: 16자
- **최대 청크 크기**: 11,916자
- **중복 제거**: 40개

### 5.2 Category1 분포

| 대분류 | 청크 수 | 비율 |
|--------|---------|------|
| 기타서비스 | 188 | 18.9% |
| 전자금융 | 164 | 16.5% |
| 신용카드 | 124 | 12.5% |
| 앱/디지털결제 | 119 | 12.0% |
| 대출/여신 | 104 | 10.5% |
| 계좌/송금 | 102 | 10.3% |
| 가맹점/제휴 | 64 | 6.4% |
| 자동차금융 | 62 | 6.2% |
| 선불카드 | 45 | 4.5% |
| 포인트/리워드 | 21 | 2.1% |

### 5.3 Category2 분포 (상위 10개)

| 중분류 | 청크 수 |
|--------|---------|
| 본문 | 665 |
| 보칙 | 34 |
| 총칙 | 34 |
| 전자금융거래의 종류 및 이용 한도 | 32 |
| 카드 이용 | 30 |
| 총 칙 | 27 |
| 카드이용 | 20 |
| 손해배상 등 | 18 |
| 거래 내역의 확인 | 16 |
| 카드발급/관리 | 15 |

---

## 6. 설계 의사결정

### 6.1 청크 분할 전략: 조(條) 단위

**선택 이유**:
- 약관의 조(條)가 의미적으로 완결된 정보 단위
- 평균 청크 크기 489자로 임베딩에 최적 (OpenAI 권장: 256~512 토큰)
- 사용자 질의 패턴과 일치 ("연회비는?", "해지 방법은?")

**대안 검토**:
- 장(章) 단위: 너무 큼 (1000자 이상)
- 항(①) 단위: 너무 작음 (50~100자)

### 6.2 Category1: 파일명 기반 자동 분류

**매핑 규칙**:
```python
CATEGORY1_MAPPING = {
    "신용카드": ["신용카드", "체크카드", "법인회원", "개인회원"],
    "대출/여신": ["대출", "여신", "마이너스", "스피드론"],
    "앱/디지털결제": ["앱카드", "페이", "간편결제", "CARPAY"],
    # ... 총 10개 카테고리
}
```

**장점**:
- 파일명에 이미 명확한 서비스 구분 존재
- 100% 자동 분류 성공

### 6.3 Category2: 장(章) 제목 기반 추출

**정규화 매핑**:
```python
CATEGORY2_NORMALIZATION = {
    "총칙": "총칙",
    "카드의 발급 및 관리 등": "카드발급/관리",
    "카드 거래 관련": "카드거래",
    # ... 37개 중분류
}
```

### 6.4 ID 생성 규칙

**형식**: `sinhan_terms_{category_code}_{file_code}_{index:03d}`

**예시**:
- `sinhan_terms_credit_신용카드_개인회원_약관_001`
- `sinhan_terms_loan_대출_비교_서비스_이용약관_016`
- `sinhan_terms_app_shinhanpay머니_이용약관_003`

---

## 7. 검증 결과

### 7.1 검증 항목

1. 필수 필드 존재: id, title, content, text, metadata ✅
2. ID 형식: `^sinhan_terms_\w+_[\w가-힣_]+_\d{3}$` ✅
3. 텍스트 길이: 10~3000자 ⚠️ 5개 초과 (최대 11,916자)
4. Category1 유효성: 10개 카테고리 범위 ✅
5. 인코딩: UTF-8 유효성 ✅
6. 중복: 40개 중복 제거 완료 ✅

### 7.2 발견된 이슈

**텍스트 길이 초과 (5건)**:
- Genesis CARPAY 약관: 11,916자 (매우 긴 단일 조항)
- 스마트생활 서비스 약관: 5,157자
- 신용카드 법인회원 약관: 3,103자, 3,168자
- 캐피탈론 기본약관: 3,192자

**권장 조치**:
- RAG 성능에 영향 가능성 있음
- 필요시 항(①) 단위로 추가 분할 고려
- 현재는 검색 가능 상태로 유지

### 7.3 중복 청크 (40건 제거)

**주요 중복 패턴**:
1. Hyundai CarPay vs Kia CarPay 약관 (20건)
   - 두 약관이 거의 동일한 내용
2. 계좌통합관리서비스 vs 계좌통합관리서비스(뱅크 카드 한도대출) (10건)
   - 유사 서비스 약관 중복
3. 대출이동시스템 관련 약관 (10건)
   - 여러 파일에 동일 조항 포함

**처리 결과**: MD5 해시 기반 완전 중복 제거 완료

---

## 8. 스크립트 설명

### 8.1 parse_sinhan_terms.py (Stage 1-2)

**기능**: TXT 파일 파싱 및 구조 분석

**주요 함수**:
- `parse_terms_file()`: 장/조/항/호 파싱
- `categorize_by_filename()`: 파일명 기반 category1 분류
- `normalize_chapter_name()`: 장 제목 정규화

**정규식 패턴**:
```python
PATTERN_CHAPTER = r'^제(\d+)장\s*(.+)$'
PATTERN_ARTICLE = r'^제(\d+)조\s*\((.+)\)$'
PATTERN_PARAGRAPH = r'^([①②③④⑤⑥⑦⑧⑨⑩]+)\s*(.+)$'
```

### 8.2 chunk_sinhan_terms.py (Stage 3)

**기능**: 조(條) 단위 청크 생성

**주요 함수**:
- `create_chunks()`: 파싱 구조 → 청크 변환
- `normalize_text()`: 텍스트 정규화 파이프라인
- `generate_id()`: ID 생성

**정규화 로직**:
```python
def normalize_text(text: str) -> str:
    text = strip_links(text)        # URL 제거
    text = normalize_newlines(text) # 줄바꿈 정규화
    text = squash_ws(text)          # 공백 압축
    return text
```

### 8.3 batch_process_sinhan_terms.py (Stage 1-3 통합)

**기능**: 86개 파일 자동 배치 처리

**출력**:
- `chunks_all.json`: 전체 청크 (1,033개)
- `file_metadata.json`: 파일별 통계
- `processing_report.json`: 처리 결과

### 8.4 validate_sinhan_terms.py (Stage 4)

**기능**: 데이터 검증 및 품질 관리

**검증 항목**:
- 필수 필드 존재
- ID 형식 검증
- 텍스트 길이 검증
- 중복 탐지 (MD5 해시)
- 인코딩 검증

**출력**:
- `chunks_validated.json`: 검증 완료 청크 (993개)
- `validation_report.json`: 상세 검증 리포트

### 8.5 finalize_sinhan_terms.py (Stage 5)

**기능**: 최종 JSON 생성

**출력 형식**:
1. **통합 JSON**: 모든 필드 포함
2. **RDB JSON**: id, title, content, metadata, source_type
3. **VectorDB JSON**: id, text, metadata

---

## 9. 다음 단계

### 9.1 즉시 진행 가능

1. **RDB 적재**
   ```bash
   # PostgreSQL 적재 스크립트 실행
   python load_to_postgres.py --file sinhan_terms_for_rdb.json
   ```

2. **임베딩 생성**
   ```bash
   # OpenAI API를 사용한 임베딩 생성
   python generate_embeddings.py --file sinhan_terms_for_vectordb.json
   ```

3. **VectorDB 저장**
   ```bash
   # pgvector에 임베딩 저장
   python load_to_vectordb.py --embeddings embeddings.json
   ```

### 9.2 선택적 개선 사항

1. **긴 청크 추가 분할**
   - 3000자 초과 5개 청크를 항(①) 단위로 분할
   - 검색 성능 최적화

2. **메타데이터 보강**
   - 시행일자, 개정일자 추출 (부칙 파싱)
   - 연관 약관 링크 추가

3. **증분 업데이트 로직**
   - 새로운 약관 추가 시 자동 처리
   - 기존 약관 변경 감지 및 업데이트

---

## 10. 파일 구조

```
data-preprocessing/
├── preprocess/
│   └── sinhan_terms/
│       ├── parse_sinhan_terms.py          # Stage 1-2
│       ├── chunk_sinhan_terms.py          # Stage 3
│       ├── batch_process_sinhan_terms.py  # Stage 1-3 통합
│       ├── validate_sinhan_terms.py       # Stage 4
│       └── finalize_sinhan_terms.py       # Stage 5
│
└── data/
    └── sinhan_terms/
        ├── raw_data/                      # 입력: 86개 TXT 파일
        ├── intermediate/                  # 중간 결과
        │   ├── parsed_structure_prototype.json
        │   ├── chunks_raw_prototype.json
        │   ├── chunks_all.json
        │   └── chunks_validated.json
        ├── final/                         # 최종 출력 ✅
        │   ├── sinhan_terms_final.json
        │   ├── sinhan_terms_for_rdb.json
        │   ├── sinhan_terms_for_vectordb.json
        │   └── final_metadata.json
        ├── reports/                       # 리포트
        │   ├── file_metadata.json
        │   ├── processing_report.json
        │   └── validation_report.json
        └── README.md                      # 본 문서
```

---

## 11. 참고 문서

- ERD 스키마: `docs/04_dev/01_data-preprocessing/ERD/CALL_ACT_ERD_Schema_설명.md`
- VectorDB 설계: `docs/04_dev/01_data-preprocessing/ERD/VectorDB_통합_설계.md`
- 요구사항 명세: `docs/01_주제 구체화/1224_01_요구사항_명세서.md`

---

## 12. 문의

**데이터 전처리 팀**
- 작성일: 2026-01-08
- 프로젝트: CALL-ACT
