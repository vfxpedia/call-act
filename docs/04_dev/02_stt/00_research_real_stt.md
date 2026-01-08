CALL-ACT 프로젝트 실시간 키워드 추출 → DB 검색 파이프라인을 설계

## 핵심 아키텍처

```
[고객 음성] → [실시간 STT] → [키워드 추출] → [DB 검색] → [상담사 화면]
                ↓
           Streaming ASR
```

## 1. 실시간 STT 옵션 비교

| 모델/서비스 | 지연시간 | 한국어 | 실시간 스트리밍 | 추천도 |
|------------|---------|--------|----------------|--------|
| **faster-whisper** | ~200ms | ⭐⭐⭐ | VAD로 구현 | ⭐⭐⭐⭐ |
| **Deepgram** | ~100ms | ⭐⭐ | ✅ 네이티브 | ⭐⭐⭐ |
| **Google STT Streaming** | ~150ms | ⭐⭐⭐⭐ | ✅ 네이티브 | ⭐⭐⭐⭐⭐ |
| **CLOVA Speech** | ~200ms | ⭐⭐⭐⭐⭐ | ✅ | ⭐⭐⭐⭐ |
| whisper (원본) | ~1-3초 | ⭐⭐⭐ | ❌ 배치만 | ⭐⭐ |

**추천**: 한국어 카드 상담이라면 **Google STT Streaming** 또는 **CLOVA Speech**

---

## 2. 실시간 키워드 추출 전략

카드 상담은 도메인이 명확하니까 **사전 기반 + 패턴 매칭**이 가장 빠르고 정확해요:

```python
# keyword_extractor.py
import re
from typing import List, Dict, Set
from collections import defaultdict

class CardServiceKeywordExtractor:
    def __init__(self):
        # 카드 상담 키워드 사전 (카테고리별)
        self.keyword_dict = {
            "카드종류": ["신용카드", "체크카드", "법인카드", "기프트카드", "선불카드"],
            "결제": ["결제", "승인", "취소", "환불", "거절", "한도", "일시불", "할부", "리볼빙"],
            "포인트": ["포인트", "마일리지", "캐시백", "적립", "사용", "소멸", "전환"],
            "분실도난": ["분실", "도난", "재발급", "정지", "해지", "차단"],
            "연체": ["연체", "이자", "수수료", "납부", "청구서", "명세서"],
            "혜택": ["할인", "무이자", "프로모션", "이벤트", "제휴", "특별"],
            "본인확인": ["비밀번호", "CVC", "유효기간", "본인확인", "인증"],
            "해외": ["해외", "환전", "달러", "엔화", "원화"],
        }
        
        # 검색용 역인덱스 생성 (O(1) 룩업)
        self.keyword_to_category = {}
        for category, keywords in self.keyword_dict.items():
            for kw in keywords:
                self.keyword_to_category[kw] = category
        
        # 정규식 패턴 (한 번만 컴파일)
        all_keywords = "|".join(self.keyword_to_category.keys())
        self.pattern = re.compile(f"({all_keywords})")
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """실시간 텍스트에서 키워드 추출 - 매우 빠름"""
        results = defaultdict(list)
        
        for match in self.pattern.finditer(text):
            keyword = match.group()
            category = self.keyword_to_category[keyword]
            if keyword not in results[category]:
                results[category].append(keyword)
        
        return dict(results)
    
    def extract_with_context(self, text: str, window: int = 10) -> List[Dict]:
        """키워드 + 주변 문맥 추출 (검색 정확도 향상)"""
        results = []
        for match in self.pattern.finditer(text):
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            results.append({
                "keyword": match.group(),
                "category": self.keyword_to_category[match.group()],
                "context": text[start:end],
                "position": match.start()
            })
        return results


# 사용 예시
extractor = CardServiceKeywordExtractor()
text = "신용카드 해외결제 한도가 얼마인지 알고 싶어요. 포인트 적립도 되나요?"
print(extractor.extract(text))
# {'카드종류': ['신용카드'], '결제': ['결제', '한도'], '해외': ['해외'], '포인트': ['포인트', '적립']}
```

---

## 3. 실시간 파이프라인 (faster-whisper + 키워드 추출)

