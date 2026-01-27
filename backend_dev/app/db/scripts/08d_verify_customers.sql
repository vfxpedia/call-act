-- ==================================================
-- Customers 데이터 검증 쿼리
-- ==================================================
-- 이 파일의 쿼리들을 실행하여 데이터 무결성을 검증합니다.
-- ==================================================

-- 1. 데이터 무결성 검증
-- ==============================

-- 1.1 모든 상담이 유효한 customer_id를 참조하는지 확인
SELECT COUNT(*) as orphaned_consultations
FROM consultations c
LEFT JOIN customers cu ON c.customer_id = cu.id
WHERE cu.id IS NULL;
-- 기대값: 0

-- 1.2 고객 수 확인
SELECT COUNT(*) as total_customers FROM customers;
-- 기대값: 2,500

-- 1.3 상담 건수 확인
SELECT COUNT(*) as total_consultations FROM consultations;
-- 기대값: 6,533

-- 2. 성별 분포 검증
-- ==============================
SELECT
    gender,
    COUNT(*) as count,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers) * 100, 1) as pct
FROM customers
GROUP BY gender
ORDER BY count DESC;
-- 기대값: female ~55%, male ~45%

-- 3. 연령대 분포 검증
-- ==============================
SELECT
    age_group,
    COUNT(*) as count,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers) * 100, 1) as pct
FROM customers
GROUP BY age_group
ORDER BY age_group;
-- 기대값: 50대 28.3% 최다

-- 4. 등급 분포 검증
-- ==============================
SELECT
    grade,
    COUNT(*) as count,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers) * 100, 1) as pct
FROM customers
GROUP BY grade
ORDER BY
    CASE grade
        WHEN 'VIP' THEN 1
        WHEN 'GOLD' THEN 2
        WHEN 'SILVER' THEN 3
        ELSE 4
    END;
-- 기대값: VIP 3%, GOLD 12%, SILVER 25%, GENERAL 60%

-- 5. 페르소나 분포 검증
-- ==============================
SELECT
    unnest(personality_tags) as tag,
    COUNT(*) as count
FROM customers
GROUP BY tag
ORDER BY count DESC
LIMIT 20;

-- 6. FCR 검증
-- ==============================

-- 6.1 전체 FCR 비율
SELECT
    SUM(resolved_first_call) as fcr_success,
    SUM(total_consultations) as total,
    ROUND(
        SUM(resolved_first_call)::numeric /
        NULLIF(SUM(total_consultations), 0) * 100, 1
    ) as fcr_rate
FROM customers
WHERE total_consultations > 0;
-- 기대값: FCR ~70%

-- 6.2 등급별 FCR 비율
SELECT
    grade,
    COUNT(*) as customer_count,
    SUM(total_consultations) as total_consultations,
    SUM(resolved_first_call) as fcr_success,
    ROUND(
        SUM(resolved_first_call)::numeric /
        NULLIF(SUM(total_consultations), 0) * 100, 1
    ) as fcr_rate
FROM customers
WHERE total_consultations > 0
GROUP BY grade
ORDER BY
    CASE grade
        WHEN 'VIP' THEN 1
        WHEN 'GOLD' THEN 2
        WHEN 'SILVER' THEN 3
        ELSE 4
    END;

-- 6.3 연령대별 FCR 비율
SELECT
    age_group,
    COUNT(*) as customer_count,
    SUM(total_consultations) as total_consultations,
    ROUND(
        SUM(resolved_first_call)::numeric /
        NULLIF(SUM(total_consultations), 0) * 100, 1
    ) as fcr_rate
FROM customers
WHERE total_consultations > 0
GROUP BY age_group
ORDER BY age_group;

-- 7. 상담 횟수 분포 검증
-- ==============================
SELECT
    CASE
        WHEN total_consultations = 1 THEN '1회'
        WHEN total_consultations BETWEEN 2 AND 4 THEN '2-4회'
        WHEN total_consultations BETWEEN 5 AND 9 THEN '5-9회'
        ELSE '10회+'
    END as tier,
    COUNT(*) as customers,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers WHERE total_consultations > 0) * 100, 1) as pct
FROM customers
WHERE total_consultations > 0
GROUP BY
    CASE
        WHEN total_consultations = 1 THEN '1회'
        WHEN total_consultations BETWEEN 2 AND 4 THEN '2-4회'
        WHEN total_consultations BETWEEN 5 AND 9 THEN '5-9회'
        ELSE '10회+'
    END
ORDER BY
    CASE
        WHEN MIN(total_consultations) = 1 THEN 1
        WHEN MIN(total_consultations) BETWEEN 2 AND 4 THEN 2
        WHEN MIN(total_consultations) BETWEEN 5 AND 9 THEN 3
        ELSE 4
    END;
-- 기대값: 1회 35%, 2-4회 45%, 5-9회 17%, 10회+ 3%

-- 8. 샘플 데이터 조회
-- ==============================

-- 8.1 VIP 고객 샘플
SELECT id, name, phone, grade, card_type, total_consultations, resolved_first_call, llm_guidance
FROM customers
WHERE grade = 'VIP'
LIMIT 5;

-- 8.2 다빈도 고객 샘플
SELECT id, name, grade, total_consultations, resolved_first_call,
       ROUND(resolved_first_call::numeric / NULLIF(total_consultations, 0) * 100, 1) as fcr_rate
FROM customers
WHERE total_consultations >= 10
ORDER BY total_consultations DESC
LIMIT 10;

-- 8.3 상담 연결 확인
SELECT
    c.id as consultation_id,
    c.customer_id,
    cu.name as customer_name,
    cu.grade,
    c."category_raw",
    c.call_date,
    c.fcr
FROM consultations c
JOIN customers cu ON c.customer_id = cu.id
WHERE c.call_date IS NOT NULL
ORDER BY c.call_date DESC
LIMIT 10;

-- 9. 카드 타입 분포
-- ==============================
SELECT
    card_type,
    COUNT(*) as count,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM customers) * 100, 1) as pct
FROM customers
GROUP BY card_type
ORDER BY count DESC;

-- 10. LLM 가이던스 샘플
-- ==============================
SELECT
    id,
    name,
    personality_tags,
    communication_style,
    llm_guidance
FROM customers
WHERE array_length(personality_tags, 1) > 0
ORDER BY random()
LIMIT 5;
