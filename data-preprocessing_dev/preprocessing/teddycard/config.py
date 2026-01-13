"""
테디카드 전처리 설정 파일

개발 환경(_dev)과 프로덕션 환경(data-preprocessing) 간 경로 전환을 쉽게 하기 위한 설정
"""

import os
from pathlib import Path
from typing import Literal

# 환경 타입: 'dev' 또는 'prod'
# dev: data-preprocessing_dev 사용
# prod: data-preprocessing 사용
ENV_TYPE: Literal['dev', 'prod'] = os.getenv('PREPROCESSING_ENV', 'dev').lower()

# 프로젝트 루트 디렉토리
# config.py 위치: data-preprocessing_dev/preprocessing/teddycard/config.py
# call-act 루트까지: parents[3]
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # call-act

# 데이터 디렉토리 경로
if ENV_TYPE == 'dev':
    DATA_DIR = PROJECT_ROOT / "data-preprocessing_dev"
    PREPROCESSING_DIR = DATA_DIR / "preprocessing"
    OUTPUT_DIR = PREPROCESSING_DIR / "output"
else:
    DATA_DIR = PROJECT_ROOT / "data-preprocessing"
    PREPROCESSING_DIR = DATA_DIR / "preprocess"  # prod는 preprocess
    OUTPUT_DIR = PREPROCESSING_DIR / "output"

# 스크립트 디렉토리
SCRIPT_DIR = Path(__file__).parent

# 하나카드 데이터 경로
HANA_DATA_FILE = PROJECT_ROOT / "data-preprocessing" / "data" / "hana" / "hana_vectordb.json"

# 키워드 사전 파일
KEYWORDS_DICT_FILE = SCRIPT_DIR / "keywords_dict.json"

# 임베딩 관련 설정 (OpenAI API 키는 .env에서만 관리)
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",
    "dimension": 1536,
    "batch_size": 100,
    "max_retries": 3,
    "retry_delay": 5,  # 초
    "request_delay": 0.5,  # 초 (API rate limit 고려)
}

# LLM 관련 설정 (환경 변수로 오버라이드 가능)
# 기본 모델: gpt-4.1-mini (최신 모델, 비용 효율적, 확장된 컨텍스트 지원)
# 상위 모델 테스트: gpt-4o, gpt-4-turbo (환경 변수로 변경 가능)
LLM_CONFIG = {
    "model": os.getenv("LLM_MODEL", "gpt-4.1-mini"),  # 기본값: gpt-4.1-mini
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.3")),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2000")),  # detailContent, fullTerms 포함하여 증가
    # 지원 모델: gpt-4.1-mini (기본), gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo
}

# 구조화 관련 설정
STRUCTURE_CONFIG = {
    "use_parallel": False,  # 기본값: 순차 처리 (안전)
    "max_workers": 5,  # 병렬 처리 시 worker 수
    "rate_limit_per_minute": 60,  # 분당 요청 수 제한 (안전 마진)
}

# 청킹 관련 설정
CHUNKING_CONFIG = {
    "max_tokens": 8191,  # OpenAI 제한
    "chunk_max_tokens": 6000,  # 안전 마진
    "chunk_overlap_tokens": 600,  # 10% overlap
}

# 출력 파일명 패턴
OUTPUT_PATTERNS = {
    "card_products": "teddycard_card_products",
    "service_guides": "teddycard_service_guides",
    "notices": "teddycard_notices",
}

# 처리할 파일 목록
SERVICE_GUIDES_FILES = [
    "teddycard_service_guides_hyundai.json",
    "teddycard_service_guides_samsung.json",
    "teddycard_service_guides_shinhan.json",
    "teddycard_service_guides_special.json"
]

NOTICES_FILE = "teddycard_notices_enriched.json"
