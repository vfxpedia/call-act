"""
테디카드 통합 전처리 - 임베딩 생성

변환된 JSON 파일들을 읽어서 OpenAI Embedding API로 임베딩을 생성하고 저장
- service_guide_documents: text 필드를 기반으로 임베딩 생성
- card_products: full_content 또는 main_benefits를 기반으로 임베딩 생성
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI

# 환경 변수 로드
BASE_DIR = Path(__file__).resolve().parents[3]  # call-act
load_dotenv(BASE_DIR / '.env', override=False)

# 상수
# 주의: 현재는 data-preprocessing_dev에서 작업, 나중에 data-preprocessing로 옮길 예정
# 옮길 때는 아래 경로를 BASE_DIR / "data-preprocessing" / "preprocessing" / "output"로 변경
INPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "preprocessing" / "output"
OUTPUT_DIR = BASE_DIR / "data-preprocessing_dev" / "preprocessing" / "output"  # 임베딩 포함 파일 저장
CHECKPOINT_FILE = OUTPUT_DIR / "embedding_checkpoint.json"
LOG_FILE = OUTPUT_DIR / "embedding_generation.log"

# 환경 변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("OPENAI_EMBEDDING_DIMENSION", "1536"))
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("EMBEDDING_RETRY_DELAY", "5"))
REQUEST_DELAY = float(os.getenv("EMBEDDING_REQUEST_DELAY", "0.5"))


class TeeLogger:
    """콘솔과 파일에 동시에 로그를 출력하는 클래스"""
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.file_handle = open(log_file, 'a', encoding='utf-8')
        self.original_stdout = sys.stdout
    
    def write(self, message: str):
        self.file_handle.write(message)
        self.file_handle.flush()
        self.original_stdout.write(message)
        self.original_stdout.flush()
    
    def close(self):
        if self.file_handle:
            self.file_handle.close()


tee_logger: Optional[TeeLogger] = None


def setup_logging():
    """로깅 설정"""
    global tee_logger
    if tee_logger is None:
        tee_logger = TeeLogger(LOG_FILE)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tee_logger.write(f"\n{'='*80}\n")
        tee_logger.write(f"Embedding Generation Started: {timestamp}\n")
        tee_logger.write(f"{'='*80}\n")
    return tee_logger


def log_print(*args, **kwargs):
    """로그 출력 함수"""
    global tee_logger
    if tee_logger is None:
        setup_logging()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = ' '.join(str(arg) for arg in args)
    if kwargs.get('end', '\n') == '\n':
        message += '\n'
    
    timestamped_message = f"[{timestamp}] {message}"
    tee_logger.write(timestamped_message)


def load_json_file(file_path: Path) -> List[Dict]:
    """JSON 파일 로드"""
    log_print(f"[INFO] Loading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    log_print(f"[INFO] Loaded {len(data)} documents")
    return data


def load_checkpoint() -> Dict:
    """체크포인트 로드"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_ids": []}


def save_checkpoint(checkpoint: Dict):
    """체크포인트 저장"""
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def generate_embedding(text: str, client: OpenAI, retries: int = MAX_RETRIES) -> Optional[List[float]]:
    """OpenAI Embedding API 호출"""
    for attempt in range(retries):
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt < retries - 1:
                wait_time = RETRY_DELAY * (attempt + 1)
                log_print(f"[WARNING] API error (attempt {attempt + 1}/{retries}): {e}")
                time.sleep(wait_time)
            else:
                log_print(f"[ERROR] Failed to generate embedding: {e}")
                return None
    return None


