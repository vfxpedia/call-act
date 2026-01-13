"""
테디카드 통합 전처리 - 문서 통합 유틸리티

Category2 기준으로 문서를 통합하는 함수를 제공합니다.
"""

from typing import List, Dict, Any
from collections import defaultdict


def merge_by_category2(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    같은 category2를 가진 문서들을 하나로 통합
    
    통합 전략:
    - 같은 metadata.original_category2 값을 가진 문서가 2개 이상인 경우 통합
    - 통합된 문서의 제목은 category2 값 사용
    - 통합된 문서의 내용은 모든 문서의 내용을 '\n\n'으로 연결
    - 원본 문서 ID 목록을 metadata.merged_from에 저장
    
    Args:
        documents: 문서 리스트
    
    Returns:
        통합된 문서 리스트
    """
    grouped = defaultdict(list)
    standalone_docs = []
    
    # category2 기준으로 그룹화
    for doc in documents:
        category2 = doc.get('metadata', {}).get('original_category2', '')
        if category2:
            grouped[category2].append(doc)
        else:
            # category2가 없는 문서는 그대로 유지
            standalone_docs.append(doc)
    
    merged_docs = []
    
    for category2, docs in grouped.items():
        if len(docs) > 1:
            # 여러 개일 때만 통합
            # 첫 번째 문서를 기준으로 통합
            merged = docs[0].copy()
            
            # ID 생성 (category2 기반)
            merged['id'] = f"{category2}_merged"
            
            # 제목은 category2 값 사용
            merged['title'] = category2
            
            # 내용 통합 (각 문서의 title과 content를 연결)
            content_parts = []
            text_parts = []
            
            for d in docs:
                title = d.get('title', '')
                content = d.get('content', '')
                text = d.get('text', '')
                
                if title and content:
                    content_parts.append(f"{title}\n{content}")
                elif content:
                    content_parts.append(content)
                
                if text:
                    text_parts.append(text)
            
            merged['content'] = '\n\n'.join(content_parts)
            merged['text'] = '\n\n'.join(text_parts)
            
            # 메타데이터 업데이트
            merged['metadata'] = merged.get('metadata', {}).copy()
            merged['metadata']['merged_from'] = [d['id'] for d in docs]
            merged['metadata']['is_merged'] = True
            merged['metadata']['merge_count'] = len(docs)
            
            merged_docs.append(merged)
        else:
            # 1개만 있는 경우 그대로 유지
            standalone_docs.extend(docs)
    
    return merged_docs + standalone_docs


if __name__ == '__main__':
    # 테스트 코드
    test_docs = [
        {
            'id': 'doc1',
            'title': '제목1',
            'content': '내용1',
            'text': '텍스트1',
            'metadata': {
                'original_category2': '신용도 관리방법'
            }
        },
        {
            'id': 'doc2',
            'title': '제목2',
            'content': '내용2',
            'text': '텍스트2',
            'metadata': {
                'original_category2': '신용도 관리방법'
            }
        },
        {
            'id': 'doc3',
            'title': '제목3',
            'content': '내용3',
            'text': '텍스트3',
            'metadata': {
                'original_category2': '다른카테고리'
            }
        }
    ]
    
    result = merge_by_category2(test_docs)
    
    print("통합 테스트 결과:")
    print(f"원본: {len(test_docs)}개")
    print(f"결과: {len(result)}개")
    
    for doc in result:
        if doc.get('metadata', {}).get('is_merged'):
            print(f"\n통합된 문서: {doc['id']}")
            print(f"  원본 문서 수: {doc['metadata']['merge_count']}")
            print(f"  원본 ID: {doc['metadata']['merged_from']}")
        else:
            print(f"\n단독 문서: {doc['id']}")
