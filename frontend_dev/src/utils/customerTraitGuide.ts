/**
 * 고객 특성 태그 기반 상담 가이드 유틸리티
 * ⭐ Phase 9: LLM 기반 고객 맞춤형 상담 가이드 생성
 */

import type { CustomerInfo } from '../data/scenarios';

/**
 * 영어 personalityTags → 한글 변환 매핑
 * DB에 영어로 저장된 태그를 한글로 표시
 */
const PERSONALITY_TAG_MAP: { [key: string]: string } = {
  // 성격/성향
  'impatient': '성급함',
  'emotional': '감정적',
  'calm': '차분함',
  'friendly': '친절함',
  'aggressive': '공격적',
  'passive': '수동적',
  'analytical': '분석적',
  'expressive': '표현적',
  'assertive': '적극적',
  'reserved': '내성적',
  'talkative': '수다형',
  'personal': '친밀형',
  'quiet': '조용함',
  'polite': '예의바름',
  'direct': '직접적',
  'indirect': '우회적',
  'patient': '인내심',
  'anxious': '불안함',
  'confident': '자신감',
  'hesitant': '망설임',

  // 상담 스타일
  'quick_response': '빠른 답변 선호',
  'detailed_explanation': '상세 설명 필요',
  'empathy_needed': '공감 필요',
  'repeat_explanation': '반복 설명 필요',
  'self_service': '셀프서비스 선호',
  'digital_native': '디지털 친화',
  'tech_savvy': '기술 친화적',
  'needs_empathy': '공감 필요',
  'detail_oriented': '꼼꼼함',

  // 고객 유형
  'vip': 'VIP 고객',
  'premium': '프리미엄 고객',
  'loyal': '충성 고객',
  'new_customer': '신규 고객',
  'senior': '시니어',
  'business': '비즈니스 고객',
  'regular': '일반 고객',

  // 성격/성향 (추가)
  'practical': '실용적',
  'efficient': '효율적',
  'cautious': '신중함',
  'security_conscious': '보안 의식',
  'suspicious': '의심형',
  'detailed': '꼼꼼함',
  'thorough': '철저함',
  'confused': '혼란형',
  'demanding': '요구사항 많음',
  'normal': '일반',

  // 상담 스타일 (추가)
  'needs_repetition': '반복 설명 필요',
  'patient_required': '인내심 필요',
  'repeat_caller': '반복 문의',
  'frequent_caller': '잦은 문의',

  // 고객 유형 (추가)
  'elderly': '시니어',
  'high_value': '고가치 고객',

  // 주의 필요
  'complaint_prone': '민원 이력',
  'delinquent': '연체 이력',
  'cost_sensitive': '비용 민감',
  'high_maintenance': '고요구',
  'sensitive': '민감함',
  'urgent': '긴급',
  'time_sensitive': '시간 민감',
  'rushed': '급함',
  'busy': '바쁨',
  'frustrated': '좌절감',
  'angry': '화남',
  'unresolved': '미해결',
  'complaining': '불만형',
};

/**
 * 영어 태그를 한글로 변환
 */
export function translatePersonalityTag(tag: string): string {
  // 이미 한글이면 그대로 반환
  if (/[가-힣]/.test(tag)) {
    return tag;
  }
  // 매핑된 한글이 있으면 반환, 없으면 원본
  return PERSONALITY_TAG_MAP[tag.toLowerCase()] || tag;
}

/**
 * 고객 특성 태그 색상 매핑 (UI 배지용)
 * ⭐ Phase 10: 12개 페르소나 특성 추가 + 블루 계열 통일
 */
