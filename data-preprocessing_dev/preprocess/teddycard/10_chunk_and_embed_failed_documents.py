"""
테디카드 통합 전처리 - 임베딩 실패 문서 청킹 및 재처리

22개 card_products 문서가 8192 토큰 초과로 임베딩 실패
의미 기반 청킹을 통해 처리하고 기존 임베딩 파일에 추가
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI
import tiktoken

# 설정 파일 로드
from config import (
    PROJECT_ROOT, OUTPUT_DIR, EMBEDDING_CONFIG, CHUNKING_CONFIG
)

# 환경 변수 로드 (API 키만 .env에서)
load_dotenv(PROJECT_ROOT / '.env', override=False)

# 경로 설정 (config에서 가져옴)
INPUT_DIR = OUTPUT_DIR
ERRORS_FILE = INPUT_DIR / "embedding_errors.json"
ENRICHED_CARDS_FILE = INPUT_DIR / "teddycard_card_products_enriched.json"
EMBEDDINGS_FILE = INPUT_DIR / "teddycard_card_products_with_embeddings.json"
OUTPUT_FILE = INPUT_DIR / "teddycard_card_products_with_embeddings.json"  # 기존 파일에 추가

# 환경 변수 (API 키만 .env에서)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 임베딩 설정 (config에서 가져옴)
EMBEDDING_MODEL = EMBEDDING_CONFIG["model"]
REQUEST_DELAY = EMBEDDING_CONFIG["request_delay"]

# 청킹 설정 (config에서 가져옴)
MAX_TOKENS = CHUNKING_CONFIG["max_tokens"]
CHUNK_MAX_TOKENS = CHUNKING_CONFIG["chunk_max_tokens"]
CHUNK_OVERLAP_TOKENS = CHUNKING_CONFIG["chunk_overlap_tokens"]

# 토큰 인코더
try:
    encoding = tiktoken.encoding_for_model("gpt-4")
except:
    encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """텍스트의 토큰 수 계산"""
    return len(encoding.encode(text))


def split_by_sections(text: str) -> List[Tuple[str, str]]:
    """
    텍스트를 섹션 단위로 분할
    Markdown 헤더(#, ##, ###) 기준으로 분할
    
    Returns:
        [(section_header, section_content), ...]
    """
    sections = []
    
    # 헤더 패턴: #, ##, ###로 시작하는 줄
    header_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    
    # 헤더 위치 찾기
    matches = list(header_pattern.finditer(text))
    
    if not matches:
        # 헤더가 없으면 전체를 하나의 섹션으로
        return [("", text)]
    
    # 첫 번째 섹션 (헤더 이전)
    if matches[0].start() > 0:
        sections.append(("", text[:matches[0].start()].strip()))
    
    # 헤더별 섹션 추출
    for i, match in enumerate(matches):
        header_level = len(match.group(1))
        header_text = match.group(2).strip()
        start_pos = match.end()
        
        # 다음 헤더 위치 (또는 끝)
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(text)
        
        section_content = text[start_pos:end_pos].strip()
        sections.append((header_text, section_content))
    
    return sections


def chunk_text_semantic(text: str, max_tokens: int = CHUNK_MAX_TOKENS, overlap_tokens: int = CHUNK_OVERLAP_TOKENS) -> List[str]:
    """
    의미 기반 청킹
    섹션 단위로 분할하고, 필요시 더 작게 분할
    """
    chunks = []
    
    # 1. 섹션 단위로 분할
    sections = split_by_sections(text)
    
    current_chunk = ""
    current_tokens = 0
    
    for header, content in sections:
        section_text = f"{'#' * (1 if header else 0)} {header}\n{content}" if header else content
        section_tokens = count_tokens(section_text)
        
        # 섹션이 작으면 현재 청크에 추가
        if current_tokens + section_tokens <= max_tokens:
            if current_chunk:
                current_chunk += "\n\n" + section_text
            else:
                current_chunk = section_text
            current_tokens += section_tokens
        else:
            # 현재 청크 저장
            if current_chunk:
                chunks.append(current_chunk)
            
            # 섹션이 너무 크면 문단 단위로 분할
            if section_tokens > max_tokens:
                # 문단 단위 분할
                paragraphs = re.split(r'\n\n+', content)
                sub_chunk = f"# {header}\n" if header else ""
                sub_tokens = count_tokens(sub_chunk)
                
                for para in paragraphs:
                    para_tokens = count_tokens(para)
                    
                    if sub_tokens + para_tokens <= max_tokens:
                        sub_chunk += para + "\n\n"
                        sub_tokens += para_tokens
                    else:
                        if sub_chunk.strip():
                            chunks.append(sub_chunk.strip())
                        sub_chunk = f"# {header}\n{para}\n\n" if header else para + "\n\n"
                        sub_tokens = count_tokens(sub_chunk)
                
                if sub_chunk.strip():
                    current_chunk = sub_chunk.strip()
                    current_tokens = sub_tokens
                else:
                    current_chunk = ""
                    current_tokens = 0
            else:
                current_chunk = section_text
                current_tokens = section_tokens
    
    # 마지막 청크 추가
    if current_chunk:
        chunks.append(current_chunk)
    
    # Overlap 적용 (마지막 청크 제외)
    overlapped_chunks = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            overlapped_chunks.append(chunk)
        else:
            # 이전 청크의 마지막 부분을 현재 청크 앞에 추가
            prev_chunk = chunks[i - 1]
            prev_tokens = count_tokens(prev_chunk)
            
            # 이전 청크의 마지막 부분 추출 (overlap_tokens만큼)
            prev_lines = prev_chunk.split('\n')
            overlap_text = ""
            overlap_count = 0
            
            for line in reversed(prev_lines):
                line_tokens = count_tokens(line)
                if overlap_count + line_tokens <= overlap_tokens:
                    overlap_text = line + '\n' + overlap_text
                    overlap_count += line_tokens
                else:
                    break
            
            if overlap_text:
                overlapped_chunk = overlap_text.strip() + '\n\n' + chunk
            else:
                overlapped_chunk = chunk
            
            overlapped_chunks.append(overlapped_chunk)
    
    return overlapped_chunks


def generate_embedding(text: str, client: OpenAI, retries: int = 3) -> Optional[List[float]]:
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
                wait_time = 5 * (attempt + 1)
                print(f"[WARNING] API error (attempt {attempt + 1}/{retries}): {e}")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] Failed to generate embedding: {e}")
                return None
    return None


def process_failed_documents():
    """실패한 문서들을 청킹하고 임베딩 생성"""
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # 1. 에러 문서 ID 로드
    if not ERRORS_FILE.exists():
        print(f"[ERROR] 에러 파일을 찾을 수 없습니다: {ERRORS_FILE}")
        return
    
    with open(ERRORS_FILE, 'r', encoding='utf-8') as f:
        errors_data = json.load(f)
    
    error_ids = set(errors_data.get("errors", []))
    print(f"[INFO] 처리할 실패 문서: {len(error_ids)}개")
    
    # 2. 원본 문서 로드
    if not ENRICHED_CARDS_FILE.exists():
        print(f"[ERROR] 원본 파일을 찾을 수 없습니다: {ENRICHED_CARDS_FILE}")
        return
    
    with open(ENRICHED_CARDS_FILE, 'r', encoding='utf-8') as f:
        all_documents = json.load(f)
    
    # 3. 실패한 문서만 필터링
    failed_docs = [doc for doc in all_documents if doc.get("id") in error_ids]
    print(f"[INFO] 실패 문서 필터링 완료: {len(failed_docs)}개")
    
    # 4. 기존 임베딩 파일 로드 (추가를 위해)
    existing_docs = []
    if EMBEDDINGS_FILE.exists():
        with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
            existing_docs = json.load(f)
        print(f"[INFO] 기존 임베딩 문서: {len(existing_docs)}개")
    
    # 5. 청킹 및 임베딩 생성
    chunked_docs = []
    
    for doc in tqdm(failed_docs, desc="청킹 및 임베딩 생성"):
        doc_id = doc.get("id")
        text = doc.get("main_benefits") or doc.get("full_content", "")
        
        if not text:
            print(f"[WARNING] 문서 {doc_id}에 텍스트가 없습니다. 건너뜁니다.")
            continue
        
        # 토큰 수 확인
        tokens = count_tokens(text)
        print(f"[INFO] 문서 {doc_id}: {tokens} 토큰")
        
        if tokens <= MAX_TOKENS:
            # 토큰 제한 내이면 그대로 임베딩 생성
            embedding = generate_embedding(text, client)
            if embedding:
                doc["embedding"] = embedding
                doc["metadata"] = doc.get("metadata", {})
                doc["metadata"]["chunked"] = False
                chunked_docs.append(doc)
                time.sleep(REQUEST_DELAY)
        else:
            # 청킹 필요
            print(f"[INFO] 문서 {doc_id} 청킹 중...")
            chunks = chunk_text_semantic(text, CHUNK_MAX_TOKENS, CHUNK_OVERLAP_TOKENS)
            print(f"[INFO] {len(chunks)}개 청크로 분할됨")
            
            chunk_embeddings = []
            for chunk_idx, chunk in enumerate(chunks):
                chunk_tokens = count_tokens(chunk)
                print(f"  청크 {chunk_idx + 1}/{len(chunks)}: {chunk_tokens} 토큰")
                
                embedding = generate_embedding(chunk, client)
                if embedding:
                    # 청크 문서 생성
                    chunk_doc = doc.copy()
                    chunk_doc["id"] = f"{doc_id}_chunk_{chunk_idx + 1}"
                    chunk_doc["main_benefits"] = chunk
                    chunk_doc["full_content"] = chunk  # 청크는 main_benefits와 동일
                    chunk_doc["embedding"] = embedding
                    chunk_doc["metadata"] = doc.get("metadata", {}).copy()
                    chunk_doc["metadata"]["chunked"] = True
                    chunk_doc["metadata"]["original_id"] = doc_id
                    chunk_doc["metadata"]["chunk_index"] = chunk_idx + 1
                    chunk_doc["metadata"]["total_chunks"] = len(chunks)
                    
                    chunk_embeddings.append(chunk_doc)
                    time.sleep(REQUEST_DELAY)
                else:
                    print(f"[WARNING] 청크 {chunk_idx + 1} 임베딩 생성 실패")
            
            if chunk_embeddings:
                chunked_docs.extend(chunk_embeddings)
                print(f"[INFO] 문서 {doc_id}: {len(chunk_embeddings)}개 청크 임베딩 완료")
    
    # 6. 기존 문서와 병합
    print(f"\n[INFO] 기존 문서와 병합 중...")
    all_docs = existing_docs + chunked_docs
    
    # 7. 저장
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)
    
    print(f"\n[INFO] 완료!")
    print(f"  기존 문서: {len(existing_docs)}개")
    print(f"  추가 문서: {len(chunked_docs)}개")
    print(f"  총 문서: {len(all_docs)}개")
    print(f"  저장 위치: {OUTPUT_FILE}")


if __name__ == "__main__":
    print("=" * 80)
    print("임베딩 실패 문서 청킹 및 재처리")
    print("=" * 80)
    process_failed_documents()
