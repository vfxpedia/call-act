/**
 * 텍스트 포맷팅 유틸리티
 */

/**
 * 한국어 문서 텍스트를 ReactMarkdown용 마크다운으로 전처리
 * - 이미 마크다운인 텍스트(`#`, `-`, `|`)는 그대로 통과
 * - 한국어 약관(`제N조`, `【】`) → 마크다운 헤딩/볼드 변환
 * - 서비스 가이드(첫줄 제목 + 본문) → 헤딩 변환
 */
export function convertToMarkdown(text: string): string {
  if (!text) return '';

  // 이미 마크다운 헤딩이 있으면 최소 전처리만
  if (/^#{1,3}\s/m.test(text)) {
    return _normalizeEscapes(text);
  }

  let result = _normalizeEscapes(text);

  // 【제목】 → ### 제목
  result = result.replace(/【(.+?)】/g, '\n### $1\n');

  // 제N조 (제목) → ## 제N조 (제목)  (줄 시작에서만)
  result = result.replace(/^(제\d+조(?:\s*\(.*?\))?)/gm, '## $1');

  // 부칙 → ## 부칙
  result = result.replace(/^(부칙)\s*$/gm, '## $1');

  // 서비스 가이드 패턴: 짧은 제목줄(40자 이하) 뒤에 긴 본문줄
  // "제목\n긴 설명..." → "### 제목\n긴 설명..."
  result = result.replace(
    /^(.{4,40})\n(?=.{60,})/gm,
    (_, title) => {
      // 이미 heading이면 스킵
      if (/^#{1,3}\s/.test(title)) return `${title}\n`;
      // 숫자 목록이면 스킵
      if (/^\d+\./.test(title)) return `${title}\n`;
      // 들여쓰기 목록이면 스킵
      if (/^\s+-/.test(title)) return `${title}\n`;
      return `### ${title}\n`;
    }
  );

  // 들여쓰기 목록(3+ 공백 + -)을 정규 마크다운 목록으로
  result = result.replace(/^(\s{3,})- /gm, '  - ');

  // 연속 빈 줄 정리 (3줄 이상 → 2줄)
  result = result.replace(/\n{3,}/g, '\n\n');

  return result.trim();
}

function _normalizeEscapes(text: string): string {
  // \\n → 실제 줄바꿈
  return text.replace(/\\\\n/g, '\n').replace(/\\n/g, '\n');
}

/**
 * 줄바꿈 문자를 실제 줄바꿈으로 변환
 * \\n 또는 \n을 <br/>로 변환
 * @param text - 변환할 텍스트
 * @returns 줄바꿈이 적용된 텍스트
 */
export function normalizeLineBreaks(text: string): string {
  if (!text) return '';
  
  // \\n (이중 백슬래시)을 실제 줄바꿈으로 변환
  let result = text.replace(/\\\\n/g, '\n');
  
  // 이미 변환되지 않은 \n도 처리
  result = result.replace(/\\n/g, '\n');
  
  return result;
}

/**
 * HTML 엔티티를 디코딩
 * @param text - 디코딩할 텍스트
 * @returns 디코딩된 텍스트
 */
export function decodeHTMLEntities(text: string): string {
  if (!text) return '';
  
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  return textarea.value;
}

/**
 * 공지사항 content 전용 포맷터
 * \\n을 실제 줄바꿈으로 변환하고 HTML 엔티티 디코딩
 * @param content - 공지사항 content
 * @returns 포맷팅된 content
 */
export function formatNoticeContent(content: string): string {
  if (!content) return '';
  
  // 1단계: HTML 엔티티 디코딩
  let result = decodeHTMLEntities(content);
  
  // 2단계: \\n을 실제 줄바꿈으로 변환
  result = normalizeLineBreaks(result);
  
  return result;
}