export function getTraitColor(trait: string): { bg: string; text: string } {
  const colorMap: { [key: string]: { bg: string; text: string } } = {
    // 등급별 테마 색상 (짧은 형식)
    'VIP': { bg: '#FDF4E7', text: '#B8860B' },          // 골드 계열
    'GOLD': { bg: '#FDF4E7', text: '#B8860B' },         // 골드 계열
    'PREMIUM': { bg: '#F3E8FF', text: '#7C3AED' },      // 퍼플 계열
    'SILVER': { bg: '#F1F5F9', text: '#475569' },       // 실버 계열
    'GENERAL': { bg: '#F5F5F5', text: '#666666' },      // 일반 그레이
    '일반': { bg: '#F5F5F5', text: '#666666' },         // 일반 그레이
    // 등급별 테마 색상 (긴 형식 - 호환용)
    'VIP 등급': { bg: '#FDF4E7', text: '#B8860B' },
    'GOLD 등급': { bg: '#FDF4E7', text: '#B8860B' },
    'PREMIUM 등급': { bg: '#F3E8FF', text: '#7C3AED' },
    'SILVER 등급': { bg: '#F1F5F9', text: '#475569' },
    'GENERAL 등급': { bg: '#F5F5F5', text: '#666666' },

    // 긍정적 특성 - 진한 블루
    'VIP 고객': { bg: '#FDF4E7', text: '#B8860B' },
    '신용 관리 철저': { bg: '#E8F1FC', text: '#0047AB' },
    '계획적인 성향': { bg: '#E8F1FC', text: '#0047AB' },
    '기술 친화적': { bg: '#E8F1FC', text: '#0047AB' },
    '비즈니스 목적': { bg: '#E8F1FC', text: '#0047AB' },
    '프로세스 이해도 높음': { bg: '#E8F1FC', text: '#0047AB' },
    '결과 중심': { bg: '#E8F1FC', text: '#0047AB' },
    '자동화 선호': { bg: '#E8F1FC', text: '#0047AB' },
    '적극적인 질문': { bg: '#E8F1FC', text: '#0047AB' },
    '프리미엄 서비스 기대': { bg: '#E8F1FC', text: '#0047AB' },
    '충성 고객': { bg: '#E8F1FC', text: '#0047AB' },
    '디지털 네이티브': { bg: '#E8F1FC', text: '#0047AB' },
    '셀프서비스 선호': { bg: '#E8F1FC', text: '#0047AB' },
    
    // 중립적 특성 - 그레이
    '일반 고객': { bg: '#F5F5F5', text: '#666666' },
    '친절한 성향': { bg: '#F5F5F5', text: '#666666' },
    '조용한 성향': { bg: '#F5F5F5', text: '#666666' },
    '내성적': { bg: '#F5F5F5', text: '#666666' },
    '실용주의': { bg: '#F5F5F5', text: '#666666' },
    '효율 중시': { bg: '#F5F5F5', text: '#666666' },
    '목적 지향적': { bg: '#F5F5F5', text: '#666666' },
    '친화적': { bg: '#F5F5F5', text: '#666666' },
    '수다형': { bg: '#E8F4FD', text: '#1976D2' },
    '친밀형': { bg: '#E8F4FD', text: '#1976D2' },
    '대화 선호': { bg: '#F5F5F5', text: '#666666' },
    '조용함': { bg: '#F5F5F5', text: '#666666' },
    '예의바름': { bg: '#E8F1FC', text: '#0047AB' },
    '인내심': { bg: '#E8F1FC', text: '#0047AB' },
    '자신감': { bg: '#E8F1FC', text: '#0047AB' },
    '꼼꼼함': { bg: '#F5F5F5', text: '#666666' },
    '빠른 답변 선호': { bg: '#F5F5F5', text: '#666666' },
    '바쁨': { bg: '#F5F5F5', text: '#666666' },
    '상세한 설명 필요': { bg: '#F5F5F5', text: '#666666' },
    '상세한 설명 요구': { bg: '#F5F5F5', text: '#666666' },
    '분석적': { bg: '#F5F5F5', text: '#666666' },
    '표현적': { bg: '#F5F5F5', text: '#666666' },
    '시니어': { bg: '#F5F5F5', text: '#666666' },
    '천천히 설명 필요': { bg: '#F5F5F5', text: '#666666' },
    '반복 안내 필요': { bg: '#F5F5F5', text: '#666666' },
    '해외 거주': { bg: '#F5F5F5', text: '#666666' },
    '해외 출장 잦음': { bg: '#F5F5F5', text: '#666666' },
    '비용 민감': { bg: '#F5F5F5', text: '#666666' },
    '꼼꼼한 성향': { bg: '#F5F5F5', text: '#666666' },
    '반복 질문 많음': { bg: '#F5F5F5', text: '#666666' },
    // Level02 추가 번역 태그
    '실용적': { bg: '#F5F5F5', text: '#666666' },
    '효율적': { bg: '#F5F5F5', text: '#666666' },
    '신중함': { bg: '#F5F5F5', text: '#666666' },
    '보안 의식': { bg: '#E8F1FC', text: '#0047AB' },
    '철저함': { bg: '#F5F5F5', text: '#666666' },
    '일반': { bg: '#F5F5F5', text: '#666666' },
    '반복 설명 필요': { bg: '#F5F5F5', text: '#666666' },
    '인내심 필요': { bg: '#F5F5F5', text: '#666666' },
    '고가치 고객': { bg: '#FDF4E7', text: '#B8860B' },
    '고요구': { bg: '#F5F5F5', text: '#666666' },
    '잦은 문의': { bg: '#D4E3F3', text: '#003580' },
    '반복 문의': { bg: '#D4E3F3', text: '#003580' },
    '영어 가능': { bg: '#F5F5F5', text: '#666666' },
    '온라인 처리 선호': { bg: '#F5F5F5', text: '#666666' },
    '급여일 기반 관리': { bg: '#F5F5F5', text: '#666666' },
    '이전 이력 확인 필요': { bg: '#F5F5F5', text: '#666666' },
    '요구사항 많음': { bg: '#F5F5F5', text: '#666666' },
    '까다로움': { bg: '#F5F5F5', text: '#666666' },
    
    // 주의 필요 특성 - 연한 블루 (경고성이지만 부드럽게)
    '급한 성향': { bg: '#D4E3F3', text: '#003580' },
    '감정 기복 있음': { bg: '#D4E3F3', text: '#003580' },
    '경제적 어려움': { bg: '#D4E3F3', text: '#003580' },
    '반복 연체 이력': { bg: '#D4E3F3', text: '#003580' },
    '공감 필요': { bg: '#D4E3F3', text: '#003580' },
    '감정 호소형': { bg: '#D4E3F3', text: '#003580' },
    '반복 민원': { bg: '#D4E3F3', text: '#003580' },
    '좌절감': { bg: '#D4E3F3', text: '#003580' },
    '불만 항의': { bg: '#D4E3F3', text: '#003580' },
    '불만형': { bg: '#D4E3F3', text: '#003580' },
    '의심형': { bg: '#D4E3F3', text: '#003580' },
    '혼란형': { bg: '#D4E3F3', text: '#003580' },
    '화남': { bg: '#FEE2E2', text: '#DC2626' },
    '미해결': { bg: '#FEF3C7', text: '#D97706' },
    '긴급': { bg: '#FEE2E2', text: '#DC2626' },         // 빨간색 계열
    '시간 민감': { bg: '#FEF3C7', text: '#D97706' },    // 주황색 계열
    '급함': { bg: '#FEE2E2', text: '#DC2626' },
    '민감함': { bg: '#D4E3F3', text: '#003580' },
    '불안함': { bg: '#D4E3F3', text: '#003580' },
    '망설임': { bg: '#F5F5F5', text: '#666666' },
  };

  return colorMap[trait] || { bg: '#F5F5F5', text: '#999999' };  // 기본값
}