def generate_embeddings_for_documents(
    documents: List[Dict],
    resume: bool = False
) -> List[Dict]:
    """문서들에 대해 임베딩 생성"""
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # 체크포인트 로드
    checkpoint = load_checkpoint() if resume else {"processed_ids": []}
    processed_ids = set(checkpoint.get("processed_ids", []))
    
    # 이미 처리된 문서 제외
    if resume:
        documents = [doc for doc in documents if doc.get("id") not in processed_ids]
        log_print(f"[RESUME] {len(processed_ids)} documents already processed, {len(documents)} remaining")
    
    pbar = tqdm(total=len(documents), desc="Generating embeddings")
    results = []
    errors = []
    
    for idx, doc in enumerate(documents):
        doc_id = doc.get("id", f"unknown_{idx}")
        
        # 임베딩 생성할 텍스트 선택
        text = doc.get("text") or doc.get("content") or doc.get("full_content") or doc.get("main_benefits", "")
        
        if not text:
            log_print(f"[WARNING] Document {doc_id} has no text, skipping")
            continue
        
        # 임베딩 생성
        embedding = generate_embedding(text, client)
        
        if embedding:
            doc["embedding"] = embedding
            results.append(doc)
            processed_ids.add(doc_id)
            
            # 체크포인트 저장 (100개마다)
            if (idx + 1) % 100 == 0:
                checkpoint = {
                    "processed_ids": list(processed_ids),
                    "last_index": idx,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_checkpoint(checkpoint)
        else:
            errors.append(doc_id)
        
        pbar.update(1)
        time.sleep(REQUEST_DELAY)
    
    pbar.close()
    
    # 최종 체크포인트 저장
    checkpoint = {
        "processed_ids": list(processed_ids),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_documents": len(documents),
        "processed_count": len(results),
        "error_count": len(errors),
        "completed": True
    }
    save_checkpoint(checkpoint)
    
    pbar.close()
    log_print(f"\n[INFO] Completed: {len(results)}/{len(documents)} embeddings generated, {len(errors)} errors")
    if errors:
        log_print(f"[ERROR] Failed document IDs: {errors[:10]}{'...' if len(errors) > 10 else ''}")
        # 에러 로그 파일에 저장
        error_log_file = OUTPUT_DIR / "embedding_errors.json"
        with open(error_log_file, 'w', encoding='utf-8') as f:
            json.dump({"errors": errors, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
        log_print(f"[INFO] Error log saved: {error_log_file}")
    
    return results


def merge_and_save_outputs(resume: bool = False):
    """모든 변환된 JSON 파일들을 읽어서 임베딩 생성 및 통합 저장"""
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # service_guide_documents 파일들 통합
    # 보강된 파일이 있으면 우선 사용, 없으면 원본 파일 사용
    enriched_guides_file = INPUT_DIR / "teddycard_service_guides_enriched.json"
    if enriched_guides_file.exists():
        log_print(f"[INFO] Using enriched file: {enriched_guides_file.name}")
        all_service_guides = load_json_file(enriched_guides_file)
    else:
        log_print(f"[INFO] Using original files (enriched file not found)")
        service_guide_files = [
            INPUT_DIR / "teddycard_service_guides_hyundai.json",
            INPUT_DIR / "teddycard_service_guides_samsung.json",
            INPUT_DIR / "teddycard_service_guides_shinhan.json",
            INPUT_DIR / "teddycard_service_guides_special.json",
        ]
        
        all_service_guides = []
        for file_path in service_guide_files:
            if file_path.exists():
                data = load_json_file(file_path)
                all_service_guides.extend(data)
    
    log_print(f"[INFO] Total service_guide_documents: {len(all_service_guides)}")
    
    # 임베딩 생성
    log_print("\n[INFO] Generating embeddings for service_guide_documents...")
    service_guides_with_embeddings = generate_embeddings_for_documents(all_service_guides, resume=resume)
    
    # 저장
    output_file = OUTPUT_DIR / "teddycard_service_guides_with_embeddings.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(service_guides_with_embeddings, f, ensure_ascii=False, indent=2)
    log_print(f"[INFO] Saved: {output_file}")
    
    # card_products 파일 처리
    # 보강된 파일이 있으면 우선 사용
    enriched_cards_file = INPUT_DIR / "teddycard_card_products_enriched.json"
    if enriched_cards_file.exists():
        log_print(f"[INFO] Using enriched file: {enriched_cards_file.name}")
        card_products = load_json_file(enriched_cards_file)
    else:
        card_products_file = INPUT_DIR / "teddycard_card_products.json"
        if card_products_file.exists():
            log_print(f"[INFO] Using original file: {card_products_file.name}")
            card_products = load_json_file(card_products_file)
        else:
            card_products = []
    
    if card_products:
        log_print(f"[INFO] Total card_products: {len(card_products)}")
        
        log_print("\n[INFO] Generating embeddings for card_products...")
        card_products_with_embeddings = generate_embeddings_for_documents(card_products, resume=resume)
        
        output_file = OUTPUT_DIR / "teddycard_card_products_with_embeddings.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(card_products_with_embeddings, f, ensure_ascii=False, indent=2)
        log_print(f"[INFO] Saved: {output_file}")
    
    # notices 파일 처리
    # 보강된 파일이 있으면 우선 사용
    enriched_notices_file = INPUT_DIR / "teddycard_notices_enriched.json"
    if enriched_notices_file.exists():
        log_print(f"[INFO] Using enriched file: {enriched_notices_file.name}")
        notices = load_json_file(enriched_notices_file)
    else:
        notices_file = INPUT_DIR / "teddycard_notices.json"
        if notices_file.exists():
            log_print(f"[INFO] Using original file: {notices_file.name}")
            notices = load_json_file(notices_file)
        else:
            notices = []
    
    if notices:
        log_print(f"[INFO] Total notices: {len(notices)}")
        
        log_print("\n[INFO] Generating embeddings for notices...")
        notices_with_embeddings = generate_embeddings_for_documents(notices, resume=resume)
        
        output_file = OUTPUT_DIR / "teddycard_notices_with_embeddings.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(notices, f, ensure_ascii=False, indent=2)
        log_print(f"[INFO] Saved: {output_file}")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate embeddings for TeddyCard data")
    parser.add_argument('--resume', action='store_true', help='Resume from checkpoint')
    args = parser.parse_args()
    
    setup_logging()
    
    try:
        log_print("=" * 80)
        log_print("테디카드 통합 전처리 - 임베딩 생성 스크립트")
        log_print("=" * 80)
        
        merge_and_save_outputs(resume=args.resume)
        
        log_print("\n" + "=" * 80)
        log_print("임베딩 생성 완료!")
        log_print("=" * 80)
        
    except KeyboardInterrupt:
        log_print("\n[WARNING] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        log_print(traceback.format_exc())
        sys.exit(1)
    finally:
        if tee_logger:
            tee_logger.close()


if __name__ == '__main__':
    main()
