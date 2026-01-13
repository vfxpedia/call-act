"""
하나카드 데이터 임베딩 생성 스크립트

기능:
- hana_vectordb.json 로드
- OpenAI Embedding API 호출
- 임베딩 벡터 생성 및 저장
- 배치 처리 및 에러 핸들링
- 체크포인트 지원 (재시작 가능)
- 파일 로그 저장 (단일 파일에 기록 업데이트)
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
# 1. 로컬 .env 파일 우선 (backend_dev/app/db/scripts/.env)
# 2. 프로젝트 루트 .env 파일 (override=False로 이미 로드된 값은 유지)
load_dotenv(Path(__file__).parent / '.env', override=False)
load_dotenv(Path(__file__).parent.parent.parent.parent.parent / '.env', override=False)

# 상수
BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
INPUT_FILE = BASE_DIR / "data-preprocessing" / "data" / "hana" / "hana_vectordb.json"
OUTPUT_FILE = BASE_DIR / "data-preprocessing" / "data" / "hana" / "hana_vectordb_with_embeddings.json"
CHECKPOINT_FILE = Path(__file__).parent / "embedding_checkpoint.json"
LOG_FILE = Path(__file__).parent / "embedding_generation.log"


class TeeLogger:
    """콘솔과 파일에 동시에 로그를 출력하는 클래스"""
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.file_handle = open(log_file, 'a', encoding='utf-8')
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def write(self, message: str):
        """로그 메시지를 파일과 콘솔에 동시에 출력"""
        # 파일에 기록
        self.file_handle.write(message)
        self.file_handle.flush()
        
        # 콘솔에 출력
        self.original_stdout.write(message)
        self.original_stdout.flush()
    
    def close(self):
        """로그 파일 닫기"""
        if self.file_handle:
            self.file_handle.close()


# 전역 로거 인스턴스
tee_logger: Optional[TeeLogger] = None


def setup_logging():
    """로깅 설정 (단일 파일에 기록)"""
    global tee_logger
    if tee_logger is None:
        # 기존 로그 파일에 이어서 기록 (append 모드)
        tee_logger = TeeLogger(LOG_FILE)
        # 시작 로그
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tee_logger.write(f"\n{'='*80}\n")
        tee_logger.write(f"Embedding Generation Started: {timestamp}\n")
        tee_logger.write(f"{'='*80}\n")
    return tee_logger


def log_print(*args, **kwargs):
    """로그 출력 함수 (콘솔 + 파일, 타임스탬프 포함)"""
    global tee_logger
    if tee_logger is None:
        setup_logging()
    
    # 타임스탬프 추가
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = ' '.join(str(arg) for arg in args)
    if kwargs.get('end', '\n') == '\n':
        message += '\n'
    
    # 타임스탬프가 포함된 메시지 생성
    timestamped_message = f"[{timestamp}] {message}"
    
    tee_logger.write(timestamped_message)

# 환경 변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("OPENAI_EMBEDDING_DIMENSION", "1536"))
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("EMBEDDING_RETRY_DELAY", "5"))
REQUEST_DELAY = float(os.getenv("EMBEDDING_REQUEST_DELAY", "0.5"))


def load_vectordb_json(file_path: Path) -> List[Dict]:
    """VectorDB JSON 파일 로드"""
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
    return {"processed_ids": [], "last_index": -1}


def save_checkpoint(checkpoint: Dict):
    """체크포인트 저장"""
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def generate_embedding(text: str, client: OpenAI, retries: int = MAX_RETRIES) -> Optional[List[float]]:
    """OpenAI Embedding API 호출 (재시도 로직 포함)"""
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
                log_print(f"[INFO] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                log_print(f"[ERROR] Failed to generate embedding after {retries} attempts: {e}")
                return None
    return None


def generate_embeddings_batch(
    documents: List[Dict],
    limit: Optional[int] = None,
    resume: bool = False
) -> List[Dict]:
    """배치로 임베딩 생성"""
    
    # OpenAI 클라이언트 초기화
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # 체크포인트 로드
    checkpoint = load_checkpoint() if resume else {"processed_ids": [], "last_index": -1}
    processed_ids = set(checkpoint.get("processed_ids", []))
    
    # 제한 적용
    if limit:
        documents = documents[:limit]
    
    # 이미 처리된 문서 제외
    if resume:
        documents = [doc for doc in documents if doc.get("id") not in processed_ids]
        log_print(f"[RESUME] {len(processed_ids)} documents already processed, {len(documents)} remaining")
    
    # 진행률 표시
    pbar = tqdm(total=len(documents), desc="Generating embeddings")
    
    results = []
    errors = []
    
    for idx, doc in enumerate(documents):
        doc_id = doc.get("id", f"unknown_{idx}")
        content = doc.get("content", "")
        
        if not content:
            log_print(f"[WARNING] Document {doc_id} has no content, skipping")
            continue
        
        # 임베딩 생성
        embedding = generate_embedding(content, client)
        
        if embedding:
            doc["embedding"] = embedding
            results.append(doc)
            processed_ids.add(doc_id)
            
            # 체크포인트 저장 (100개마다)
            if (idx + 1) % 100 == 0:
                checkpoint = {
                    "processed_ids": list(processed_ids),
                    "last_index": idx,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                save_checkpoint(checkpoint)
        else:
            errors.append(doc_id)
            log_print(f"[ERROR] Failed to generate embedding for {doc_id}")
        
        pbar.update(1)
        
        # Rate limit 고려 대기
        time.sleep(REQUEST_DELAY)
    
    pbar.close()
    
    # 최종 체크포인트 저장
    checkpoint = {
        "processed_ids": list(processed_ids),
        "last_index": len(documents) - 1,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_checkpoint(checkpoint)
    
    log_print(f"\n[INFO] Completed: {len(results)} embeddings generated, {len(errors)} errors")
    if errors:
        log_print(f"[ERROR] Failed document IDs: {errors[:10]}{'...' if len(errors) > 10 else ''}")
    
    return results


def save_embeddings_json(documents: List[Dict], output_path: Path):
    """임베딩이 포함된 JSON 파일 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_print(f"[INFO] Saving {len(documents)} documents to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    log_print(f"[INFO] Saved to {output_path}")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate embeddings for Hana Card consultation data")
    parser.add_argument("--limit", type=int, help="Limit number of documents to process (for testing)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--input", type=str, help="Input JSON file path")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    
    args = parser.parse_args()
    
    # 파일 경로 설정
    input_file = Path(args.input) if args.input else INPUT_FILE
    output_file = Path(args.output) if args.output else OUTPUT_FILE
    
    # 로깅 설정
    setup_logging()
    log_print(f"[INFO] Log file: {LOG_FILE}")
    
    # 입력 파일 확인
    if not input_file.exists():
        log_print(f"[ERROR] Input file not found: {input_file}")
        if tee_logger:
            tee_logger.close()
        return
    
    # 데이터 로드
    documents = load_vectordb_json(input_file)
    
    # 임베딩 생성
    log_print(f"\n[INFO] Starting embedding generation...")
    log_print(f"[INFO] Model: {EMBEDDING_MODEL}")
    log_print(f"[INFO] Dimension: {EMBEDDING_DIMENSION}")
    log_print(f"[INFO] Batch size: {BATCH_SIZE}")
    log_print(f"[INFO] Limit: {args.limit if args.limit else 'None (all documents)'}")
    log_print(f"[INFO] Resume: {args.resume}")
    log_print(f"[INFO] Output file: {output_file}\n")
    
    start_time = time.time()
    documents_with_embeddings = generate_embeddings_batch(
        documents,
        limit=args.limit,
        resume=args.resume
    )
    elapsed_time = time.time() - start_time
    
    # 결과 저장
    save_embeddings_json(documents_with_embeddings, output_file)
    
    # 요약
    log_print(f"\n[SUMMARY]")
    log_print(f"  Total documents: {len(documents)}")
    log_print(f"  Processed: {len(documents_with_embeddings)}")
    log_print(f"  Elapsed time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
    if documents_with_embeddings:
        log_print(f"  Average time per document: {elapsed_time/len(documents_with_embeddings):.2f} seconds")
    log_print(f"  Output file: {output_file}")
    log_print(f"  Log file: {LOG_FILE}")
    
    # 로그 파일 닫기
    if tee_logger:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tee_logger.write(f"{'='*80}\n")
        tee_logger.write(f"[{timestamp}] Embedding Generation Completed\n")
        tee_logger.write(f"{'='*80}\n\n")
        tee_logger.close()


if __name__ == "__main__":
    main()


