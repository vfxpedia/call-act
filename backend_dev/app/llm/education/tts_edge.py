"""
Edge-TTS 래퍼 모듈

Microsoft Edge TTS를 사용하여 무료로 음성을 생성합니다.
실시간 스트리밍을 지원하며, 한국어 음성을 제공합니다.
"""
import os
import asyncio
from typing import Dict, Any, Optional

# Edge-TTS 패키지 (pip install edge-tts)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("[TTS Edge] edge-tts 패키지가 설치되지 않았습니다. pip install edge-tts")


# 한국어 음성 목록
KOREAN_VOICES = {
    "SunHi": "ko-KR-SunHiNeural",      # 여성, 차분함
    "InJoon": "ko-KR-InJoonNeural",    # 남성
    "HyunSu": "ko-KR-HyunsuNeural",    # 남성
    "Sohee": "ko-KR-SunHiNeural",      # 기존 호환성 (Sohee -> SunHi 매핑)
}

# 기본 음성
DEFAULT_VOICE = "ko-KR-SunHiNeural"


async def _generate_speech_async(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> bool:
    """
    비동기 음성 생성

    Args:
        text: 변환할 텍스트
        output_path: 출력 파일 경로 (.mp3)
        voice: Edge-TTS 음성 ID
        rate: 속도 조절 (예: "+10%", "-20%")
        pitch: 피치 조절 (예: "+5Hz", "-10Hz")

    Returns:
        성공 여부
    """
    if not EDGE_TTS_AVAILABLE:
        print("[TTS Edge] edge-tts 패키지가 없습니다")
        return False

    try:
        # 출력 디렉토리 생성
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Edge-TTS 객체 생성
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)

        # 오디오 저장
        await communicate.save(output_path)

        return True

    except Exception as e:
        print(f"[TTS Edge] 음성 생성 실패: {e}")
        return False


def generate_speech_edge(
    text: str,
    voice_config: Dict[str, Any],
    output_path: str
) -> bool:
    """
    Edge-TTS로 음성 생성 (동기 래퍼)

    Args:
        text: 변환할 텍스트
        voice_config: 음성 설정
            - speaker: 스피커 이름 (SunHi, InJoon, HyunSu, Sohee)
            - speed: 속도 (slow, moderate, fast)
        output_path: 출력 파일 경로 (.mp3)

    Returns:
        성공 여부
    """
    if not text or not text.strip():
        print("[TTS Edge] 빈 텍스트, 건너뜀")
        return False

    # 스피커 매핑
    speaker = voice_config.get("speaker", "SunHi")
    voice = KOREAN_VOICES.get(speaker, DEFAULT_VOICE)

    # 속도 매핑
    speed = voice_config.get("speed", "moderate")
    rate_map = {
        "slow": "-20%",
        "moderate": "+0%",
        "fast": "+15%"
    }
    rate = rate_map.get(speed, "+0%")

    print(f"[TTS Edge] 음성 생성 중: {text[:50]}...")
    print(f"[TTS Edge] 설정: voice={voice}, rate={rate}")

    # 비동기 함수를 동기로 실행
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    success = loop.run_until_complete(
        _generate_speech_async(text, output_path, voice, rate)
    )

    if success:
        print(f"[TTS Edge] 음성 파일 저장 완료: {output_path}")

    return success


def get_available_voices() -> list:
    """
    사용 가능한 한국어 음성 목록 반환
    """
    return [
        {"name": "SunHi", "voice_id": "ko-KR-SunHiNeural", "gender": "female", "description": "차분한 여성 음성"},
        {"name": "InJoon", "voice_id": "ko-KR-InJoonNeural", "gender": "male", "description": "남성 음성"},
        {"name": "HyunSu", "voice_id": "ko-KR-HyunsuNeural", "gender": "male", "description": "남성 음성"},
    ]


async def generate_speech_streaming(
    text: str,
    voice: str = DEFAULT_VOICE
):
    """
    스트리밍 방식 음성 생성 (실시간 재생용)

    사용 예:
        async for chunk in generate_speech_streaming("안녕하세요"):
            # chunk는 bytes (오디오 데이터)
            play_audio(chunk)

    Yields:
        오디오 청크 (bytes)
    """
    if not EDGE_TTS_AVAILABLE:
        return

    communicate = edge_tts.Communicate(text, voice)

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


def check_edge_tts_available() -> bool:
    """Edge-TTS 사용 가능 여부 확인"""
    return EDGE_TTS_AVAILABLE