```python
# realtime_pipeline.py
import asyncio
import json
from faster_whisper import WhisperModel
from keyword_extractor import CardServiceKeywordExtractor
import sounddevice as sd
import numpy as np
from collections import deque

class RealtimeCardAssistant:
    def __init__(self, db_searcher):
        # STT 모델 (small이 속도/정확도 균형 좋음)
        self.whisper = WhisperModel("small", device="cuda", compute_type="float16")
        self.extractor = CardServiceKeywordExtractor()
        self.db_searcher = db_searcher  # 기존 RAG 시스템
        
        # 오디오 버퍼 (VAD용)
        self.audio_buffer = deque(maxlen=16000 * 3)  # 3초 버퍼
        self.detected_keywords = {}
        self.keyword_history = []
        
    async def process_audio_chunk(self, audio_chunk: np.ndarray):
        """오디오 청크 처리 (실시간)"""
        self.audio_buffer.extend(audio_chunk)
        
        # 일정량 모이면 transcribe
        if len(self.audio_buffer) >= 16000 * 1.5:  # 1.5초
            audio_array = np.array(self.audio_buffer)
            
            # STT (비동기로 처리)
            segments, _ = self.whisper.transcribe(
                audio_array, 
                language="ko",
                vad_filter=True,  # 음성 구간만 처리
                vad_parameters=dict(min_silence_duration_ms=300)
            )
            
            text = " ".join([seg.text for seg in segments])
            
            if text.strip():
                # 키워드 추출
                keywords = self.extractor.extract_with_context(text)
                
                if keywords:
                    await self.on_keywords_detected(keywords, text)
            
            # 버퍼 절반 비우기 (오버랩 유지)
            for _ in range(len(self.audio_buffer) // 2):
                self.audio_buffer.popleft()
    
    async def on_keywords_detected(self, keywords: list, full_text: str):
        """키워드 감지 시 DB 검색 트리거"""
        # 새 키워드만 필터링 (중복 방지)
        new_keywords = [
            kw for kw in keywords 
            if kw['keyword'] not in self.detected_keywords
        ]
        
        if new_keywords:
            # 키워드 기록
            for kw in new_keywords:
                self.detected_keywords[kw['keyword']] = kw
            
            # 검색 쿼리 생성
            search_query = " ".join([kw['context'] for kw in new_keywords])
            
            # DB 검색 (기존 RAG 시스템 활용)
            results = await self.db_searcher.search(search_query)
            
            # 상담사 화면에 전송
            await self.send_to_agent_screen({
                "type": "keyword_detected",
                "keywords": new_keywords,
                "transcript": full_text,
                "search_results": results,
                "timestamp": asyncio.get_event_loop().time()
            })
    
    async def send_to_agent_screen(self, data: dict):
        """WebSocket으로 상담사 화면에 실시간 전송"""
        # 실제 구현에서는 WebSocket 연결
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 키워드 히스토리 저장
        self.keyword_history.append(data)
    
    def get_session_summary(self) -> dict:
        """통화 종료 시 요약"""
        return {
            "total_keywords": list(self.detected_keywords.keys()),
            "categories": list(set(kw['category'] for kw in self.detected_keywords.values())),
            "history": self.keyword_history
        }
```

---

## 4. 더 빠른 대안: 스트리밍 STT API 사용

**Google Cloud Speech-to-Text Streaming** (가장 안정적):

```python
# google_streaming_stt.py
from google.cloud import speech
import pyaudio
import queue
import threading

class GoogleStreamingSTT:
    def __init__(self, keyword_callback):
        self.client = speech.SpeechClient()
        self.keyword_callback = keyword_callback
        self.extractor = CardServiceKeywordExtractor()
        
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="ko-KR",
            enable_automatic_punctuation=True,
            model="phone_call",  # 전화 통화 최적화 모델!
        )
        
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True,  # 중간 결과도 받기 (더 빠른 반응)
        )
    
    def process_responses(self, responses):
        for response in responses:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                is_final = result.is_final
                
                # 중간 결과에서도 키워드 추출 (초저지연)
                keywords = self.extractor.extract(transcript)
                
                if keywords:
                    self.keyword_callback(
                        keywords=keywords,
                        transcript=transcript,
                        is_final=is_final
                    )
    
    def start_streaming(self, audio_generator):
        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk)
            for chunk in audio_generator
        )
        
        responses = self.client.streaming_recognize(
            self.streaming_config, 
            requests
        )
        
        self.process_responses(responses)
```

