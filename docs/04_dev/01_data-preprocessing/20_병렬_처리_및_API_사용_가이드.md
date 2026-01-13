# 병렬 처리 및 OpenAI API 사용 가이드

**작성일**: 2026-01-12  
**작성자**: CALL:ACT Team  
**버전**: v1.0

---

## 개요

RAG 구조화 데이터 생성 시 병렬 처리를 통해 시간을 단축할 수 있습니다. 하지만 OpenAI API의 rate limit을 고려하여 안전하게 사용해야 합니다.

---

## 1. OpenAI API Rate Limit

### 1.1 기본 제한

- **GPT-4o-mini**: 분당 500 requests (Tier 1 기준)
- **동시 요청**: 제한 없음 (하지만 rate limit 초과 시 429 오류)

### 1.2 안전 마진 설정

코드에서는 안전 마진을 두고 **분당 60 requests**로 제한합니다:
- 예상치 못한 요청 증가 대비
- 다른 프로세스와의 충돌 방지

---

## 2. 병렬 처리 옵션

### 2.1 순차 처리 (기본, 권장)

**설정**:
```bash
# .env 파일
# STRUCTURE_USE_PARALLEL 설정 안 함 또는 false
```

**특징**:
- ✅ 가장 안전함
- ✅ Rate limit 초과 위험 없음
- ⚠️ 처리 시간: 30-60분 (1000개 문서 기준)

**사용 시나리오**:
- 첫 실행 시
- 안정성 우선 시
- 다른 프로세스와 동시 실행 시

### 2.2 병렬 처리 (선택적)

**설정**:
```bash
# .env 파일
STRUCTURE_USE_PARALLEL=true
STRUCTURE_MAX_WORKERS=5  # 권장: 5-10
```

**특징**:
- ✅ 처리 시간 단축: 10-20분 (1000개 문서, 5 workers 기준)
- ⚠️ Rate limit 관리 필요
- ⚠️ 동일 API 키를 다른 노트북에서 동시 사용 금지

**사용 시나리오**:
- 시간 단축이 필요한 경우
- 하나의 노트북에서만 실행하는 경우
- Rate limit 여유가 있는 경우

---

## 3. API 키 사용 규칙

### 3.1 하나의 API 키로 병렬 처리 가능

✅ **단일 노트북에서 병렬 처리**: 가능
- 하나의 API 키로 여러 worker가 동시에 요청 가능
- Rate limit만 준수하면 문제없음

### 3.2 여러 노트북에서 동시 사용

❌ **권장하지 않음**: Rate limit 초과 위험
- 동일 API 키를 여러 노트북에서 동시 사용 시 전체 요청 수가 합산됨
- Rate limit 초과 시 429 오류 발생

**예시**:
```
노트북 A: 5 workers × 60 requests/min = 300 requests/min
노트북 B: 5 workers × 60 requests/min = 300 requests/min
총합: 600 requests/min > 500 (rate limit 초과!)
```

### 3.3 권장 사용 방법

**옵션 1: 하나의 노트북에서 순차 처리** (가장 안전)
```bash
# .env
# STRUCTURE_USE_PARALLEL 설정 안 함
python 11_structured_for_rag.py
```

**옵션 2: 하나의 노트북에서 병렬 처리** (빠르고 안전)
```bash
# .env
STRUCTURE_USE_PARALLEL=true
STRUCTURE_MAX_WORKERS=5
python 11_structured_for_rag.py
```

**옵션 3: 여러 노트북에서 순차 처리** (느리지만 안전)
```bash
# 각 노트북에서
# .env
# STRUCTURE_USE_PARALLEL 설정 안 함
python 11_structured_for_rag.py
```

---

## 4. Worker 수 결정 가이드

### 4.1 권장 설정

| 문서 수 | Worker 수 | 예상 시간 | 안전도 |
|---------|-----------|-----------|--------|
| < 500개 | 3 | 5-10분 | 높음 |
| 500-1000개 | 5 | 10-20분 | 중간 |
| 1000-2000개 | 5-7 | 20-30분 | 중간 |
| > 2000개 | 7-10 | 30-40분 | 낮음 |

