# M-1: STT 비교 테스트 계획서

> **작성**: AI/ML 팀장 (M)
> **작성일**: 2026-02-10
> **상태**: 계획 수립 완료 → 실행 대기
> **관련 문서**: `02_LEVEL02_DISCUSSION.md` Phase 3 M-1

---

## 1. 테스트 목적

실시간 상담 STT 엔진을 교체하여 **전사 정확도 향상 → 키워드 추출 품질 → RAG 검색 품질** 전체 체인 개선

### 현재 문제
- Whisper-1 전사 오류 → 잘못된 키워드 → 무관한 문서 검색
- 실시간 상담 중 짧은 발화(1-1.5초) 단위로 전사 → 문맥 없는 키워드 추출

---

## 2. 테스트 대상 엔진

| # | 엔진 | 타입 | 구현 상태 | 특징 |
|---|------|------|----------|------|
| A | **Whisper-1** (기준선) | OpenAI API | `stt_engine.py:86` ✅ | 프로덕션 사용중, 안정적 |
| B | **Qwen3-ASR 1.7B** | 로컬 HTTP (8104) | `stt_engine.py:151` ✅ | GPU 0, 빠른 속도 |
| C | **Faster-Whisper large-v3** | 로컬 모델 | `stt_engine.py:226` ✅ | GPU, 높은 정확도 기대 |
| D | **VibeVoice-ASR** | 로컬 모델 | `backend_dev/` 데모만 | 화자분리 내장, 60분 처리 |

---

## 3. 평가 기준

### 3.1 정량 지표

| 지표 | 설명 | 목표 |
|------|------|------|
| **WER** (Word Error Rate) | 단어 수준 오류율 | < 15% (현재 추정 20-30%) |
| **CER** (Character Error Rate) | 문자 수준 오류율 | < 10% |
| **RTF** (Real-Time Factor) | 처리시간/오디오시간 | < 0.3 (실시간) |
| **Latency** (첫 응답 시간) | 오디오 전송 → 텍스트 수신 | < 1.5초 |
| **키워드 정확도** | 전사 결과에서 올바른 키워드 추출 비율 | > 85% |

### 3.2 정성 지표

| 지표 | 설명 |
|------|------|
| **한국어 고유명사** | 카드명, 서비스명 정확도 (테디카드, 국민행복카드 등) |
| **숫자/날짜** | 금액, 날짜, 전화번호 전사 정확도 |
| **화자 분리** | 상담사/고객 구분 정확도 (VibeVoice만 내장) |
| **환경 소음 내성** | 배경 소음 환경에서의 전사 품질 |
| **할루시네이션** | 침묵 구간에서 잘못된 텍스트 생성 빈도 |

---

## 4. 테스트 데이터셋

### 4.1 기존 시나리오 오디오 (8개)

프로젝트에 이미 존재하는 시나리오:

| ID | 시나리오 | 난이도 | 예상 길이 |
|----|---------|--------|----------|
| scenario-1 | 부정 결제 문의 | 중 | ~120초 |
| scenario-2 | 카드 분실 신고 | 중 | ~115초 |
| scenario-3 | 연회비 문의 | 하 | ~90초 |
| scenario-4 | 포인트 적립/사용 | 중 | ~100초 |
| scenario-5 | 할부 변경 | 중 | ~95초 |
| scenario-6 | 한도 변경 | 하 | ~80초 |
| scenario-7 | 카드 재발급 | 하 | ~85초 |
| scenario-8 | 복합 문의 (다중 주제) | 상 | ~150초 |

### 4.2 추가 테스트 케이스

| 케이스 | 목적 |
|--------|------|
| 짧은 발화 (3-5초) | 실시간 VAD 단위 테스트 |
| 긴 발화 (30초+) | 연속 발화 정확도 |
| 소음 환경 | 배경 소음 내성 |
| 빠른 말투 | 빠른 발화 인식률 |
| 전문 용어 | 카드/금융 전문 용어 정확도 |

### 4.3 정답 데이터 (Ground Truth)
- 각 시나리오에 대한 수동 전사 텍스트 준비 필요
- 핵심 키워드 목록 라벨링 필요

---

## 5. 테스트 환경

### 5.1 하드웨어