---

## 5. 전체 시스템 구성도

```
┌─────────────────────────────────────────────────────────────┐
│                    실시간 상담 지원 시스템                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [고객 전화] ──→ [PBX/CTI] ──→ [오디오 스트림]                │
│                                      │                      │
│                                      ▼                      │
│                    ┌─────────────────────────────┐          │
│                    │   Streaming STT             │          │
│                    │   (Google/CLOVA)            │          │
│                    │   ~100-200ms 지연           │          │
│                    └──────────┬──────────────────┘          │
│                               │                             │
│                               ▼                             │
│                    ┌─────────────────────────────┐          │
│                    │   Keyword Extractor         │          │
│                    │   (사전 기반, <1ms)          │          │
│                    └──────────┬──────────────────┘          │
│                               │                             │
│                               ▼                             │
│                    ┌─────────────────────────────┐          │
│                    │   RAG Search (ChromaDB)     │          │
│                    │   ~50-100ms                 │          │
│                    └──────────┬──────────────────┘          │
│                               │                             │
│                               ▼                             │
│                    ┌─────────────────────────────┐          │
│  [상담사 화면] ◀── │   WebSocket Server          │          │
│                    │   실시간 푸시                │          │
│                    └─────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘

총 지연시간: 약 200-400ms (거의 실시간!)
```

---

## 추천 접근 방식

**Phase 1 (MVP - 빠르게 검증):**
1. **Google STT Streaming** + **사전 기반 키워드 추출**
2. 기존 ChromaDB RAG 시스템 연동
3. 간단한 WebSocket으로 상담사 화면 연결

**Phase 2 (고도화):**
1. 키워드 사전 확장 (실제 상담 로그 분석)
2. 의도(Intent) 분류 추가 (문의/불만/요청 등)
3. 키워드 가중치 적용 (중요도에 따라)

## 핵심 문제: "어디서 끊을 것인가?"

```
실시간 음성 스트림:
"신용카..." → "신용카드 해외..." → "신용카드 해외결제 한도가..." → "...알고 싶어요"
     ↑              ↑                      ↑                           ↑
   여기서 끊으면?  여기서?              여기서?                    여기가 맞음!
```

---

## 끊는 전략 3가지

### 1. **VAD (Voice Activity Detection) - 침묵 기반**

가장 일반적. "말이 멈추면 끊는다"

```python
# 침묵 감지로 발화 단위 분리
from silero_vad import load_silero_vad, get_speech_timestamps

class VADBasedSegmenter:
    def __init__(self):
        self.vad_model = load_silero_vad()
        self.buffer = []
        self.silence_threshold_ms = 500  # 0.5초 침묵이면 끊기
        
    def process_chunk(self, audio_chunk):
        speech_timestamps = get_speech_timestamps(
            audio_chunk, 
            self.vad_model,
            threshold=0.5,
            min_silence_duration_ms=self.silence_threshold_ms
        )
        
        # 침묵 구간 감지되면 → 여기서 끊어서 처리!
        if self._detected_end_of_speech(speech_timestamps):
            complete_utterance = self.flush_buffer()
            return complete_utterance  # 이걸 키워드 추출로
        
        return None
```

**장점**: 자연스러운 발화 단위
**단점**: 말 빠른 사람, 더듬는 사람 처리 어려움

---

### 2. **Streaming STT의 `is_final` 활용**

STT 엔진이 "문장 끝났다"고 판단해주는 것 활용

```python
# Google STT Streaming의 is_final 활용
def on_streaming_result(result):
    transcript = result.alternatives[0].transcript
    
    if result.is_final:  # ← STT가 "이 문장 끝났어"라고 판단
        # 여기서 키워드 추출!
        keywords = extractor.extract(transcript)
        trigger_db_search(keywords)
    else:
        # 중간 결과 - 화면에 실시간 표시만
        update_live_transcript(transcript)
```

