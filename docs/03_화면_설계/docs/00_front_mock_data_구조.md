## 📊 CALL:ACT 실시간 상담 페이지 Mock 데이터 구조

#### 1. 고객 정보 (customerInfo)
```json
{
  "id": "CUST-001",
  "name": "홍길동",
  "phone": "010-1234-5678",
  "birthDate": "1985-03-15",
  "address": "서울시 강남구 테헤란로 123"
}
```
- 용도: 좌측 사이드바에 고객 정보 표시
- 필드: 고객 ID, 이름, 전화번호, 생년월일, 주소

#### 2. 최근 상담 내역 (recentConsultations)
```json
[
  {
    "id": 1,
    "title": "카드 재발급 문의",
    "date": "2025-01-03 10:30",
    "category": "카드분실",
    "status": "완료"
  },
  {
    "id": 2,
    "title": "해외 결제 문의",
    "date": "2024-12-28 14:20",
    "category": "해외결제",
    "status": "진행중"
  },
  {
    "id": 3,
    "title": "수수료 환불 요청",
    "date": "2024-12-20 09:15",
    "category": "수수료문의",
    "status": "완료"
  }
]
```
- 용도: 좌측 사이드바에 최근 상담 이력 표시
- 필드: ID, 제목, 날짜, 카테고리, 상태

#### 3. STT 키워드 (sttKeywords)
```text
["카드분실", "해외결제", "수수료문의"]
```
- 용도: STT(음성→텍스트 변환) 결과로 추출된 핵심 키워드
- 역할: 이 키워드를 기반으로 RAG 시스템이 관련 문서를 자동 검색

#### 4. 현재 상황 칸반보드 (currentSituationCards) ⭐ 핵심!
```json
[
  {
    "id": 1,
    "title": "카드 분실 신고 처리 절차",
    "keywords": ["##분실신고", "##즉시정지", "##재발급"],
    "content": "고객의 카드 분실 신고를 접수하고 즉시 카드 사용을 정지합니다. 고객 확인 후 재발급 절차를 진행하며..."
  },
  {
    "id": 2,
    "title": "긴급 카드 정지 안내",
    "keywords": ["##긴급처리", "##즉시정지"],
    "content": "카드 분실 시 즉시 사용 정지가 가능합니다. 시스템에서 자동으로 처리되며, 부정 사용 방지를 위해..."
  }
]
```
- 용도: STT 키워드를 기반으로 현재 상황에 관련된 문서를 실시간 표시
- 필드:
    - `id`: 카드 고유 번호
    - `title`: 문서 제목
    - `keywords`: 해시태그 형태의 핵심 키워드 배열
    - `content`: 문서 내용 (상담사가 참고할 정보)

#### 5. 다음 단계 칸반보드 (nextStepCards) ⭐ 핵심!
```json
[
  {
    "id": 1,
    "title": "재발급 카드 배송 안내",
    "keywords": ["##배송", "##3-5일", "##주소확인"],
    "content": "재발급 카드는 등록된 주소로 3-5일 내 배송됩니다. 고객에게 배송 추적 정보를 제공하고..."
  },
  {
    "id": 2,
    "title": "분실 카드 부정 사용 보상",
    "keywords": ["##보상", "##부정사용", "##보험"],
    "content": "분실 신고 후 발생한 부정 사용에 대해서는 보험 처리가 가능합니다. 고객에게 보상 절차를 안내..."
  }
]
```
- 용도: STT 키워드를 기반으로 다음 단계에 필요한 정보를 선제적 표시
- 필드: currentSituationCards와 동일 구조

#### 6. 권장 안내 멘트 (guidanceScript)
```text
"고객님, 카드 분실 신고 접수되었습니다. 즉시 카드 사용이 정지되며, 3-5일 내 재발급 카드가 등록된 주소로 배송됩니다."
```
- 용도: AI가 생성한 권장 상담 스크립트
- 기능: 복사 버튼으로 클립보드 복사 가능

#### 7. 채팅 메시지 (ChatMessage Interface)
```json
interface ChatMessage {
  id: number;
  type: 'user' | 'ai';
  text: string;
  timestamp: string;
}
```
- 용도: 우측 AI 검색 어시스턴트의 채팅 메시지
- 필드:
- id: 메시지 고유 번호
    - type: 사용자('user') 또는 AI('ai')
    - text: 메시지 내용
    - timestamp: 시간 (예: "14:32")
#### 🔄 데이터 흐름 (STT + RAG 연동 구조)
```text
1. 고객 전화 인입
   ↓
2. STT 시스템: 음성 → 텍스트 변환
   ↓
3. 키워드 추출: ["카드분실", "해외결제", "수수료문의"]
   ↓
4. RAG 검색: 키워드 기반으로 문서 DB 검색
   ↓
5. 칸반보드 표시:
   - 현재 상황 관련 정보 (currentSituationCards)
   - 다음 단계 예상 정보 (nextStepCards)
   ↓
6. 상담사: 칸반보드 카드 참고하여 상담 진행
```

#### 💡 실제 운영 시 백엔드 연동 구조 (예상)
```json
// API 요청 예시
POST /api/consultation/search
{
  "sttKeywords": ["카드분실", "해외결제"],
  "customerId": "CUST-001"
}

// API 응답 예시
{
  "currentSituation": [
    { "id": 1, "title": "...", "keywords": [...], "content": "..." }
  ],
  "nextStep": [
    { "id": 1, "title": "...", "keywords": [...], "content": "..." }
  ],
  "guidanceScript": "고객님, ..."
}
```

이 구조를 통해 실시간으로 RAG 기반 문서 검색 결과를 칸반보드에 표시하여 상담사를 지원합니다!