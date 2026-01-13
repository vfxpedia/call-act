# 테디카드 전처리 문서 (개인 소지용)

## 작성일: 2026-01-11
## 목적: 테디카드 데이터 전처리 과정 및 실행 가이드 (개인 개발 참고용)

---

**참고**: 
- 이 문서는 개인 개발 환경(`docs/04_dev/01_data-preprocessing`)에서 관리되는 문서입니다.
- 팀 공유용 핵심 문서: `data-preprocessing/docs/teddycard_preprocessing/` (간단한 실행 가이드만 포함)
- 전체 문서 목록: `docs/04_dev/01_data-preprocessing/README.md`

---

## 문서 목록

### 실행 가이드 (우선순위)

1. **[13_실행_가이드_최종_완성.md](./13_실행_가이드_최종_완성.md)** ⭐ **가장 먼저 보기!**
   - 실제 실행 가능한 단계별 가이드
   - STT 키워드 → VectorDB 검색 시나리오
   - 문서 번호 정보 점검 결과
   - 빠른 실행 명령어

2. **[16_데이터_복사_및_커밋_가이드.md](./16_데이터_복사_및_커밋_가이드.md)**: 데이터 복사 및 Git 커밋 가이드
   - data-preprocessing_dev → data-preprocessing 복사 가이드
   - Git 서브모듈 커밋 방법
   - 브랜치 생성 및 푸시

---

### 작업 요약 및 검증 문서

3. **[00_전처리_작업_요약.md](./00_전처리_작업_요약.md)**: 작업 전체 요약
   - 주요 작업 내용
   - 생성된 스크립트
   - 주요 결정 사항

4. **[10_전처리_재검증_완료_보고서.md](./10_전처리_재검증_완료_보고서.md)**: 재검증 결과
   - 발견된 문제점
   - 수정 완료 사항
   - 확인 사항

---

### 검토 및 개선 방안 문서

5. **[12_merge_로직_적용_검토.md](./12_merge_로직_적용_검토.md)**: merge 로직 검토
   - 각 데이터 소스별 merge 적용 여부
   - merge 기준 및 효과

6. **[11_키워드_사전_개선_방안.md](./11_키워드_사전_개선_방안.md)**: 키워드 사전 개선 방안
   - hana 데이터 활용 방안
   - 향후 개선 계획

---

### 전략 및 설계 문서

7. **[02_테디카드_통합_전략_및_rag_검색_최적화_분석.md](./02_테디카드_통합_전략_및_rag_검색_최적화_분석.md)**: 테디카드 통합 전략
   - 데이터 소스 통합 방안
   - RAG 검색 최적화 전략

8. **[03_테디카드_전처리_검증_및_통합_전략.md](./03_테디카드_전처리_검증_및_통합_전략.md)**: 전처리 검증 및 통합 전략
   - 텍스트 치환 검증
   - 문서 통합 전략
   - RAG 검색 워크플로우

9. **[04_DB_적재_전_데이터_보강_전략.md](./04_DB_적재_전_데이터_보강_전략.md)**: DB 적재 전 데이터 보강
   - 필수 필드 보완
   - LLM 기반 데이터 보강

10. **[05_청킹_필요성_분석_결과.md](./05_청킹_필요성_분석_결과.md)**: 청킹 필요성 분석
    - 문서 길이 분석
    - 청킹 필요 여부 판단

11. **[14_파일_구조_및_워크플로우_정리.md](./14_파일_구조_및_워크플로우_정리.md)**: 파일 구조 및 워크플로우
    - 중간 파일 vs 최종 파일 구분
    - 작업 흐름 정리

---

## 빠른 시작

### 실행 순서

1. **환경 설정** (1회성)
   ```bash
   conda activate final_env
   cd data-preprocessing_dev/preprocessing/tedicard  # 개발 환경
   # 또는
   cd data-preprocessing/preprocess/teddycard  # 팀 공유 환경
   ```

2. **데이터 변환** (01~05 스크립트)
   ```bash
   python 01_convert_shinhan_cards.py
   python 02_convert_hyundai_guides.py
   python 03_convert_samsung_guides.py
   python 04_convert_shinhan_terms.py
   python 05_convert_special_cards.py
   ```

3. **데이터 보강**
   ```bash
   python 07_enrich_for_db.py
   ```

4. **키워드 추출**
   ```bash
   python 08_extract_keywords.py
   ```

5. **임베딩 생성**
   ```bash
   python 06_generate_embeddings.py
   ```

**상세 가이드**: [13_실행_가이드_최종_완성.md](./13_실행_가이드_최종_완성.md) 참고

---

## 주요 특징

### 1. 문서 번호 정보
- 약관 조 번호: `title` 필드에 포함 (예: "제1조(목적)")
- 문서 식별자: `id` 필드
- 출처 정보: `metadata.original_source`
- 프론트엔드 표시 가능

### 2. 키워드 추출
- 단어사전 기반 키워드 매칭
- LLM 보완 옵션
- STT 키워드 추출 정밀도 향상

### 3. merge 로직
- 삼성/현대: merge 적용
- 신한 약관: merge 미적용 (조 단위 독립성 유지)
- 스페셜 카드: merge 미적용

---

## 스크립트 위치

**개인 개발 환경**:
```
data-preprocessing_dev/preprocessing/tedicard/
```

**팀 공유 환경**:
```
data-preprocessing/preprocess/teddycard/
```

---

## 출력 파일 위치

**개인 개발 환경**:
```
data-preprocessing_dev/preprocessing/output/
```

**팀 공유 환경**:
```
data-preprocessing/preprocess/output/
```

최종 적재용 파일은 `data-preprocessing/data/teddycard/`에 위치합니다.

---

## 다음 단계

1. **DB 적재**: VectorDB 구성 및 데이터 적재
2. **프론트엔드 연동**: STT 키워드 → VectorDB 검색 → 화면 표시
3. **키워드 사전 개선**: hana 데이터 활용
