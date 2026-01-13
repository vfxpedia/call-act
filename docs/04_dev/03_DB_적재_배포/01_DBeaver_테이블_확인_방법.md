# DBeaver에서 테이블 확인 방법

**작성일**: 2026-01-11  
**목적**: DBeaver에서 생성된 테이블이 보이지 않을 때 확인 방법

---

## 문제 상황

SQL 스크립트를 실행했지만 DBeaver의 Database Navigator에서 테이블이 보이지 않는 경우

---

## 해결 방법

### 방법 1: Database Navigator 새로고침 (가장 일반적)

1. **전체 데이터베이스 새로고침**:
   - 왼쪽 패널에서 `callact_db` 우클릭
   - `Refresh` 클릭 또는 `F5` 키 누르기

2. **스키마 새로고침**:
   - `Schemas` → `public` 우클릭
   - `Refresh` 클릭

3. **Tables 폴더 새로고침**:
   - `Schemas` → `public` → `Tables` 우클릭
   - `Refresh` 클릭

### 방법 2: SQL로 테이블 목록 확인

**모든 테이블 목록 조회**:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

**특정 테이블 확인**:
```sql
-- keyword_dictionary 테이블 확인
SELECT COUNT(*) as row_count 
FROM keyword_dictionary;

-- keyword_synonyms 테이블 확인
SELECT COUNT(*) as row_count 
FROM keyword_synonyms;
```

**테이블 구조 확인**:
```sql
-- keyword_dictionary 테이블 구조
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'keyword_dictionary'
ORDER BY ordinal_position;
```

### 방법 3: DBeaver 재연결

1. **연결 종료 후 재연결**:
   - 왼쪽 패널에서 `callact_db` 우클릭
   - `Disconnect` 클릭
   - 다시 우클릭 → `Connect` 클릭

2. **DBeaver 재시작**:
   - DBeaver 완전 종료 후 재시작

---

## 생성된 테이블 확인 체크리스트

### 키워드 사전 관련 테이블

- [ ] `keyword_dictionary` 테이블 존재 확인
- [ ] `keyword_synonyms` 테이블 존재 확인
- [ ] 인덱스 생성 확인:
  ```sql
  SELECT indexname 
  FROM pg_indexes 
  WHERE schemaname = 'public' 
  AND tablename IN ('keyword_dictionary', 'keyword_synonyms');
  ```

### 테디카드 데이터 관련 테이블

- [ ] `card_products` 테이블 존재 확인
- [ ] `service_guide_documents` 테이블 존재 확인
- [ ] `notices` 테이블 존재 확인

### 하나카드 데이터 관련 테이블

- [ ] `consultations` 테이블 존재 확인
- [ ] `consultation_documents` 테이블 존재 확인
- [ ] `employees` 테이블 존재 확인

---

## 일반적인 문제 해결

### 문제 1: 테이블이 생성되지 않음

**확인 사항**:
1. SQL 스크립트 실행 시 에러가 없었는지 확인
2. Output 탭에서 에러 메시지 확인
3. 트랜잭션이 커밋되었는지 확인 (`COMMIT` 실행)

**해결**:
```sql
-- 트랜잭션 상태 확인
SELECT * FROM pg_stat_activity WHERE datname = 'callact_db';

-- 수동 커밋
COMMIT;
```

### 문제 2: 권한 문제

**확인**:
```sql
-- 현재 사용자 확인
SELECT current_user;

-- 테이블 소유자 확인
SELECT 
    table_name,
    table_schema,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
AND table_name = 'keyword_dictionary';
```

**해결**: 관리자 권한으로 실행하거나 테이블 소유자에게 권한 요청

### 문제 3: 다른 스키마에 생성됨

**확인**:
```sql
-- 모든 스키마의 테이블 확인
SELECT 
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_name IN ('keyword_dictionary', 'keyword_synonyms')
ORDER BY table_schema, table_name;
```

**해결**: 올바른 스키마(`public`)에 생성되었는지 확인

---

## 빠른 확인 쿼리

**모든 테이블과 행 수 확인**:
```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

**최근 생성된 테이블 확인**:
```sql
SELECT 
    table_name,
    table_schema,
    pg_size_pretty(pg_total_relation_size('"' || table_schema || '"."' || table_name || '"')) as size
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```