```
타임라인 예시:
t=0.0s  interim: "신용"
t=0.3s  interim: "신용카드"
t=0.6s  interim: "신용카드 해외"
t=1.0s  interim: "신용카드 해외결제 한도가"
t=1.5s  interim: "신용카드 해외결제 한도가 얼마인지"
t=2.0s  FINAL:   "신용카드 해외결제 한도가 얼마인지 알고 싶어요"  ← 여기서 처리!
t=2.3s  interim: "포인트"
t=2.8s  FINAL:   "포인트 적립도 되나요"  ← 여기서 처리!
```

**장점**: STT가 언어학적으로 판단해줌 (문법적 완결성)
**단점**: STT 서비스에 의존적

---

### 3. **하이브리드: 조기 감지 + 최종 확정** ⭐ 추천

실시간성을 위해 **"빠른 힌트"** + **"정확한 확정"** 2단계로:

```python
class HybridSegmenter:
    def __init__(self):
        self.extractor = CardServiceKeywordExtractor()
        self.pending_keywords = set()  # 감지했지만 아직 미확정
        self.confirmed_keywords = set()  # 확정된 키워드
        
    def on_interim_result(self, interim_text: str):
        """중간 결과에서 키워드 "미리" 감지 (빠른 힌트)"""
        keywords = self.extractor.extract(interim_text)
        
        for kw in keywords:
            if kw not in self.confirmed_keywords:
                self.pending_keywords.add(kw)
                # 미리 DB 검색 시작 (prefetch)
                self.prefetch_search(kw)
    
    def on_final_result(self, final_text: str):
        """최종 결과에서 확정 + 화면에 표시"""
        keywords = self.extractor.extract(final_text)
        
        new_confirmed = set(keywords) - self.confirmed_keywords
        self.confirmed_keywords.update(new_confirmed)
        
        # prefetch 해둔 결과 있으면 즉시 표시
        # 없으면 이제 검색
        self.show_results(new_confirmed, final_text)
    
    def prefetch_search(self, keyword: str):
        """백그라운드에서 미리 검색해두기"""
        # 비동기로 검색 시작, 결과는 캐시에 저장
        asyncio.create_task(self.db_searcher.search_and_cache(keyword))
```

```
타임라인:
t=0.6s  interim "신용카드 해외" → "신용카드", "해외" 감지 → prefetch 시작
t=1.0s  interim "...한도가" → "한도" 감지 → prefetch 시작
t=2.0s  FINAL → 확정! → prefetch 결과 즉시 표시 (이미 준비됨!)

결과: 체감 지연시간 대폭 감소
```

---

## 실제 구현 예시