| 자원 | 사양 |
|------|------|
| GPU 0 | 사용 가능 (Qwen3-ASR, Faster-Whisper) |
| GPU 1 | 사용 가능 (VibeVoice-ASR) |
| RAM | 충분 |
| 네트워크 | OpenAI API 접근 가능 |

### 5.2 실행 방법

```bash
# 기존 A/B 테스트 도구 활용
cd /mnt/c/Users/AI-WS01/projects/call-act/backend_dev/local_servers

# STT 비교 테스트
python ab_test_runner.py --test stt

# 비교 대시보드
python comparison_dashboard.py  # → http://localhost:8889
```

### 5.3 모델 서빙

```bash
# Qwen3-ASR (이미 구성됨)
bash local_servers/orchestrator.sh start  # 포트 8104

# VibeVoice-ASR (추가 설정 필요)
cd backend_dev/local_servers/VibeVoice
python demo/vibevoice_asr_inference_from_file.py  # 파일 기반 테스트
```

---

## 6. 테스트 절차

### Phase A: 오프라인 파일 기반 비교 (1-2일)

1. **테스트 오디오 준비**
   - 시나리오 1-8 TTS 생성 오디오 수집
   - 실제 녹음 오디오가 있다면 추가
   - Ground Truth 전사 텍스트 작성

2. **4개 엔진 순차 테스트**
   ```
   for each audio_file in test_set:
     for each engine in [whisper-1, qwen3-asr, faster-whisper, vibevoice]:
       result = engine.transcribe(audio_file)
       save(result, metrics)
   ```

3. **WER/CER 계산**
   - jiwer 라이브러리 사용
   - 엔진별 비교표 생성

### Phase B: 실시간 시뮬레이션 비교 (1-2일)

1. **WebSocket 기반 실시간 테스트**
   - VAD 단위 (1-1.5초) 오디오 청크 전송
   - Latency 측정 (전송 → 응답)
   - 실시간 전사 품질 vs 파일 기반 차이 비교

2. **키워드 추출 연계 테스트**
   - 각 엔진의 전사 결과 → extract_signals() → 키워드 비교
   - VocabGate 통과율 비교

### Phase C: 종합 평가 및 보고서 (1일)

1. **결과 종합**
   - 엔진별 WER/CER/RTF/Latency 비교표
   - 키워드 추출 정확도 비교
   - 비용/GPU 사용량 비교

2. **권고안 작성**
   - 프로덕션 교체 권고 엔진 선정
   - 마이그레이션 계획

---

## 7. 성공 기준

| 기준 | 현재 (Whisper-1) | 목표 |
|------|-----------------|------|
| WER | ~20-30% (추정) | < 15% |
| RTF | ~0.5 (API 지연 포함) | < 0.3 |
| 키워드 정확도 | ~60% (추정) | > 85% |
| 할루시네이션 | 가끔 발생 | 거의 없음 |
| 비용 | $0.006/분 (API) | $0/분 (로컬) |
| 화자 분리 | 별도 LLM 필요 | 내장 (VibeVoice) |

---

## 8. 사전 조건 (Backend 세션 협조 필요)

- [ ] `call_websocket.py:27`에서 `WhisperService()` → `create_stt_service()` 전환
- [ ] 테스트 오디오 파일 확보 (시나리오 1-8)
- [ ] VibeVoice-ASR을 `STTService` 인터페이스로 래핑 (M+B 공동)
- [ ] Ground Truth 전사 텍스트 작성 (M 담당)

---

## 9. 일정

| 일자 | 작업 | 담당 |
|------|------|------|
| D+0 (오늘) | 계획 수립, 코드베이스 분석 | M |
| D+1 | 테스트 오디오/GT 준비, 환경 세팅 | M |
| D+2 | Phase A: 오프라인 비교 테스트 | M |
| D+3 | Phase B: 실시간 시뮬레이션 | M + B |
| D+4 | Phase C: 종합 평가, 보고서 작성 | M |
| D+5 | 엔진 교체 결정 및 마이그레이션 | M + B |

---

## 10. 의존성

```
M-1 (STT 비교 테스트)
  ↓
M-2 (키워드 추출 개선) ← STT 품질이 개선되어야 키워드 품질 측정 의미 있음
  ↓
M-3 (RAG 검색 품질) ← 키워드 품질이 개선되어야 검색 품질 측정 의미 있음
```
