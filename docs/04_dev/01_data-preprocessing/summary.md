### 5. DATA-010

- 저장 형식: JSON
- 저장 환경: 로컬 서버
- 데이터 구조

```json
# 형식 (VectorDB용)
{
    "id": "hana_consultation_{source_id}",
    "consultation_id": "CS-HANA-{source_id}",
    "document_type": "consultation_transcript",
    "title": "{category} 상담",
    "content": "전처리된 상담 대화 내용 ([타입#번호] 형식 태그)",
    "metadata": {
        "source_id": "21749",
        "category": "교육비자동납부",
        "keywords": ["카드", "교육비", "자동납부"],
        "slot_types": ["상담원명", "고객명", "초등학교명"],
        "scenario_tags": ["자동납부신청", "본인확인"],
        "summary": null,
        "created_at": "2025-01-06T23:45:00.000Z"
    }
}

# 형식 (RDB용)
{
    "id": "hana_consultation_{source_id}",
    "source_id": "21749",
    "consulting_category": "교육비자동납부",
    "status": "완료",
    "client_id": "HANA_CLT_a3f5b2c1",
    "client_name": "[고객명#1]",
    "client_phone": "[전화번호#1]",
    "client_gender": "여자",
    "client_age": "50대",
    "call_duration": 166,
    "consulting_turns": 37,
    "keywords": "카드,교육비,자동납부"
}
    
# 예시 (VectorDB용)
{
    "id": "hana_consultation_20593",
    "consultation_id": "CS-HANA-20593",
    "document_type": "consultation_transcript",
    "title": "도난/분실 신청/해제 상담",
    "content": "상담사: 상담원 [상담원명#1]입니다.\n손님: 저 [카드사명#1]카드 문의좀 드릴려고요.\n상담사: 고객님. 그럼 본인 확인 후 안내를 해드리겠습니다. 고객님 성함과 생년월일 말씀해 주시겠어요?\n손님: [고객명#1]이고요, [생년월일#1]요.",
    "metadata": {
        "source_id": "20593",
        "category": "도난/분실 신청/해제",
        "keywords": ["카드", "결제", "발급"],
        "slot_types": ["상담원명", "고객명", "카드사명", "생년월일"],
        "scenario_tags": ["본인확인", "카드교체발급"],
        "summary": null,
        "created_at": "2025-01-06T23:45:00.000Z"
    }
}

# 예시 (RDB용)
{
    "id": "hana_consultation_20593",
    "source_id": "20593",
    "consulting_category": "도난/분실 신청/해제",
    "status": "완료",
    "client_id": "HANA_CLT_82d857dd",
    "client_name": "[고객명#1]",
    "client_phone": "[전화번호#1]",
    "client_gender": "여자",
    "client_age": "50대",
    "call_duration": 166,
    "consulting_turns": 37,
    "keywords": "도난/분실 신청/해제,카드,결제,발급,이용"
}
```
- 데이터 정제 및 전처리
- 마스킹 기호 통일화
    - 예) `▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲` → `[카드번호#1]`
    - 예) `▲▲▲▲▲▲▲▲▲▲▲` → `[전화번호#1]`
    - 예) `▲▲▲초등학교` → `[초등학교명#1]`
    - 예) `▲▲▲` → `[고객명#1]` (문맥 기반)
- 불용어 처리
    - 반복 불용어 축소: `네 네 네.` → `네.`, `그 그` → `그`, `아 아` → `아`
    - 구두점 정리: `네.,` → `네.`
- LLM 기반 문맥 태깅
    - 정규식으로 처리 불가능한 마스킹을 문맥 분석하여 적절한 태그로 변환
    - 동일 개체는 동일 번호 유지 (Entity Tracking)
    - 예: 손님이 말한 이름과 상담사가 확인한 이름은 같은 번호 사용

```json
# 예시 (VectorDB용)
{
    "id": "hana_consultation_20593",
    "consultation_id": "CS-HANA-20593",
    "document_type": "consultation_transcript",
    "title": "도난/분실 신청/해제 상담",
    "content": "상담사: 상담원 [상담원명#1]입니다.\n손님: 저 [카드사명#1]카드 문의좀 드릴려고요.\n상담사: 고객님. 그럼 본인 확인 후 안내를 해드리겠습니다. 고객님 성함과 생년월일 말씀해 주시겠어요?\n손님: [고객명#1]이고요, [생년월일#1]요.",
    "metadata": {
        "source_id": "20593",
        "category": "도난/분실 신청/해제",
        "keywords": ["카드", "결제", "발급"],
        "slot_types": ["상담원명", "고객명", "카드사명", "생년월일"],
        "scenario_tags": ["본인확인", "카드교체발급"],
        "summary": null,
        "created_at": "2025-01-06T23:45:00.000Z"
    }
}

# 예시 (RDB용)
{
    "id": "hana_consultation_20593",
    "source_id": "20593",
    "consulting_category": "도난/분실 신청/해제",
    "status": "완료",
    "client_id": "HANA_CLT_82d857dd",
    "client_name": "[고객명#1]",
    "client_phone": "[전화번호#1]",
    "client_gender": "여자",
    "client_age": "50대",
    "call_duration": 166,
    "consulting_turns": 37,
    "keywords": "도난/분실 신청/해제,카드,결제,발급,이용"
}
```
- 데이터 정제 및 전처리
    - 마스킹 기호 통일화
        - 예) ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ → [카드번호#1]
        - 예) ▲▲▲▲▲▲▲▲▲▲▲ → [전화번호#1]
        - 예) ▲▲▲초등학교 → [초등학교명#1]
        - 예) ▲▲▲ → [고객명#1] (문맥 기반)
    - 불용어 처리
        - 반복 불용어 축소: 네 네 네. → 네., 그 그 → 그, 아 아 → 아
        - 구두점 정리: 네., → 네.
    - LLM 기반 문맥 태깅
        - 정규식으로 처리 불가능한 마스킹을 문맥 분석하여 적절한 태그로 변환
        - 동일 개체는 동일 번호 유지 (Entity Tracking)
        - 예: 손님이 말한 이름과 상담사가 확인한 이름은 같은 번호 사용