```python
import asyncio
from dataclasses import dataclass
from typing import Optional, Callable
from collections import deque

@dataclass
class SegmentResult:
    text: str
    is_final: bool
    keywords: list
    confidence: float

class RealtimeUtteranceProcessor:
    """실시간 발화 처리기 - 끊기 로직의 핵심"""
    
    def __init__(
        self,
        on_keyword_detected: Callable,  # 키워드 감지 시 콜백
        on_utterance_complete: Callable,  # 발화 완료 시 콜백
        silence_threshold_ms: int = 500,
        max_utterance_ms: int = 10000,  # 최대 10초면 강제로 끊기
    ):
        self.on_keyword_detected = on_keyword_detected
        self.on_utterance_complete = on_utterance_complete
        self.silence_threshold_ms = silence_threshold_ms
        self.max_utterance_ms = max_utterance_ms
        
        self.extractor = CardServiceKeywordExtractor()
        self.current_utterance = ""
        self.detected_in_current = set()
        self.last_speech_time = None
        self.utterance_start_time = None
        
    async def process_stt_result(
        self, 
        text: str, 
        is_final: bool, 
        timestamp: float
    ):
        """STT 결과 처리 - 핵심 로직"""
        
        # 1. 새 발화 시작 체크
        if self.utterance_start_time is None:
            self.utterance_start_time = timestamp
        
        # 2. 중간 결과에서 키워드 조기 감지
        if not is_final:
            new_keywords = self._extract_new_keywords(text)
            if new_keywords:
                # 즉시 알림! (prefetch용)
                await self.on_keyword_detected(
                    keywords=new_keywords,
                    text=text,
                    is_final=False,
                    action="prefetch"
                )
        
        # 3. 최종 결과 → 발화 단위 완료
        if is_final:
            all_keywords = self.extractor.extract(text)
            
            await self.on_utterance_complete(
                text=text,
                keywords=all_keywords,
                duration_ms=(timestamp - self.utterance_start_time) * 1000
            )
            
            # 상태 리셋
            self._reset_utterance()
        
        # 4. 너무 길면 강제 끊기
        elif self._should_force_segment(timestamp):
            await self._force_segment(text, timestamp)
        
        self.last_speech_time = timestamp
    
    def _extract_new_keywords(self, text: str) -> list:
        """이번 발화에서 아직 감지 안 된 새 키워드만"""
        all_kw = set(self.extractor.extract(text).keys())
        new_kw = all_kw - self.detected_in_current
        self.detected_in_current.update(new_kw)
        return list(new_kw)
    
    def _should_force_segment(self, current_time: float) -> bool:
        """강제로 끊어야 하는지 체크"""
        if self.utterance_start_time is None:
            return False
        duration = (current_time - self.utterance_start_time) * 1000
        return duration > self.max_utterance_ms
    
    async def _force_segment(self, text: str, timestamp: float):
        """너무 긴 발화 강제 분리"""
        await self.on_utterance_complete(
            text=text,
            keywords=list(self.detected_in_current),
            duration_ms=self.max_utterance_ms,
            forced=True
        )
        self._reset_utterance()
    
    def _reset_utterance(self):
        """발화 상태 리셋"""
        self.current_utterance = ""
        self.detected_in_current = set()
        self.utterance_start_time = None


# 사용 예시
async def main():
    async def on_keyword(keywords, text, is_final, action):
        print(f"[{action}] 키워드 감지: {keywords}")
        if action == "prefetch":
            # 미리 DB 검색 시작
            pass
    
    async def on_complete(text, keywords, duration_ms, forced=False):
        print(f"[완료] {text}")
        print(f"  키워드: {keywords}")
        print(f"  소요: {duration_ms}ms, 강제끊기: {forced}")
        # 여기서 최종 DB 검색 & 화면 표시
    
    processor = RealtimeUtteranceProcessor(
        on_keyword_detected=on_keyword,
        on_utterance_complete=on_complete
    )
    
    # 시뮬레이션: STT 결과가 들어오는 상황
    await processor.process_stt_result("신용카드", False, 0.3)
    await processor.process_stt_result("신용카드 해외결제", False, 0.6)
    await processor.process_stt_result("신용카드 해외결제 한도가 얼마인지 알고 싶어요", True, 2.0)
```

---

## 요약: 끊기 전략 선택 가이드

| 상황 | 추천 전략 |
|-----|----------|
| STT 서비스 사용 (Google, CLOVA) | `is_final` 활용 |
| 로컬 Whisper 사용 | VAD (Silero) |
| 최고의 반응속도 필요 | 하이브리드 (interim + prefetch) |
| 단순 구현 우선 | 시간 기반 (매 2초) |

CALL-ACT 프로젝트에는 **하이브리드 방식 + Google STT의 `is_final`** 조합을 추천
상담 품질이 중요하니까요!

이 끊기 로직을 기반으로 전체 파이프라인 코드를 짜볼까요?

정확해! 이게 실제 운영에서 가장 고민되는 부분이야. 정리해볼게.

## 문제 상황 예시

```
고객: "해외에서 카드가 안 돼요. 한도는 남아있는데..."

필요한 정보:
├─ 카드 정보 DB: 해외결제 한도, 해외사용 설정 여부
├─ 이용 안내 DB: 해외결제 차단 해제 방법, 최근 해외결제 관련 공지
└─ 상담 사례 DB: 유사 케이스 해결 사례, 자주 발생하는 원인
```

---

## 멀티 DB 검색 전략

### 전략 1: 병렬 검색 (Fan-out) - 단순하지만 효과적

