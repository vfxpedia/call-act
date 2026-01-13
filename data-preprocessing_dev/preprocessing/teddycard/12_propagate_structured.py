"""
테디카드 전처리 - structured 필드 전파 스크립트

원본, 보강(enriched), 임베딩(with_embeddings) 파일 모두에 structured 필드를 일관되게 적용합니다.
structured 필드가 있는 파일에서 읽어와서 같은 id를 가진 문서에 전파합니다.

처리 대상:
- service_guides: 원본 → enriched → with_embeddings 전파
- card_products: 원본 → enriched → with_embeddings 전파
- notices: structured 필드 제거 (RAG 검색 미사용)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from tqdm import tqdm

# 설정 파일 로드
from config import OUTPUT_DIR

# 처리할 파일 그룹 정의
FILE_GROUPS = {
    "service_guides": {
        "source_files": [  # 원본 파일들 (structured 필드가 있는 파일)
            "teddycard_service_guides_hyundai.json",
            "teddycard_service_guides_samsung.json",
            "teddycard_service_guides_shinhan.json",
            "teddycard_service_guides_special.json"
        ],
        "targets": [
            "teddycard_service_guides_enriched.json",  # 보강 (통합)
            "teddycard_service_guides_with_embeddings.json"  # 임베딩
        ]
    },
    "card_products": {
        "source": "teddycard_card_products.json",  # 원본 파일 (structured 필드가 있는 파일)
        "targets": [
            "teddycard_card_products_enriched.json",  # 보강
            "teddycard_card_products_with_embeddings.json"  # 임베딩
        ]
    }
}


def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """JSON 파일 로드"""
    if not file_path.exists():
        print(f"[WARNING] 파일이 존재하지 않습니다: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            return [data]
        return data
    except Exception as e:
        print(f"[ERROR] 파일 로드 실패 {file_path}: {e}")
        return []


def save_json_file(file_path: Path, data: List[Dict[str, Any]]):
    """JSON 파일 저장"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] 저장 완료: {file_path}")
    except Exception as e:
        print(f"[ERROR] 파일 저장 실패 {file_path}: {e}")