/**
 * 고객 특성 태그 아이콘 매핑 (선택)
 * ⭐ Phase 9-2: 아이콘 제거로 인해 사용하지 않음 (향후 삭제 가능)
 */
export function getTraitIcon(trait: string): string {
  return '';  // 아이콘 제거
}

/**
 * 고객 특성 요약 문구 생성
 * 
 * @param customer - 고객 정보
 * @returns 간결한 특성 요약
 */
export function getCustomerTraitSummary(customer: CustomerInfo): string {
  if (!customer.traits || customer.traits.length === 0) {
    return '일반적인';
  }

  // 주요 특성 1-2개만 추출
  const keyTraits = customer.traits.slice(0, 2);
  return keyTraits.join(', ');
}

/**
 * 고객 특성 태그 기반 상담 가이드 생성
 * 
 * @param customer - 고객 정보 (traits, age, preferredStyle 포함)
 * @returns 상담 가이드 문구
 */
export function generateCustomerGuide(customer: CustomerInfo): string {
  if (!customer.traits || customer.traits.length === 0) {
    return `${customer.name} 고객님과의 상담을 시작합니다. 기본 응대 매뉴얼에 따라 진행해주세요.`;
  }

  // ⭐ Mock LLM: 태그 기반 가이드 생성 로직
  const traits = customer.traits;
  const age = customer.age || null;
  const style = customer.preferredStyle || '';

  // 1. 인사말
  let guide = `💡 ${customer.name} 고객님 상담 가이드\n\n`;

  // 2. 고객 특성 요약
  guide += `🏷️ 고객 특성:\n`;
  traits.forEach((trait, index) => {
    guide += `  ${index + 1}. ${trait}\n`;
  });
  if (age) {
    guide += `  • 연령대: ${age}세\n`;
  }
  guide += `\n`;

  // 3. 추천 상담 방식
  guide += `📌 추천 상담 방식:\n`;
  
  // 특성별 상담 팁
  if (traits.includes('빠른 답변 선호') || traits.includes('급한 성향')) {
    guide += `  • 핵심 정보를 먼저 전달하고, 세부사항은 필요시 추가 설명\n`;
    guide += `  • 불필요한 인사말이나 전치사를 최소화\n`;
  }
  
  if (traits.includes('VIP 고객') || traits.includes('PREMIUM') || traits.includes('GOLD')) {
    guide += `  • VIP 전용 혜택 및 우선 처리 옵션 안내\n`;
    guide += `  • 담당 매니저 연결 가능 여부 확인\n`;
  }
  
  if (traits.includes('해외 거주') || traits.includes('해외 출장 잦음')) {
    guide += `  • 시차를 고려한 응대 (현재 현지 시간 확인)\n`;
    guide += `  • 해외 연락처 확인 및 국제 전화 안내\n`;
  }
  
  if (traits.includes('감정 기복 있음') || traits.includes('공감 필요')) {
    guide += `  • 공감 표현을 자주 사용 ("고객님 말씀 충분히 이해됩니다")\n`;
    guide += `  • 차분한 톤으로 안정감 제공\n`;
  }
  
  if (traits.includes('상세한 설명 필요') || traits.includes('꼼꼼한 성향')) {
    guide += `  • 단계별 설명과 구체적인 예시 제공\n`;
    guide += `  • 서면 자료(이메일/SMS) 발송 제안\n`;
  }
  
  if (traits.includes('비용 민감') || traits.includes('경제적 어려움')) {
    guide += `  • 수수료 면제/할인 혜택 적극 안내\n`;
    guide += `  • 무이자 할부, 리볼빙 등 대안 제시\n`;
  }

  if (traits.includes('기술 친화적') || traits.includes('온라인 처리 선호') || traits.includes('자동화 선호')) {
    guide += `  • 앱/웹 셀프서비스 적극 안내\n`;
    guide += `  • 자동화된 프로세스(자동이체, 알림 설정 등) 추천\n`;
  }

  // 4. 선호 스타일 (있을 경우)
  if (style) {
    guide += `\n✨ 이 고객님은:\n`;
    guide += `  "${style}"\n`;
  }

  // 5. 마무리 팁
  guide += `\n💬 추가 팁:\n`;
  guide += `  • 상담 종료 시 "또 궁금하신 점 있으시면 언제든 연락주세요" 안내\n`;
  guide += `  • 이번 상담에서 새로운 특성 발견 시 후처리 메모에 기록\n`;

  return guide;
}