```python
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class DBType(Enum):
    CARD_INFO = "card_info"        # 카드 정보
    SERVICE_GUIDE = "service_guide" # 이용 안내
    CASE_HISTORY = "case_history"   # 상담 사례

@dataclass
class SearchResult:
    db_type: DBType
    content: str
    score: float
    metadata: dict

class MultiDBSearcher:
    """3개 DB 병렬 검색"""
    
    def __init__(self, card_db, guide_db, case_db):
        self.databases = {
            DBType.CARD_INFO: card_db,
            DBType.SERVICE_GUIDE: guide_db,
            DBType.CASE_HISTORY: case_db,
        }
    
    async def search_all(
        self, 
        query: str, 
        top_k: int = 3
    ) -> Dict[DBType, List[SearchResult]]:
        """모든 DB에 동시 검색"""
        
        tasks = {
            db_type: asyncio.create_task(
                db.search(query, top_k=top_k)
            )
            for db_type, db in self.databases.items()
        }
        
        results = {}
        for db_type, task in tasks.items():
            try:
                results[db_type] = await asyncio.wait_for(task, timeout=0.5)
            except asyncio.TimeoutError:
                results[db_type] = []  # 타임아웃 시 빈 결과
        
        return results
```

**장점**: 구현 간단, 항상 모든 정보 제공
**단점**: 불필요한 검색, 노이즈 많을 수 있음

---

### 전략 2: 의도 기반 라우팅 ⭐ 추천

키워드/의도에 따라 **어떤 DB를 검색할지** 먼저 결정:

```python
from typing import Set

class IntentBasedRouter:
    """의도 분석 → DB 라우팅"""
    
    def __init__(self):
        # 키워드 → DB 매핑 규칙
        self.routing_rules = {
            # 카드 정보 DB 트리거
            DBType.CARD_INFO: {
                "keywords": ["한도", "혜택", "포인트", "적립", "수수료", "이자", 
                            "연회비", "캐시백", "마일리지", "할부", "결제일"],
                "intents": ["상품문의", "혜택문의", "한도문의"]
            },
            # 이용 안내 DB 트리거  
            DBType.SERVICE_GUIDE: {
                "keywords": ["방법", "어떻게", "설정", "변경", "신청", "등록",
                            "해지", "분실", "재발급", "비밀번호", "공지"],
                "intents": ["절차문의", "방법문의", "설정문의"]
            },
            # 상담 사례 DB 트리거
            DBType.CASE_HISTORY: {
                "keywords": ["안돼요", "오류", "실패", "거절", "왜", "문제",
                            "이상", "갑자기", "원래", "다른사람"],
                "intents": ["문제해결", "오류문의", "불만"]
            }
        }
        
        # 복합 시나리오 (여러 DB 필요)
        self.compound_scenarios = {
            "해외결제불가": [DBType.CARD_INFO, DBType.SERVICE_GUIDE, DBType.CASE_HISTORY],
            "카드분실": [DBType.SERVICE_GUIDE, DBType.CARD_INFO, DBType.CASE_HISTORY],
            "포인트전환": [DBType.CARD_INFO, DBType.SERVICE_GUIDE],
            "한도증액": [DBType.CARD_INFO, DBType.SERVICE_GUIDE, DBType.CASE_HISTORY],
        }
    
    def route(self, text: str, keywords: List[str]) -> List[DBType]:
        """어떤 DB를 검색할지 결정"""
        
        # 1. 복합 시나리오 체크
        scenario = self._detect_compound_scenario(text, keywords)
        if scenario:
            return self.compound_scenarios[scenario]
        
        # 2. 키워드 기반 라우팅
        target_dbs = set()
        
        for db_type, rules in self.routing_rules.items():
            for kw in keywords:
                if kw in rules["keywords"]:
                    target_dbs.add(db_type)
                    break
        
        # 3. 기본값: 최소 1개는 검색
        if not target_dbs:
            target_dbs.add(DBType.CARD_INFO)  # 기본
        
        return list(target_dbs)
    
    def _detect_compound_scenario(self, text: str, keywords: List[str]) -> Optional[str]:
        """복합 시나리오 감지"""
        
        # 해외 + (안됨/오류/거절) → 해외결제불가
        if "해외" in keywords and any(k in keywords for k in ["안", "오류", "거절", "실패"]):
            return "해외결제불가"
        
        # 분실/도난 → 카드분실
        if any(k in keywords for k in ["분실", "도난", "잃어버"]):
            return "카드분실"
        
        # 포인트 + 전환/교환 → 포인트전환
        if "포인트" in keywords and any(k in keywords for k in ["전환", "교환", "바꾸"]):
            return "포인트전환"
        
        return None
```