def create_structured_map(documents: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """문서 리스트에서 id -> structured 필드 매핑 생성"""
    structured_map = {}
    for doc in documents:
        doc_id = doc.get("id")
        structured = doc.get("structured")
        if doc_id and structured:
            structured_map[doc_id] = structured
    return structured_map


def propagate_structured_to_documents(
    documents: List[Dict[str, Any]],
    structured_map: Dict[str, Dict[str, Any]],
    update_existing: bool = True
) -> tuple[int, int]:
    """
    문서 리스트에 structured 필드 전파
    
    Returns:
        (업데이트된 문서 수, 새로 추가된 문서 수)
    """
    updated_count = 0
    added_count = 0
    
    for doc in documents:
        doc_id = doc.get("id")
        if not doc_id:
            continue
        
        if doc_id in structured_map:
            if "structured" in doc:
                if update_existing:
                    doc["structured"] = structured_map[doc_id]
                    updated_count += 1
            else:
                doc["structured"] = structured_map[doc_id]
                added_count += 1
    
    return updated_count, added_count


def process_card_products():
    """카드 상품 파일 처리"""
    print("\n=== 카드 상품 (card_products) 처리 ===")
    
    group = FILE_GROUPS["card_products"]
    source_file = OUTPUT_DIR / group["source"]
    
    # Source 파일에서 structured 필드 읽기
    source_docs = load_json_file(source_file)
    if not source_docs:
        print(f"[WARNING] Source 파일이 비어있거나 로드할 수 없습니다: {source_file}")
        return
    
    structured_map = create_structured_map(source_docs)
    print(f"[INFO] Source 파일에서 {len(structured_map)}개의 structured 필드를 찾았습니다.")
    
    # Target 파일들에 structured 필드 전파
    for target_filename in group["targets"]:
        target_file = OUTPUT_DIR / target_filename
        target_docs = load_json_file(target_file)
        
        if not target_docs:
            print(f"[WARNING] Target 파일이 비어있습니다: {target_file}")
            continue
        
        updated, added = propagate_structured_to_documents(target_docs, structured_map)
        print(f"[INFO] {target_filename}: {updated}개 업데이트, {added}개 추가")
        
        if updated > 0 or added > 0:
            save_json_file(target_file, target_docs)
        else:
            print(f"[INFO] {target_filename}: 변경사항 없음")


def remove_structured_from_notices():
    """공지사항 파일에서 structured 필드 제거 (RAG 검색 미사용)"""
    print("\n=== 공지사항 (notices) 처리 - structured 필드 제거 ===")
    
    notice_files = [
        "teddycard_notices.json",
        "teddycard_notices_enriched.json",
        "teddycard_notices_with_embeddings.json"
    ]
    
    for filename in notice_files:
        file_path = OUTPUT_DIR / filename
        if not file_path.exists():
            print(f"[WARNING] 파일이 존재하지 않습니다: {file_path}")
            continue
        
        documents = load_json_file(file_path)
        if not documents:
            continue
        
        removed_count = 0
        for doc in documents:
            if "structured" in doc:
                del doc["structured"]
                removed_count += 1
        
        if removed_count > 0:
            save_json_file(file_path, documents)
            print(f"[INFO] {filename}: {removed_count}개 문서에서 structured 필드 제거")
        else:
            print(f"[INFO] {filename}: structured 필드 없음 (변경사항 없음)")


def process_service_guides():
    """서비스 가이드 파일 처리"""
    print("\n=== 서비스 가이드 (service_guides) 처리 ===")
    
    group = FILE_GROUPS["service_guides"]
    
    # 모든 원본 파일에서 structured 필드 수집
    all_structured_map = {}
    
    for source_filename in group["source_files"]:
        source_file = OUTPUT_DIR / source_filename
        source_docs = load_json_file(source_file)
        
        if source_docs:
            structured_map = create_structured_map(source_docs)
            all_structured_map.update(structured_map)
            print(f"[INFO] {source_filename}: {len(structured_map)}개의 structured 필드 발견")
    
    print(f"[INFO] 총 {len(all_structured_map)}개의 structured 필드를 수집했습니다.")
    
    # Target 파일들에 structured 필드 전파
    for target_filename in group["targets"]:
        target_file = OUTPUT_DIR / target_filename
        target_docs = load_json_file(target_file)
        
        if not target_docs:
            print(f"[WARNING] Target 파일이 비어있습니다: {target_file}")
            continue
        
        updated, added = propagate_structured_to_documents(target_docs, all_structured_map)
        print(f"[INFO] {target_filename}: {updated}개 업데이트, {added}개 추가")
        
        if updated > 0 or added > 0:
            save_json_file(target_file, target_docs)
        else:
            print(f"[INFO] {target_filename}: 변경사항 없음")


def main():
    """메인 함수"""
    print("=" * 60)
    print("structured 필드 전파 스크립트")
    print("=" * 60)
    print(f"출력 디렉토리: {OUTPUT_DIR}")
    
    # 디렉토리 확인
    if not OUTPUT_DIR.exists():
        print(f"[ERROR] 출력 디렉토리가 존재하지 않습니다: {OUTPUT_DIR}")
        sys.exit(1)
    
    try:
        # 서비스 가이드 처리
        process_service_guides()
        
        # 카드 상품 처리
        process_card_products()
        
        # 공지사항 처리 (structured 필드 제거)
        remove_structured_from_notices()
        
        print("\n" + "=" * 60)
        print("처리 완료!")
        print("=" * 60)
        print("\n[INFO] service_guides: enriched, with_embeddings에 structured 필드 전파 완료")
        print("[INFO] card_products: enriched, with_embeddings에 structured 필드 전파 완료")
        print("[INFO] notices: structured 필드 제거 완료 (RAG 검색 미사용)")
        
    except Exception as e:
        print(f"\n[ERROR] 처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
