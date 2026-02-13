"""
TTS 엔진 래퍼 모듈

TTS_ENGINE 환경변수에 따라 다른 TTS 백엔드를 사용합니다:
- "qwen3" (기본값): RunPod에 배포된 Qwen3 TTS 서버
- "edge": Microsoft Edge-TTS (무료, 로컬)
"""
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# TTS 엔진 선택 (qwen3 | edge)
TTS_ENGINE = os.getenv("TTS_ENGINE", "qwen3").lower()

# RunPod TTS 서버 설정 (qwen3 엔진용)
TTS_RUNPOD_URL = os.getenv("TTS_RUNPOD_URL", "http://localhost:8000")
TTS_TIMEOUT = int(os.getenv("TTS_TIMEOUT", "30"))

# Edge-TTS 사용 가능 여부
_edge_tts_available = None

# 세션 재사용
_session = requests.Session()

# 상태 캐시
_server_available = None


def check_server_health() -> bool:
    """TTS 서버 상태 확인"""
    global _server_available

    try:
        response = _session.get(f"{TTS_RUNPOD_URL}/health", timeout=5)
        _server_available = response.status_code == 200
        return _server_available
    except Exception as e:
        print(f"[TTS Engine] 서버 연결 실패: {e}")
        _server_available = False
        return False


def _generate_speech_qwen3(
    text: str,
    voice_config: Dict[str, Any],
    output_path: str
) -> bool:
    """
    Qwen3 TTS (RunPod 서버) 음성 생성
    """
    try:
        # 출력 디렉토리 생성
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 음성 설정 매핑
        speaker = voice_config.get("speaker", "Sohee")
        language = voice_config.get("language", "Korean")
        instruct = voice_config.get("instruct", "")

        # 속도를 instruct로 변환 (호환성)
        speed = voice_config.get("speed", "moderate")
        if speed == "slow" and not instruct:
            instruct = "천천히 말해"
        elif speed == "fast" and not instruct:
            instruct = "빠르게 말해"

        print(f"[TTS Qwen3] 음성 생성 중: {text[:50]}...")
        print(f"[TTS Qwen3] 설정: speaker={speaker}, language={language}")

        # RunPod TTS API 호출
        payload = {
            "text": text,
            "language": language,
            "speaker": speaker,
            "instruct": instruct
        }

        response = _session.post(
            f"{TTS_RUNPOD_URL}/tts",
            json=payload,
            timeout=TTS_TIMEOUT
        )

        if response.status_code != 200:
            print(f"[TTS Qwen3] API 오류 ({response.status_code}): {response.text[:200]}")
            return False

        # WAV 파일 저장
        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"[TTS Qwen3] 음성 파일 저장 완료: {output_path}")
        return True

    except requests.exceptions.Timeout:
        print(f"[TTS Qwen3] 서버 타임아웃 ({TTS_TIMEOUT}초)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"[TTS Qwen3] 서버 연결 실패: {TTS_RUNPOD_URL}")
        return False
    except Exception as e:
        print(f"[TTS Qwen3] 음성 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def _generate_speech_edge(
    text: str,
    voice_config: Dict[str, Any],
    output_path: str
) -> bool:
    """
    Edge-TTS 음성 생성
    """
    global _edge_tts_available

    # Edge-TTS 모듈 동적 로드
    if _edge_tts_available is None:
        try:
            from app.llm.education.tts_edge import generate_speech_edge as edge_generate
            _edge_tts_available = True
        except ImportError:
            _edge_tts_available = False
            print("[TTS Edge] edge-tts 모듈 로드 실패")

    if not _edge_tts_available:
        return False

    from app.llm.education.tts_edge import generate_speech_edge as edge_generate
    return edge_generate(text, voice_config, output_path)


def generate_speech(
    text: str,
    voice_config: Dict[str, Any],
    output_path: str,
    speaker_wav: Optional[str] = None  # 하위 호환성 (미사용)
) -> bool:
    """
    텍스트를 음성으로 변환

    TTS_ENGINE 환경변수에 따라 백엔드를 선택합니다:
    - "qwen3": RunPod Qwen3 TTS 서버
    - "edge": Microsoft Edge-TTS (무료, 로컬)

    Args:
        text: 변환할 텍스트
        voice_config: 음성 설정 (speaker, language, instruct, speed)
        output_path: 출력 파일 경로 (.wav 또는 .mp3)
        speaker_wav: (미사용) 하위 호환성을 위해 유지

    Returns:
        성공 여부 (bool)
    """
    if not text or not text.strip():
        print("[TTS Engine] 빈 텍스트, 건너뜀")
        return False

    print(f"[TTS Engine] 사용 엔진: {TTS_ENGINE}")

    if TTS_ENGINE == "edge":
        return _generate_speech_edge(text, voice_config, output_path)
    else:
        # 기본값: qwen3
        return _generate_speech_qwen3(text, voice_config, output_path)


def get_model_status() -> Dict[str, Any]:
    """
    TTS 모델 상태 조회
    """
    status_info = {
        "engine": TTS_ENGINE,
        "status": "unknown"
    }

    if TTS_ENGINE == "edge":
        # Edge-TTS는 항상 사용 가능 (인터넷 연결 시)
        try:
            from app.llm.education.tts_edge import check_edge_tts_available
            status_info["status"] = "available" if check_edge_tts_available() else "unavailable"
            status_info["note"] = "Edge-TTS (Microsoft, 무료)"
        except ImportError:
            status_info["status"] = "unavailable"
            status_info["error"] = "edge-tts 패키지 미설치"
    else:
        # Qwen3 TTS (RunPod)
        try:
            response = _session.get(f"{TTS_RUNPOD_URL}/health", timeout=5)
            if response.status_code == 200:
                status_info.update(response.json())
                status_info["status"] = "available"
            else:
                status_info["status"] = "error"
        except Exception:
            status_info["status"] = "unavailable"
            status_info["server_url"] = TTS_RUNPOD_URL

    return status_info


def get_available_speakers() -> list:
    """
    사용 가능한 스피커 목록 조회
    """
    try:
        response = _session.get(f"{TTS_RUNPOD_URL}/speakers", timeout=5)
        if response.status_code == 200:
            return response.json().get("speakers", [])
    except Exception:
        pass

    # 기본 스피커 목록 (오프라인 시)
    return [
        {"name": "Sohee", "language": "Korean", "description": "한국어 여성"},
    ]


def save_audio_file(audio_data: bytes, file_path: str) -> bool:
    """
    오디오 데이터를 파일로 저장

    Args:
        audio_data: 오디오 바이트 데이터
        file_path: 저장 경로

    Returns:
        성공 여부
    """
    try:
        output_dir = os.path.dirname(file_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(audio_data)

        print(f"[TTS Engine] 오디오 파일 저장: {file_path}")
        return True

    except Exception as e:
        print(f"[TTS Engine] 파일 저장 실패: {e}")
        return False