---

### 전략 3: 계층적 검색 + 동적 확장

1차 검색 → 결과 부족하면 → 다른 DB로 확장

```python
class HierarchicalSearcher:
    """계층적 검색: 우선순위 기반 + 동적 확장"""
    
    def __init__(self, multi_db: MultiDBSearcher, router: IntentBasedRouter):
        self.multi_db = multi_db
        self.router = router
        self.min_results = 2  # 최소 결과 개수
        self.min_score = 0.7  # 최소 유사도
    
    async def search(
        self, 
        query: str, 
        keywords: List[str]
    ) -> Dict[DBType, List[SearchResult]]:
        
        # 1. 라우팅으로 우선 검색할 DB 결정
        primary_dbs = self.router.route(query, keywords)
        
        # 2. 우선 DB들 검색
        results = {}
        for db_type in primary_dbs:
            results[db_type] = await self.multi_db.databases[db_type].search(
                query, top_k=3
            )
        
        # 3. 결과 품질 체크 → 부족하면 확장
        if self._needs_expansion(results):
            secondary_dbs = self._get_secondary_dbs(primary_dbs)
            
            for db_type in secondary_dbs:
                results[db_type] = await self.multi_db.databases[db_type].search(
                    query, top_k=2
                )
        
        return results
    
    def _needs_expansion(self, results: Dict) -> bool:
        """결과가 충분한지 체크"""
        total_good_results = sum(
            1 for db_results in results.values()
            for r in db_results
            if r.score >= self.min_score
        )
        return total_good_results < self.min_results
    
    def _get_secondary_dbs(self, primary_dbs: List[DBType]) -> List[DBType]:
        """아직 검색 안 한 DB들"""
        all_dbs = set(DBType)
        return list(all_dbs - set(primary_dbs))
```

---

## 통합 아키텍처: 실시간 다중 DB 검색

```python
from dataclasses import dataclass, field
from typing import List, Dict, Callable
import asyncio

@dataclass
class AgentScreenUpdate:
    """상담사 화면에 보여줄 정보"""
    transcript: str
    keywords: List[str]
    
    # DB별 검색 결과
    card_info: List[dict] = field(default_factory=list)
    service_guide: List[dict] = field(default_factory=list)
    case_history: List[dict] = field(default_factory=list)
    
    # 메타 정보
    search_time_ms: float = 0
    scenario_detected: Optional[str] = None


class RealtimeMultiDBAssistant:
    """실시간 다중 DB 상담 지원 시스템"""
    
    def __init__(
        self,
        card_db,
        guide_db, 
        case_db,
        on_update: Callable[[AgentScreenUpdate], None]
    ):
        self.searcher = MultiDBSearcher(card_db, guide_db, case_db)
        self.router = IntentBasedRouter()
        self.extractor = CardServiceKeywordExtractor()
        self.on_update = on_update
        
        # 상태 관리
        self.session_keywords = set()
        self.session_results_cache = {}
        
    async def on_utterance(self, text: str, is_final: bool):
        """발화 처리 - 핵심 로직"""
        
        start_time = asyncio.get_event_loop().time()
        
        # 1. 키워드 추출
        extracted = self.extractor.extract(text)
        keywords = []
        for category, kws in extracted.items():
            keywords.extend(kws)
        
        # 2. 새 키워드만 필터링 (중복 검색 방지)
        new_keywords = [k for k in keywords if k not in self.session_keywords]
        
        if not new_keywords and not is_final:
            return  # 새 키워드 없으면 스킵
        
        self.session_keywords.update(new_keywords)
        
        # 3. 라우팅: 어떤 DB를 검색할지 결정
        target_dbs = self.router.route(text, keywords)
        scenario = self.router._detect_compound_scenario(text, keywords)
        
        # 4. 타겟 DB들 병렬 검색
        search_tasks = {}
        for db_type in target_dbs:
            # 캐시 체크
            cache_key = f"{db_type}:{text[:50]}"
            if cache_key in self.session_results_cache:
                continue
                
            search_tasks[db_type] = asyncio.create_task(
                self.searcher.databases[db_type].search(text, top_k=3)
            )
        
        # 5. 결과 수집
        results = {db_type: [] for db_type in DBType}
        
        for db_type, task in search_tasks.items():
            try:
                db_results = await asyncio.wait_for(task, timeout=0.3)
                results[db_type] = db_results
                
                # 캐시 저장
                cache_key = f"{db_type}:{text[:50]}"
                self.session_results_cache[cache_key] = db_results
            except asyncio.TimeoutError:
                pass  # 타임아웃은 무시
        
        # 6. 상담사 화면 업데이트
        elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
        
        update = AgentScreenUpdate(
            transcript=text,
            keywords=keywords,
            card_info=self._format_results(results[DBType.CARD_INFO]),
            service_guide=self._format_results(results[DBType.SERVICE_GUIDE]),
            case_history=self._format_results(results[DBType.CASE_HISTORY]),
            search_time_ms=elapsed,
            scenario_detected=scenario
        )
        
        await self.on_update(update)
    
    def _format_results(self, results: List[SearchResult]) -> List[dict]:
        """결과 포맷팅"""
        return [
            {
                "title": r.metadata.get("title", ""),
                "content": r.content[:200],  # 미리보기
                "score": round(r.score, 2),
                "link": r.metadata.get("link", "")
            }
            for r in results[:3]  # 상위 3개만
        ]
    
    def get_session_summary(self) -> dict:
        """통화 종료 시 요약"""
        return {
            "all_keywords": list(self.session_keywords),
            "scenarios_detected": [...],
            "dbs_searched": [...],
        }
```

