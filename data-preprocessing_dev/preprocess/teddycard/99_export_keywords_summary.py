"""
키워드 사전 요약본 생성 스크립트

keywords_dict_v2_with_patterns.json 파일을 읽어서
키워드 목록을 텍스트/마크다운 파일로 출력합니다.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# 경로 설정
BASE_DIR = Path(__file__).parent.parent.parent.parent
KEYWORDS_DICT_FILE = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard" / "keywords_dict_v2_with_patterns.json"
OUTPUT_TXT = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard" / "keywords_summary.txt"
OUTPUT_MD = BASE_DIR / "data-preprocessing_dev" / "data" / "teddycard" / "keywords_summary.md"


def load_keywords_dict() -> Dict[str, Any]:
    """키워드 사전 로드"""
    print(f"키워드 사전 로드 중: {KEYWORDS_DICT_FILE}")
    with open(KEYWORDS_DICT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('keywords', {})


def analyze_keywords(keywords_dict: Dict[str, Any]) -> Dict[str, Any]:
    """키워드 사전 분석"""
    stats = {
        'total_keywords': len(keywords_dict),
        'keywords_with_synonyms': 0,
        'keywords_with_variations': 0,
        'keywords_with_patterns': 0,
        'total_synonyms': 0,
        'total_variations': 0,
        'total_patterns': 0,
        'category_count': defaultdict(int),
        'keywords_by_category': defaultdict(list),
    }
    
    for keyword, data in keywords_dict.items():
        canonical = data.get('canonical', keyword)
        synonyms = data.get('synonyms', [])
        variations = data.get('variations', [])
        compound_patterns = data.get('compound_patterns', [])
        patterns = data.get('patterns', [])
        categories = data.get('categories', [])
        
        if synonyms:
            stats['keywords_with_synonyms'] += 1
            stats['total_synonyms'] += len(synonyms)
        
        if variations:
            stats['keywords_with_variations'] += 1
            stats['total_variations'] += len(variations)
        
        if compound_patterns:
            stats['keywords_with_patterns'] += 1
            stats['total_patterns'] += len(compound_patterns)
        elif patterns:
            stats['keywords_with_patterns'] += 1
            stats['total_patterns'] += len(patterns)
        
        # 카테고리별 통계
        for cat_info in categories:
            category = cat_info.get('category', 'Unknown')
            stats['category_count'][category] += 1
            stats['keywords_by_category'][category].append(canonical)
    
    return stats


def generate_txt_summary(keywords_dict: Dict[str, Any], stats: Dict[str, Any]) -> str:
    """텍스트 형식 요약 생성"""
    lines = []
    lines.append("=" * 80)
    lines.append("키워드 사전 요약")
    lines.append("=" * 80)
    lines.append("")
    
    # 통계 정보
    lines.append("[통계]")
    lines.append(f"  총 키워드 수: {stats['total_keywords']:,}개")
    lines.append(f"  동의어가 있는 키워드: {stats['keywords_with_synonyms']:,}개")
    lines.append(f"  변형이 있는 키워드: {stats['keywords_with_variations']:,}개")
    lines.append(f"  패턴이 있는 키워드: {stats['keywords_with_patterns']:,}개")
    lines.append(f"  총 동의어 수: {stats['total_synonyms']:,}개")
    lines.append(f"  총 변형 수: {stats['total_variations']:,}개")
    lines.append(f"  총 패턴 수: {stats['total_patterns']:,}개")
    lines.append(f"  총 카테고리 수: {len(stats['category_count'])}개")
    lines.append("")
    
    # 카테고리별 키워드 수 (상위 20개)
    lines.append("[카테고리별 키워드 수 (상위 20개)]")
    sorted_categories = sorted(stats['category_count'].items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories[:20], 1):
        lines.append(f"  {i:2d}. {category}: {count}개")
    lines.append("")
    
    # 키워드 목록 (알파벳 순)
    lines.append("=" * 80)
    lines.append("[키워드 목록 (알파벳 순)]")
    lines.append("=" * 80)
    lines.append("")
    
    sorted_keywords = sorted(keywords_dict.items(), key=lambda x: x[1].get('canonical', x[0]))
    
    for keyword, data in sorted_keywords:
        canonical = data.get('canonical', keyword)
        synonyms = data.get('synonyms', [])
        variations = data.get('variations', [])
        compound_patterns = data.get('compound_patterns', [])
        patterns = data.get('patterns', [])
        categories = [cat.get('category', 'Unknown') for cat in data.get('categories', [])]
        
        lines.append(f"■ {canonical}")
        if synonyms:
            lines.append(f"  동의어: {', '.join(synonyms)}")
        if variations:
            lines.append(f"  변형: {', '.join(variations[:5])}")  # 최대 5개만 표시
            if len(variations) > 5:
                lines.append(f"    ... 외 {len(variations) - 5}개")
        if compound_patterns:
            pattern_strs = [p.get('pattern', str(p)) for p in compound_patterns[:5]]
            lines.append(f"  패턴: {', '.join(pattern_strs)}")
            if len(compound_patterns) > 5:
                lines.append(f"    ... 외 {len(compound_patterns) - 5}개")
        elif patterns:
            lines.append(f"  패턴: {', '.join(patterns[:5])}")  # 최대 5개만 표시
            if len(patterns) > 5:
                lines.append(f"    ... 외 {len(patterns) - 5}개")
        if categories:
            lines.append(f"  카테고리: {', '.join(categories[:3])}")  # 최대 3개만 표시
            if len(categories) > 3:
                lines.append(f"    ... 외 {len(categories) - 3}개")
        lines.append("")
    
    return "\n".join(lines)


def generate_keywords_table(keywords_dict: Dict[str, Any]) -> str:
    """키워드 목록만 표로 생성"""
    lines = []
    lines.append("=" * 80)
    lines.append("키워드 목록 (표 형식)")
    lines.append("=" * 80)
    lines.append("")
    
    sorted_keywords = sorted(keywords_dict.items(), key=lambda x: x[1].get('canonical', x[0]))
    
    # 표 헤더
    lines.append("| 순번 | 키워드 | 동의어 | 변형 | 패턴 | 카테고리 수 |")
    lines.append("|------|--------|--------|------|------|------------|")
    
    for idx, (keyword, data) in enumerate(sorted_keywords, 1):
        canonical = data.get('canonical', keyword)
        synonyms = data.get('synonyms', [])
        variations = data.get('variations', [])
        compound_patterns = data.get('compound_patterns', [])
        patterns = data.get('patterns', [])
        categories = data.get('categories', [])
        
        # 동의어 표시 (최대 3개)
        synonyms_str = ', '.join(synonyms[:3]) if synonyms else '-'
        if len(synonyms) > 3:
            synonyms_str += f' ... (+{len(synonyms) - 3})'
        
        # 변형 표시 (최대 3개)
        variations_str = ', '.join(variations[:3]) if variations else '-'
        if len(variations) > 3:
            variations_str += f' ... (+{len(variations) - 3})'
        
        # 패턴 표시
        pattern_count = len(compound_patterns) if compound_patterns else (len(patterns) if patterns else 0)
        pattern_str = f'{pattern_count}개' if pattern_count > 0 else '-'
        
        # 카테고리 수
        category_count = len(categories)
        
        lines.append(f"| {idx} | {canonical} | {synonyms_str} | {variations_str} | {pattern_str} | {category_count}개 |")
    
    return "\n".join(lines)


def generate_md_summary(keywords_dict: Dict[str, Any], stats: Dict[str, Any]) -> str:
    """마크다운 형식 요약 생성"""
    lines = []
    lines.append("# 키워드 사전 요약")
    lines.append("")
    
    # 통계 정보
    lines.append("## 통계")
    lines.append("")
    lines.append("| 항목 | 수량 |")
    lines.append("|------|------|")
    lines.append(f"| 총 키워드 수 | {stats['total_keywords']:,}개 |")
    lines.append(f"| 동의어가 있는 키워드 | {stats['keywords_with_synonyms']:,}개 |")
    lines.append(f"| 변형이 있는 키워드 | {stats['keywords_with_variations']:,}개 |")
    lines.append(f"| 패턴이 있는 키워드 | {stats['keywords_with_patterns']:,}개 |")
    lines.append(f"| 총 동의어 수 | {stats['total_synonyms']:,}개 |")
    lines.append(f"| 총 변형 수 | {stats['total_variations']:,}개 |")
    lines.append(f"| 총 패턴 수 | {stats['total_patterns']:,}개 |")
    lines.append(f"| 총 카테고리 수 | {len(stats['category_count'])}개 |")
    lines.append("")
    
    # 카테고리별 키워드 수
    lines.append("## 카테고리별 키워드 수 (상위 20개)")
    lines.append("")
    lines.append("| 순위 | 카테고리 | 키워드 수 |")
    lines.append("|------|----------|-----------|")
    sorted_categories = sorted(stats['category_count'].items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories[:20], 1):
        lines.append(f"| {i} | {category} | {count}개 |")
    lines.append("")
    
    # 키워드 목록
    lines.append("## 키워드 목록 (알파벳 순)")
    lines.append("")
    
    sorted_keywords = sorted(keywords_dict.items(), key=lambda x: x[1].get('canonical', x[0]))
    
    for keyword, data in sorted_keywords:
        canonical = data.get('canonical', keyword)
        synonyms = data.get('synonyms', [])
        variations = data.get('variations', [])
        compound_patterns = data.get('compound_patterns', [])
        patterns = data.get('patterns', [])
        categories = [cat.get('category', 'Unknown') for cat in data.get('categories', [])]
        
        lines.append(f"### {canonical}")
        lines.append("")
        
        if synonyms:
            lines.append(f"**동의어:** {', '.join(synonyms)}")
            lines.append("")
        
        if variations:
            lines.append(f"**변형:**")
            for variation in variations[:10]:  # 최대 10개만 표시
                lines.append(f"- {variation}")
            if len(variations) > 10:
                lines.append(f"- ... 외 {len(variations) - 10}개")
            lines.append("")
        
        if compound_patterns:
            lines.append(f"**패턴:**")
            for pattern_info in compound_patterns[:10]:  # 최대 10개만 표시
                pattern_str = pattern_info.get('pattern', str(pattern_info))
                lines.append(f"- `{pattern_str}`")
            if len(compound_patterns) > 10:
                lines.append(f"- ... 외 {len(compound_patterns) - 10}개")
            lines.append("")
        elif patterns:
            lines.append(f"**패턴:**")
            for pattern in patterns[:10]:  # 최대 10개만 표시
                lines.append(f"- `{pattern}`")
            if len(patterns) > 10:
                lines.append(f"- ... 외 {len(patterns) - 10}개")
            lines.append("")
        
        if categories:
            lines.append(f"**카테고리:**")
            for category in categories[:5]:  # 최대 5개만 표시
                lines.append(f"- {category}")
            if len(categories) > 5:
                lines.append(f"- ... 외 {len(categories) - 5}개")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def generate_md_keywords_table(keywords_dict: Dict[str, Any]) -> str:
    """마크다운 형식 키워드 목록 표 생성"""
    lines = []
    lines.append("## 키워드 목록 (표 형식)")
    lines.append("")
    lines.append("| 순번 | 키워드 | 동의어 | 변형 | 패턴 | 카테고리 수 |")
    lines.append("|------|--------|--------|------|------|------------|")
    
    sorted_keywords = sorted(keywords_dict.items(), key=lambda x: x[1].get('canonical', x[0]))
    
    for idx, (keyword, data) in enumerate(sorted_keywords, 1):
        canonical = data.get('canonical', keyword)
        synonyms = data.get('synonyms', [])
        variations = data.get('variations', [])
        compound_patterns = data.get('compound_patterns', [])
        patterns = data.get('patterns', [])
        categories = data.get('categories', [])
        
        # 동의어 표시 (최대 3개)
        synonyms_str = ', '.join(synonyms[:3]) if synonyms else '-'
        if len(synonyms) > 3:
            synonyms_str += f' ... (+{len(synonyms) - 3})'
        
        # 변형 표시 (최대 3개)
        variations_str = ', '.join(variations[:3]) if variations else '-'
        if len(variations) > 3:
            variations_str += f' ... (+{len(variations) - 3})'
        
        # 패턴 표시
        pattern_count = len(compound_patterns) if compound_patterns else (len(patterns) if patterns else 0)
        pattern_str = f'{pattern_count}개' if pattern_count > 0 else '-'
        
        # 카테고리 수
        category_count = len(categories)
        
        lines.append(f"| {idx} | {canonical} | {synonyms_str} | {variations_str} | {pattern_str} | {category_count}개 |")
    
    return "\n".join(lines)


def main():
    """메인 함수"""
    print("키워드 사전 요약 생성 시작...")
    
    # 키워드 사전 로드
    keywords_dict = load_keywords_dict()
    print(f"로드 완료: {len(keywords_dict)}개 키워드")
    
    # 통계 분석
    print("통계 분석 중...")
    stats = analyze_keywords(keywords_dict)
    
    # 텍스트 파일 생성
    print("텍스트 파일 생성 중...")
    txt_content = generate_txt_summary(keywords_dict, stats)
    txt_table = generate_keywords_table(keywords_dict)
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        f.write(txt_content)
        f.write("\n\n")
        f.write(txt_table)
    print(f"[OK] 생성 완료: {OUTPUT_TXT}")
    
    # 마크다운 파일 생성
    print("마크다운 파일 생성 중...")
    md_content = generate_md_summary(keywords_dict, stats)
    md_table = generate_md_keywords_table(keywords_dict)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)
        f.write("\n\n")
        f.write(md_table)
    print(f"[OK] 생성 완료: {OUTPUT_MD}")
    
    print("\n완료!")
    print(f"  - 텍스트 파일: {OUTPUT_TXT}")
    print(f"  - 마크다운 파일: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