### 4.2 Worker 수 계산

**공식**:
```
Worker 수 = min(문서 수 / 100, 10)
```

**예시**:
- 500개 문서: min(5, 10) = 5 workers
- 2000개 문서: min(20, 10) = 10 workers

---

## 5. Rate Limit 관리

### 5.1 코드 내 Rate Limit 관리

코드는 자동으로 rate limit을 관리합니다:

```python
# 분당 60 requests로 제한
RATE_LIMIT_PER_MINUTE = 60

# Rate limit 초과 시 자동 대기
if rate_limit_count >= RATE_LIMIT_PER_MINUTE:
    wait_time = 60 - (current_time - rate_limit_reset_time)
    time.sleep(wait_time)
```

### 5.2 Rate Limit 오류 대응

**429 Too Many Requests 오류 발생 시**:

1. **즉시 조치**:
   ```bash
   # 스크립트 중단 (Ctrl+C)
   # .env에서 병렬 처리 비활성화
   STRUCTURE_USE_PARALLEL=false
   ```

2. **재실행**:
   ```bash
   # 순차 처리로 재실행
   python 11_structured_for_rag.py
   ```

3. **Worker 수 감소**:
   ```bash
   # .env
   STRUCTURE_USE_PARALLEL=true
   STRUCTURE_MAX_WORKERS=3  # 5 → 3으로 감소
   ```

---

## 6. 성능 비교

### 6.1 처리 시간 비교 (1000개 문서 기준)

| 방식 | Worker 수 | 예상 시간 | Rate Limit 위험 |
|------|-----------|-----------|-----------------|
| 순차 처리 | 1 | 50-60분 | 없음 |
| 병렬 처리 | 3 | 20-25분 | 낮음 |
| 병렬 처리 | 5 | 10-20분 | 중간 |
| 병렬 처리 | 10 | 5-10분 | 높음 |

### 6.2 권장 설정

**안전 우선**: 순차 처리 또는 3 workers  
**균형**: 5 workers (권장)  
**속도 우선**: 7-10 workers (주의 필요)

---

## 7. 체크리스트

### 7.1 병렬 처리 사용 전 확인

- [ ] `.env` 파일에 `STRUCTURE_USE_PARALLEL=true` 설정
- [ ] `STRUCTURE_MAX_WORKERS` 값 확인 (권장: 5)
- [ ] 다른 노트북에서 동일 API 키 사용 중인지 확인
- [ ] 네트워크 연결 안정성 확인

### 7.2 실행 중 모니터링

- [ ] Rate limit 오류 (429) 발생 여부 확인
- [ ] 처리 속도 모니터링
- [ ] 메모리 사용량 확인

### 7.3 오류 발생 시

- [ ] 즉시 스크립트 중단
- [ ] `.env`에서 병렬 처리 비활성화
- [ ] 순차 처리로 재실행

---

## 8. FAQ

### Q1: 하나의 API 키로 병렬 처리가 가능한가요?

**A**: 네, 가능합니다. 하나의 API 키로 여러 worker가 동시에 요청할 수 있습니다. 다만 rate limit을 준수해야 합니다.

### Q2: 다른 노트북에서 동시에 실행해도 되나요?

**A**: 권장하지 않습니다. 동일 API 키를 여러 노트북에서 동시 사용 시 rate limit 초과 위험이 높습니다.

### Q3: Worker 수를 늘리면 더 빠른가요?

**A**: 어느 정도까지는 그렇지만, rate limit에 도달하면 오히려 느려질 수 있습니다. 권장: 5-7 workers.

### Q4: Rate limit 오류가 발생하면 어떻게 하나요?

**A**: 즉시 스크립트를 중단하고, 순차 처리로 전환하거나 worker 수를 줄여서 재실행하세요.

---

## 결론

- ✅ **하나의 API 키로 병렬 처리 가능**: 단일 노트북에서 5-10 workers 사용 권장
- ❌ **여러 노트북에서 동시 사용 금지**: Rate limit 초과 위험
- 💡 **권장**: 안전하게 하나의 노트북에서 순차 처리 또는 병렬 처리 (5 workers)