---

## 상담사 화면 UI 구성

```
┌─────────────────────────────────────────────────────────────────┐
│  🎤 실시간 대화                                    [녹음중 ●]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  고객: "해외에서 카드가 안 돼요. 한도는 남아있는데..."              │
│                                                                 │
│  🏷️ 감지된 키워드: [해외] [카드] [한도] [안됨]                    │
│  📋 시나리오: 해외결제불가                                       │
│                                                                 │
├──────────────┬──────────────┬───────────────────────────────────┤
│  📦 카드 정보  │  📘 이용 안내  │  💬 상담 사례                  │
├──────────────┼──────────────┼───────────────────────────────────┤
│              │              │                                   │
│ ▸ 해외결제   │ ▸ 해외결제   │ ▸ [해결] 해외결제 거절               │
│   한도 조회  │   설정 방법  │   - 해외사용 설정 미등록             │
│   (98% 일치) │   (95% 일치) │   - 설정 후 정상 사용               │
│              │              │   (92% 일치)                       │
│ ▸ 해외결제   │ ▸ 해외이용   │                                     │
│   수수료     │   차단 해제  │ ▸ [해결] 한도 초과 오인              │
│   (85% 일치) │   (90% 일치) │   - 일시적 한도 소진                │
│              │              │   (88% 일치)                       │
│              │ ▸ [공지]     │                                    │
│              │   6월 해외   │                                    │
│              │   결제 점검  │                                    │
│              │   (87% 일치) │                                    │
│              │              │                                    │
└──────────────┴──────────────┴────────────────────────────────────┘
│                        [검색 소요: 180ms]                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 핵심 포인트 정리

| 고려사항 | 해결책 |
|---------|--------|
| 어떤 DB를 검색할지? | 의도 기반 라우팅 (키워드 → DB 매핑) |
| 다중 DB 동시 검색 속도? | 병렬 처리 + 타임아웃 |
| 복합 시나리오? | 시나리오 패턴 사전 정의 |
| 중복 검색 방지? | 세션 캐시 + 키워드 중복 체크 |
| 결과 우선순위? | 유사도 스코어 기반 정렬 |

이 구조로 가면 "해외결제 안됨" 같은 복합 케이스도 3개 DB에서 관련 정보를 빠르게 가져올 수 있어요.
