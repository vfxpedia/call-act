import MainLayout from '../components/layout/MainLayout';
import { Phone, PhoneOff, Save, Send, Lightbulb, Copy, Bot, User, ChevronLeft, ChevronRight, X, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSidebar } from '../contexts/SidebarContext';
import { scenarios, getScenarioByCategory, type Scenario, type ScenarioCard } from '../../data/scenarios';
import { generateConsultationId } from '@/utils/consultationId';
import { generateCustomerGuide, getCustomerTraitSummary, getTraitColor, getTraitIcon } from '@/utils/customerTraitGuide';
import { maskName, maskPhone, maskCardNumber } from '@/utils/mask';
import { InlineMaskedText } from '@/app/components/ui/MaskedText';
import { toast } from 'sonner';
import { USE_CUSTOMER_MASKING } from '@/config/mockConfig';
import { formatBirthDateWithAge } from '@/utils/age';

// Mock Data (기본값 - 통화 전)
const defaultCustomerInfo = {
  id: 'CUST-TEDDY-00000', // FK용 (화면 표시 안함)
  name: '홍길동',
  phone: '010-1234-5678',
  birthDate: '1985-03-15',
  address: '서울시 강남구 테헤란로 123',
  cardName: undefined,
  cardNumber: undefined,
  cardIssueDate: undefined,
  cardExpiryDate: undefined,
};

const defaultRecentConsultations = [
  { id: 1, title: '카드 재발급 문의', date: '2025-01-03 10:30', category: '카드분실', status: '완료' },
  { id: 2, title: '해외 결제 문의', date: '2024-12-28 14:20', category: '해외결제', status: '진행중' },
  { id: 3, title: '수수료 환불 요청', date: '2024-12-20 09:15', category: '수수료문의', status: '완료' },
];

// ⭐ 인입 케이스별 키워드 (통화 전 이미 분류되어 있음) - ⭐ Phase 14: 8개 대분류로 통일
const incomingKeywordsByCase: Record<string, string[]> = {
  '분실/도난': ['카드분실', '분실신고', '재발급', '도난', '긴급정지', '즉시정지', '카드정지'],
  '한도': ['한도증액', '한도조회', '신용한도', '증액신청', '한도상향', '한도부족'],
  '결제/승인': ['결제', '승인', '선결제', '즉시출금', '결제대금', '승인취소', '매출취소', '결제오류'],
  '이용내역': ['이용내역', '이용내역조회', '거래내역', '사용내역', '명세서'],
  '수수료/연체': ['연체', '연체문의', '연체이자', '수수료문의', '연회비', '이자', '할부수수료', '미납', '납부'],
  '포인트/혜택': ['포인트', '마일리지', '캐시백', '적립', '혜택조회', '이벤트', '혜택'],
  '정부지원': ['정부지원', '바우처', '등유', '임신', '육아', '복지카드', '정부지원금'],
  '기타': ['일반상담', '안내', '기타문의', '카드발급', '서비스', '문의', '해외결제', '해외사용', '결제일변경'],
};

// ⭐ 키워드 사전 (백엔드에서 받아올 데이터 구조) - 8개 대분류에 맞춰 확장 및 가중치 키워드 추가
const keywordDictionary = {
  "카드종류": ["신용카드", "체크카드", "법인카드", "가족카드", "선불카드", "하이브리드카드"],
  "분실도난": ["분실", "도난", "분실신고", "긴급정지", "즉시정지", "정지", "잃어버렸", "없어졌", "찾을수없"],
  "재발급": ["재발급", "재신청", "신규발급", "발급", "배송", "카드받기", "교체"],
  "결제승인": ["결제", "승인", "취소", "환불", "거절", "한도", "거래", "결제오류", "승인거부"],
  "포인트마일": ["포인트", "마일리지", "캐시백", "적립", "사용", "혜택", "리워드", "보너스"],
  "수수료연회비": ["수수료", "연회비", "이자", "할부", "수수료문의", "면제", "면제조건", "할부수수료"],
  "해외사용": ["해외", "해외결제", "해외사용", "외화", "환전", "달러", "해외승인", "해외가맹점"],
  "한도관리": ["한도", "한도증액", "한도조회", "신용한도", "증액", "증액신청", "한도상향", "한도부족"],
  "연체납부": ["연체", "연체이자", "납부", "결제지연", "미납", "입금", "가상계좌", "즉시납부"],
  "결제일": ["결제일", "결제일변경", "이체일", "출금일", "납부일", "급여일", "변경신청"],
};

// 모든 키워드를 하나의 배열로 변환
const allKeywords = Object.values(keywordDictionary).flat();

// 키워드 카테고리별 색상 매핑
const getKeywordCategory = (text: string): string | null => {
  for (const [category, keywords] of Object.entries(keywordDictionary)) {
    if (keywords.some(keyword => text.includes(keyword))) {
      return category;
    }
  }
  return null;
};

// 카테고리별 색상 - 8개 대분류에 맞춰 확장
const categoryColors: Record<string, string> = {
  "카드종류": "bg-[#E3F2FD] text-[#1976D2]",
  "분실도난": "bg-[#FFEBEE] text-[#C62828]",
  "재발급": "bg-[#E8F5E9] text-[#2E7D32]",
  "결제승인": "bg-[#FFF3E0] text-[#EF6C00]",
  "포인트마일": "bg-[#FCE4EC] text-[#C2185B]",
  "수수료연회비": "bg-[#F3E5F5] text-[#7B1FA2]",
  "해외사용": "bg-[#E0F2F1] text-[#00695C]",
  "한도관리": "bg-[#E1F5FE] text-[#0277BD]",
  "연체납부": "bg-[#FFF8E1] text-[#F57C00]",
  "결제일": "bg-[#F1F8E9] text-[#558B2F]",
};

// 대기 콜 현황 초기 데이터 (함수로 변경 - 매번 새로 생성) - ⭐ Phase 14: 8개 대분류로 통일
const getInitialWaitingCalls = () => [
  { category: '분실/도난', count: 3, waitTimeSeconds: 155, priority: 'urgent' as const },
  { category: '한도', count: 4, waitTimeSeconds: 115, priority: 'normal' as const },
  { category: '결제/승인', count: 12, waitTimeSeconds: 90, priority: 'normal' as const },
  { category: '이용내역', count: 7, waitTimeSeconds: 80, priority: 'normal' as const },
  { category: '수수료/연체', count: 2, waitTimeSeconds: 190, priority: 'urgent' as const },
  { category: '포인트/혜택', count: 2, waitTimeSeconds: 65, priority: 'normal' as const },
  { category: '정부지원', count: 1, waitTimeSeconds: 120, priority: 'normal' as const },
  { category: '기타', count: 11, waitTimeSeconds: 45, priority: 'normal' as const },
];

// 시간을 MM:SS 포맷으로 변환
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};

const currentSituationCards: ScenarioCard[] = [
  {
    id: '1',
    title: '카드 분실 신고 처리 절차',
    keywords: ['#분실신고', '#즉시정지', '#재발급'],
    content: '고객의 카드 분실 신고를 접수하�� 즉시 카드 사용을 정지합니다.',
    systemPath: '고객관리 > 카드관리 > 분실신고 > 즉시정지',
    requiredChecks: [
      '✓ 본인 확인: 주민번호 뒷자리 4자리 필수',
      '✓ 분실 일시 및 장소 확인',
      '✓ 최근 3일 거래내역 이상여부 확인',
      '✓ 재발급 신청 의사 확인'
    ],
    exceptions: [
      '⚠️ 법인카드: 담당자 승인 필요 (승인번호 기재)',
      '⚠️ 가족카드: 주카드 회원 동의 필수',
      '⚠️ 해외 분실: 긴급 카드 발급 가능 (수수료 $30)'
    ],
    regulation: '카드업무 취급요령 제34조 (분실신고 및 재발급)',
    fullText: `제34조 (카드의 분실신고 및 재발급)

① 회원은 카드를 분실한 경우 즉시 회사에 신고하여야 하며, 회사는 신고 접수 즉시 해당 카드의 이용을 정지하여야 한다.

② 회사는 회원의 분실신고 접수 시점 이후 발생한 제3자의 부정사용으로 인한 손해에 대하여 책임을 지며, 신고 접수 이전 72시간 이내 발생한 손해에 대해서는 보험 처리를 통해 보상한다.

③ 재발급 신청 시 회원은 본인확인 절차를 거쳐야 하며, 재발급 수수료는 면제한다. 단, 긴급 재발급의 경우 별도 수수료가 부과될 수 있다.

④ 재발급 카드는 신청일로부터 3-5 영업일 내 등록된 주소로 등기우편으로 발송되며, 회원은 SMS를 통해 배송 추적 번호를 제공받는다.

⑤ 법인카드의 경우 법인 담당자의 서면 승인이 필요하며, 가족카드는 주카드 회원의 동의가 필요하다.`,
    time: '처리 시간: 약 3-5분',
    note: '분실 신고 후 72시간 내 부정 사용 보상 가능'
  },
  {
    id: '2',
    title: '긴급 카드 정지 안내',
    keywords: ['#긴급처리', '#즉시정지'],
    content: '카드 분실 시 즉시 사용 정지가 가능하며 부정 사용을 방지합니다.',
    systemPath: '시스템 > 긴급처리 > 카드즉시정지 (단축키: Ctrl+Shift+S)',
    requiredChecks: [
      '✓ 정지 사유 코드 선택 (분실/도난/기타)',
      '✓ 정지 시각 자동 기록 확인',
      '✓ 고객 휴대폰 번호 재확인',
      '✓ SMS 발송 완료 확인'
    ],
    exceptions: [
      '⚠️ 정기결제: 72시간 유예 (자동이체 포함)',
      '⚠️ 교통카드: 별도 정지 필요 (교통카드 메뉴)',
      '⚠️ 해외 가맹점: 최대 24시간 지연 가능'
    ],
    regulation: '카드 이용약관 제8조 (카드의 이용정지)',
    fullText: `제8조 (카드의 이용정지)

① 회원이 카드의 이용정지를 요청하는 경우 회사는 즉시 카드 이용을 정지하며, 정지 시점은 시스템에 자동 기록된다.

② 카드 이용정지 시 회사는 회원에게 SMS, 이메일, 앱 푸시 알림을 통해 정지 사실을 통지한다.

③ 정지된 카드로는 신규 거래가 불가능하나, 정지 이전 승인된 거래 중 아직 매입되지 않은 거래는 정상 처리될 수 있다.

④ 정기결제 거래의 경우 카드 정지 후 72시간의 유예기간이 적용되며, 이 기간 동안 승인된 정기결제는 정상 처리된다.

⑤ 교통카드 기능이 포함된 카드의 경우 별도의 교통카드 정지 절차가 필요하며, 카드 정지 메뉴의 교통카드 탭에서 추가 정지를 진행해야 한다.

⑥ 해외 가맹점에서의 거래는 네트워크 지연으로 인해 카드 정지 후 최대 24시간까지 승인될 수 있다.`,
    time: '처리 시간: 즉시',
    note: '정지 후에도 정기 결제는 72시간 유예'
  },
];

const nextStepCards: ScenarioCard[] = [
  {
    id: '3',
    title: '재발급 카드 배송 안내',
    keywords: ['#배송', '#3-5일', '#주소확인'],
    content: '재발급 카드는 등록된 주소로 3-5일 내 배송되며 배송 추적이 가능합니다.',
    systemPath: '카드관리 > 재발급관리 > 배송조회 (단축키: Ctrl+D)',
    requiredChecks: [
      '✓ 등록 주소 정확성 확인 (우편번호 포함)',
      '✓ 수령 가능 시간대 확인',
      '✓ 대리 수령 가능 여부 안내',
      '✓ 배송 추적 SMS 수신 동의'
    ],
    exceptions: [
      '⚠️ 주소 변경: 발송 전까지만 가능 (고객센터 연락)',
      '⚠️ 긴급 배송: 익일 배송 가능 (수수료 5,000원)',
      '⚠️ 해외 주소: 국제 배송 불가 (국내만 가능)'
    ],
    regulation: '카드업무 취급요령 제35조 (카드의 배송 및 수령)',
    fullText: `제35조 (카드의 배송 및 수령)

① 재발급 카드는 회원이 등록한 주소로 등기우편을 통해 배송되며, 배송 기간은 신청일로부터 3-5 영업일이다.

② 회사는 카드 발송 시 회원에게 SMS를 통해 택배 송장 번호를 제공하며, 회원은 택배사 홈페이지에서 실시간 배송 추적이 가능하다.

③ 배송비는 회사가 부담하며, 회원의 추가 비용 부담은 없다. 단, 긴급 배송(익일 배송)을 요청하는 경우 별도의 수수료가 부과될 수 있다.

④ 카드는 본인 또는 동거 가족이 수령할 수 있으며, 대리 수령 시 신분증 확인이 필요하다.

⑤ 배송 주소 변경은 카드 발송 전까지만 가능하며, 발송 후에는 택배사를 통한 주소 변경이 불가능하다.

⑥ 카드 수령 후에는 즉시 카드 뒷면에 서명하고, 앱 또는 ARS를 통해 카드를 활성화해야 사용이 가능하다.`,
    time: '배송 기간: 3-5 영업일',
    note: '배송비 무료 / 등기 배송으로 안전 배송'
  },
  {
    id: '4',
    title: '분실 카드 부정 사용 보상',
    keywords: ['#보상', '#부정사용', '#보험'],
    content: '분실 신고 후 발생한 부정 사용은 보험 처리로 보상 가능합니다.',
    systemPath: '보상관리 > 부정사용보상 > 보상신청 (단축키: Ctrl+I)',
    requiredChecks: [
      '✓ 분실 신고 접수 시각 확인 (시스템 자동 기록)',
      '✓ 부정 사용 거래 내역 확인 (금액, 시각, 가맹점)',
      '✓ 경찰서 분실 신고 확인서 (고액일 경우)',
      '✓ 보험 청구 서류 안내 및 이메일 발송'
    ],
    exceptions: [
      '⚠️ 신고 전 72시간 이전 거래: 회원 부담 50%',
      '⚠️ 가족/지인 사용: 보상 불가 (본인 책임)',
      '⚠️ 비밀번호 유출: 보상 제외 (회원 과실)'
    ],
    regulation: '카드 이용약관 제23조 (분실·도난 카드의 부정사용)',
    fullText: `제23조 (분실·도난 카드의 부정사용)

① 회원이 카드의 분실 또는 도난 사실을 회사에 신고한 경우, 회사는 신고 접수 시점 이후 발생한 제3자의 부정사용으로 인한 손해를 전액 부담한다.

② 신고 접수 시점 이전 72시간 이내에 발생한 부정사용 손해에 대해서는 회사가 가입한 보험을 통해 보상하며, 보상 한도는 거래 건당 100만원, 연간 1,000만원으로 한다.

③ 72시간 이전에 발생한 부정사용에 대해서는 회원이 50%를 부담하고, 회사가 50%를 부담한다.

④ 다음 각 호의 경우에는 회사가 책임을 지지 않는다:
   1. 회원의 고의 또는 중대한 과실로 카드가 분실 또는 도난된 경우
   2. 회원이 비밀번호를 제3자에게 누설하거나 카드에 비밀번호를 기재한 경우
   3. 회원의 가족, 동거인 등 회원과 생계를 같이하는 자가 사용한 경우

⑤ 보상 처리는 필요 서류 접수 후 7-10 영업일 내에 완료되며, 보상금은 회원의 카드 대금 청구액에서 차감된다.

⑥ 고액의 부정사용(100만원 초과)이 발생한 경우 경찰서 분실 신고 확인서를 제출해야 한다.`,
    time: '처리 기간: 7-10 영업일',
    note: '신고 후 72시간 내 거래는 100% 보상'
  }
];

const guidanceScript = '고객님, 카드 분실 신고 접수되었습니다. 즉시 카드 사용이 정지되며, 3-5일 내 재발급 카드가 등록된 주소로 배송됩니다.';

// STT 실시간 스트림 데이터 (시뮬레이션) - ⭐ 딜레이 추가 및 자연스러운 타이밍
const sttStreamData = [
  { text: '안녕하세요', delay: 3000, isKeyword: false },  // 3초 딜레이 후 시작
  { text: ' 고객님', delay: 3400, isKeyword: false },
  { text: ' 테디카드입니다', delay: 4000, isKeyword: false },
  { text: ' 카드를', delay: 5500, isKeyword: false },
  { text: ' 분실', delay: 6200, isKeyword: true },
  { text: '하셨다고요?', delay: 6800, isKeyword: false },
  { text: ' 분실신고', delay: 8000, isKeyword: true },
  { text: ' 접수', delay: 8700, isKeyword: false },
  { text: ' 도와드리겠습니다', delay: 9500, isKeyword: false },
  { text: ' 먼저', delay: 11000, isKeyword: false },
  { text: ' 본인', delay: 11500, isKeyword: false },
  { text: ' 확인을', delay: 12000, isKeyword: false },
  { text: ' 위해', delay: 12500, isKeyword: false },
  { text: ' 주민번호', delay: 13000, isKeyword: false },
  { text: ' 뒷자리', delay: 13500, isKeyword: false },
  { text: ' 4자리를', delay: 14000, isKeyword: false },
  { text: ' 말씀해주시겠어요?', delay: 14800, isKeyword: false },
  { text: ' 네', delay: 18000, isKeyword: false },
  { text: ' 확인되었습니다', delay: 18700, isKeyword: false },
  { text: ' 언제', delay: 20000, isKeyword: false },
  { text: ' 어디서', delay: 20500, isKeyword: false },
  { text: ' 분실', delay: 21000, isKeyword: true },
  { text: '하셨나요?', delay: 21600, isKeyword: false },
  { text: ' 오늘', delay: 24000, isKeyword: false },
  { text: ' 오전', delay: 24400, isKeyword: false },
  { text: ' 강남역', delay: 24900, isKeyword: false },
  { text: ' 근처에서', delay: 25500, isKeyword: false },
  { text: ' 분실', delay: 26100, isKeyword: true },
  { text: '하셨군요', delay: 26700, isKeyword: false },
  { text: ' 즉시정지', delay: 28000, isKeyword: true },
  { text: ' 처리해드리겠습니다', delay: 28900, isKeyword: false },
  { text: ' 최근', delay: 30500, isKeyword: false },
  { text: ' 3일간', delay: 31000, isKeyword: false },
  { text: ' 거래내역', delay: 31600, isKeyword: false },
  { text: ' 확인', delay: 32100, isKeyword: false },
  { text: ' 중입니다', delay: 32700, isKeyword: false },
  { text: ' 이상', delay: 35000, isKeyword: false },
  { text: ' 거래는', delay: 35500, isKeyword: false },
  { text: ' 발견되지', delay: 36000, isKeyword: false },
  { text: ' 않았습니다', delay: 36700, isKeyword: false },
  { text: ' 재발급', delay: 38500, isKeyword: true },
  { text: ' 신청하시겠습니까?', delay: 39400, isKeyword: false },
  { text: ' 네', delay: 42000, isKeyword: false },
  { text: ' 재발급', delay: 42500, isKeyword: true },
  { text: ' 신청', delay: 43000, isKeyword: false },
  { text: ' 도와드리겠습니다', delay: 43800, isKeyword: false },
  { text: ' 등록된', delay: 45500, isKeyword: false },
  { text: ' 주소로', delay: 46000, isKeyword: false },
  { text: ' 3-5', delay: 46500, isKeyword: false },
  { text: ' 영업일', delay: 47000, isKeyword: false },
  { text: ' 내', delay: 47400, isKeyword: false },
  { text: ' 배송', delay: 47900, isKeyword: true },
  { text: '됩니다', delay: 48500, isKeyword: false },
];

interface ChatMessage {
  id: number;
  type: 'user' | 'ai';
  text: string;
  timestamp: string;
}

// ⭐ 페르소나 기반 상담 안내 멘트 생성 함수
const getPersonaMessage = (baseMessage: string, traits: string[] = []) => {
  if (!traits || traits.length === 0) return baseMessage;

  // 1. 성격급함/실용주의 (N1) -> 핵심만 간결하게
  if (traits.some(t => ['성격급함', '신속처리', '결론중시', '급한 성향', '빠른 답변 선호'].includes(t))) {
    // 문장이 길면 첫 문장만 사용하거나 요약
    const summary = baseMessage.split(/(?:니다|시오)\./)[0] + '니다.';
    return `(핵심 요약) 고객님, 결론부터 말씀드리면 ${summary} 바로 처리해드리겠습니다.`;
  }

  // 2. 꼼꼼함/분석형 (C3) -> 상세하게, 절차 강조
  if (traits.some(t => ['꼼꼼함', '데이터중시', '절차중시', '상세설명선호', '기술 친화적'].includes(t))) {
    return `(상세 안내) 고객님, 문의하신 내용은 규정에 따라 정확하게 처리되며, ${baseMessage} 처리 과정은 문자로도 안내해 드립니다.`;
  }

  // 3. 불만/감정형 (S5) -> 공감, 사과 먼저
  if (traits.some(t => ['불만', '감정적', '보상심리', '화남', '불편'].includes(t))) {
    return `(공감 화법) 고객님, 많이 불편하셨겠습니다. 죄송합니다. ${baseMessage} 제가 책임지고 빠르게 해결해 드리겠습니다.`;
  }
  
  // 4. 친절/관계지향 (I2) -> 친근하게
  if (traits.some(t => ['친절함', '대화선호', '라포형성'].includes(t))) {
    return `(친근하게) 네, 고객님! 걱정 마세요. ${baseMessage} 제가 꼼꼼히 챙겨서 처리해 드리겠습니다.`;
  }

  return baseMessage;
};

export default function RealTimeConsultationPage() {
  const navigate = useNavigate();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const sttEndRef = useRef<HTMLDivElement>(null); // ⭐ STT 자동 스크롤용
  
  // ⭐ 드래그 관련 ref
  const currentSituationDragRef = useRef<HTMLDivElement>(null);
  const nextStepDragRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const startXRef = useRef(0);
  const scrollLeftRef = useRef(0);
  const dragDistanceRef = useRef(0); // 드래그 거리 추적
  const activeContainerRef = useRef<'current' | 'next' | null>(null); // 어느 컨테이너를 드래그 중인지
  
  // Sidebar Context 사용
  const { isSidebarExpanded } = useSidebar();
  
  // Local state
  const [isCallActive, setIsCallActive] = useState(false);
  const [callTime, setCallTime] = useState(0); // 0부터 시작
  const [memo, setMemo] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isLeftSidebarCollapsed, setIsLeftSidebarCollapsed] = useState(true); // ⭐ Phase 13: 최초 닫힌 상태로 시작
  const [selectedDetailCard, setSelectedDetailCard] = useState<ScenarioCard | null>(null);
  const [isEndCallModalOpen, setIsEndCallModalOpen] = useState(false); // 통화 종료 확인 모달
  const [isSaving, setIsSaving] = useState(false); // 저장 상태
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle'); // 저장 상태 표시
  
  // STT 실시간 분석 state ⭐ NEW
  const [sttTexts, setSttTexts] = useState<{text: string, isKeyword: boolean, speaker?: 'agent' | 'customer'}[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false); // 칸반보드 로딩 상태
  const [incomingKeywords, setIncomingKeywords] = useState<string[]>([]); // ⭐ 인입 키워드 (3개 고정)
  const [currentCase, setCurrentCase] = useState<string>(''); // ⭐ 현재 인입 케이스
  const [isKeywordDetected, setIsKeywordDetected] = useState(false); // ⭐ 키워드 감지 여부
  const [showNextStepCards, setShowNextStepCards] = useState(false); // ⭐ 다음 단계 카드 표시 여부
  const [consultationStartTime, setConsultationStartTime] = useState<string>(''); // ⭐ 상담 시작 시간 기록
  
  // ⭐ Phase 3: 시나리오 기반 시뮬레이션
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(null);
  const [currentStep, setCurrentStep] = useState(0); // 0: 대기, 1: Step1, 2: Step2, 3: Step3
  const [previousStep, setPreviousStep] = useState(0); // 이전 step (슬라이딩 방향 결정용)
  const [maxReachedStep, setMaxReachedStep] = useState(0); // 최대 도달 Step (STT 키워드로만 증가)
  const [customerInfo, setCustomerInfo] = useState(defaultCustomerInfo);
  const [recentConsultations, setRecentConsultations] = useState(defaultRecentConsultations);
  const [showCustomerInfo, setShowCustomerInfo] = useState(false); // 고객 정보 표시 여부
  const [showRecentConsultations, setShowRecentConsultations] = useState(false); // 최근 상담 내역 표시 여부
  const [displayedKeywords, setDisplayedKeywords] = useState<string[]>([]); // 실제 화면에 표시되는 키워드
  const [isExtractingKeywords, setIsExtractingKeywords] = useState(false); // 키워드 추출 중 로딩
  
  // ⭐ Phase 8-1: 참조 문서 추적 (Step별로 표시된 카드 ID 저장)
  const [referencedDocuments, setReferencedDocuments] = useState<{
    step1: string[];
    step2: string[];
    step3: string[];
  }>({ step1: [], step2: [], step3: [] });
  
  // 모바일 탭 상태 (모바일/태블릿 전용)
  const [mobileTab, setMobileTab] = useState<'customer' | 'consultation' | 'control'>('consultation');
  
  // 대기 콜 현황 상태
  const [waitingCalls, setWaitingCalls] = useState(getInitialWaitingCalls());
  const [totalWaitingCalls, setTotalWaitingCalls] = useState(
    getInitialWaitingCalls().reduce((sum, call) => sum + call.count, 0)
  );

  // 타이머 ref
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const waitingCallsTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Phase 3-2: 이미 표시된 STT 메시지 인덱스 추적
  const displayedSttIndexRef = useRef<number>(0);
  
  // ⭐ 단어 큐 시스템 (누락 방지)
  const wordQueueRef = useRef<Array<{
    text: string;
    isKeyword: boolean;
    speaker: 'agent' | 'customer';
    matchedKeyword?: string;
  }>>([]);
  const isProcessingQueueRef = useRef(false);

  // 대기 콜 실시간 타이머 (매초마다 대기 시간 증가)
  useEffect(() => {
    waitingCallsTimerRef.current = setInterval(() => {
      setWaitingCalls(prev => 
        prev.map(call => ({
          ...call,
          waitTimeSeconds: call.waitTimeSeconds + Math.floor(Math.random() * 3) // 랜덤하게 0-2초 증가
        }))
      );
    }, 1000);

    return () => {
      if (waitingCallsTimerRef.current) {
        clearInterval(waitingCallsTimerRef.current);
      }
    };
  }, []);

  // 통화 시작 시 타이머 시작
  useEffect(() => {
    if (isCallActive) {
      timerRef.current = setInterval(() => {
        setCallTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isCallActive]);

  // 메모 자동저장 (5초마다)
  useEffect(() => {
    const autoSaveTimer = setTimeout(() => {
      if (memo.trim()) {
        localStorage.setItem('currentConsultationMemo', memo);
      }
    }, 5000);

    return () => clearTimeout(autoSaveTimer);
  }, [memo]);

  // 페이지 로드 시 저장된 메모 불러오기
  useEffect(() => {
    const savedMemo = localStorage.getItem('currentConsultationMemo');
    if (savedMemo) {
      setMemo(savedMemo);
    }
    
    // 페이지 진입 시 항상 초기 상태로 설정 (새 상담 대기)
    // 이미 localStorage는 후처리에서 정리됨
  }, []);

  // ⭐ 단어 큐 처리 Interval (100ms마다 하나씩 꺼내서 state 업데이트)
  useEffect(() => {
    const queueInterval = setInterval(() => {
      if (wordQueueRef.current.length === 0 || isProcessingQueueRef.current) {
        return;
      }
      
      isProcessingQueueRef.current = true;
      const wordObj = wordQueueRef.current.shift()!;
      
      // State 업데이트
      setSttTexts(prev => [...prev, {
        text: wordObj.text,
        isKeyword: wordObj.isKeyword,
        speaker: wordObj.speaker,
      }]);
      
      // 키워드 처리
      if (wordObj.matchedKeyword && activeScenario) {
        // 현재 Step의 키워드 가져오기
        const currentStepData = activeScenario.steps[currentStep - 1];
        const currentStepKeywords = currentStepData ? currentStepData.keywords.map(k => k.text) : [];
        
        // 다음 Step의 키워드 가져오기 (있으면)
        const nextStepData = currentStep < activeScenario.steps.length ? activeScenario.steps[currentStep] : null;
        const nextStepKeywords = nextStepData ? nextStepData.keywords.map(k => k.text) : [];
        
        // ⭐ 다음 Step의 키워드가 감지되면 Step 전환
        if (nextStepKeywords.includes(wordObj.matchedKeyword)) {
          const nextStep = currentStep + 1;
          setPreviousStep(currentStep);
          setCurrentStep(nextStep);
          setMaxReachedStep(nextStep);
          setIncomingKeywords(nextStepKeywords);
          setDisplayedKeywords([wordObj.matchedKeyword]);
          setIsExtractingKeywords(false);
          setIsKeywordDetected(true);
          
          // ⭐ Phase 8-1: 참조 문서 추적 - 새 Step 진입 시 해당 Step의 카드 ID 저장
          if (nextStepData) {
            const stepKey = `step${nextStep}` as 'step1' | 'step2' | 'step3';
            const cardIds = [
              ...nextStepData.currentSituationCards.map(card => card.id),
              ...nextStepData.nextStepCards.map(card => card.id)
            ];
            setReferencedDocuments(prev => ({
              ...prev,
              [stepKey]: cardIds
            }));
          }
          
          setTimeout(() => {
            setShowNextStepCards(true);
          }, 800);
        }
        // ⭐ 현재 Step의 키워드가 감지되면 키워드만 추가
        else if (currentStepKeywords.includes(wordObj.matchedKeyword)) {
          setDisplayedKeywords(prev => {
            if (!prev.includes(wordObj.matchedKeyword!)) {
              const newKeywords = [...prev, wordObj.matchedKeyword!];
              
              // 첫 번째 키워드가 추가되면 칸반보드 즉시 표시
              if (prev.length === 0) {
                setIsKeywordDetected(true);
                setIsExtractingKeywords(false);
                setTimeout(() => {
                  setShowNextStepCards(true);
                }, 800);
              }
              
              return newKeywords;
            }
            return prev;
          });
        }
      }
      
      isProcessingQueueRef.current = false;
    }, 100); // 100ms마다 하나씩 처리 (타이핑 효과)
    
    return () => clearInterval(queueInterval);
  }, [activeScenario, currentStep]);

  // ⭐ STT 자동 스크롤 (최신 대화가 항상 보이도록)
  useEffect(() => {
    sttEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [sttTexts]);

  // ⭐ STT에서 키워드 감지 시 칸반보드 표시
  useEffect(() => {
    // STT에서 키워드가 하나라도 감지되면 칸반보드 ���시
    const hasKeyword = sttTexts.some(item => item.isKeyword);
    if (hasKeyword && !isKeywordDetected) {
      setIsKeywordDetected(true);
      // 현재 정보 카드 표시 후 1.2초 뒤에 다음 단계 카드 표시
      setTimeout(() => {
        setShowNextStepCards(true);
      }, 1200);
    }
  }, [sttTexts, isKeywordDetected]);

  // ⭐ 3단계: STT 실시간 스트림 시뮬레이션 (통화 시작 시)
  // Phase 3-2: 시나리오가 없을 때만 기존 로직 사용
  useEffect(() => {
    if (isCallActive && !activeScenario) {
      // 기존 로직: 시나리오가 없을 때만 실행
      // 초기화
      setSttTexts([]);
      setIsAnalyzing(true); // 로딩 시작
      setIsKeywordDetected(false); // 키워드 감지 초기화
      
      // 7초 후 로딩 종료 (첫 키워드 나온 직후)
      const analyzingTimer = setTimeout(() => {
        setIsAnalyzing(false);
      }, 7000);
      
      // STT 텍스트 순서대로 표시
      const timers = sttStreamData.map((item) => 
        setTimeout(() => {
          setSttTexts(prev => [...prev, { text: item.text, isKeyword: item.isKeyword }]);
        }, item.delay)
      );
      
      return () => {
        clearTimeout(analyzingTimer);
        timers.forEach(timer => clearTimeout(timer));
      };
    } else if (!isCallActive) {
      // 통화 종료 시 초기화
      setSttTexts([]);
      setIsAnalyzing(false);
      setIsKeywordDetected(false);
      setShowNextStepCards(false);
      
      // Phase 3: 시나리오 관련 초기화
      setShowCustomerInfo(false);
      setShowRecentConsultations(false);
      setDisplayedKeywords([]);
      setIsExtractingKeywords(false);
      setActiveScenario(null);
      setCurrentStep(0);
      setPreviousStep(0);
      setMaxReachedStep(0); // 최대 도달 Step 초기화
      displayedSttIndexRef.current = 0; // Phase 3-2: STT 인덱스 초기화
    }
  }, [isCallActive, activeScenario]);

  // ⭐ ESC 키로 모달 닫기
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (selectedDetailCard) {
          setSelectedDetailCard(null);
        } else if (isEndCallModalOpen) {
          setIsEndCallModalOpen(false);
        }
      }
      // ⭐ Phase 8-3: Enter 키로 모달 확인 버튼 실행
      if (event.key === 'Enter' && isEndCallModalOpen) {
        event.preventDefault();
        handleConfirmEndCall();
      }
    };

    window.addEventListener('keydown', handleEscKey);
    return () => window.removeEventListener('keydown', handleEscKey);
  }, [selectedDetailCard, isEndCallModalOpen]);

  // ⭐ Phase 3-2: 타임라인 기반 STT 시뮬레이션 (시나리오가 있을 때)
  // 기존 형식 유지: 텍스트를 단어 단위로 쪼개서 스트림, 키워드는 태그로 표시
  useEffect(() => {
    if (!isCallActive || !activeScenario) return;

    // ⭐ 상담사 이름 동적 교체 (TODO: 로그인한 상담사 이름으로 교체)
    const loggedInAgentName = "김현우"; // TODO: Auth Context에서 가져오기 (예: useAuth().user.name)
    const sttMessages = activeScenario.sttDialogue.map(msg => {
      if (msg.speaker === 'agent' && msg.message.includes('상담사')) {
        // "상담사 XXX입니다" 패턴을 찾아서 로그인한 상담사 이름으로 교체
        const replacedMessage = msg.message.replace(/상담사\s+\S+입니다/, `상담사 ${loggedInAgentName}입니다`);
        return { ...msg, message: replacedMessage };
      }
      return msg;
    });
    
    // 키워드 매핑: "카드분실" → ["카드", "잃어버렸", "분실"]
    const keywordMap: Record<string, string[]> = {
      '카드분실': ['잃어버렸', '분실'],
      '긴급정지': ['정지'],
      '본인확인': ['생년월일'],
      '재발급': ['재발급'],
      '해외출장': ['출장'],
      '긴급배송': ['임시카드', '임시'],
      '출국일정': ['인천공항'],
      '라운지위치': ['테디라운지', '터미널'],
      '수령완료': ['수령', '감사합니다'],
      '해외결제': ['일본', '도쿄'],
      '카드차단': ['차단', '되네요'],
      '일본': ['일본', '도쿄'],
      '재설정완료': ['재설정', '활성화'],
      'SMS승인': ['SMS'],
      '알림서비스': ['알림서비스'],
      '설정완료': ['설정완료'],
      '정상사용': ['정상사용'],
      '연회비': ['연회비'],
      '청구': ['청구'],
      '면제': ['면제'],
      '환불': ['환불'],
      '실적충족': ['실적충족'],
      '추가사용': ['추가사용'],
      '이해완료': ['알겠습니다'],
      '안내완료': ['안내완료'],
      '한도증액': ['증액'],
      '신용평가': ['신용평가', '심사'],
      '심사': ['심사'],
      '증액가능': ['증액가능'],
      '700만원': ['700만원'],
      '즉시증액': ['즉시증액'],
      '증액완료': ['증액되었습니다'],
      '사용가능': ['사용가능'],
      '연체': ['연체'],
      '결제지연': ['결제지연'],
      '납부': ['납부'],
      '가상계좌': ['가상계좌'],
      '입금': ['입금'],
      '즉시납부': ['즉시납부'],
      '납부완료': ['납부완료'],
      '신용등급': ['신용등급'],
      '결제일': ['결제일'],
      '변경': ['변경'],
      '급여일': ['급여일'],
      '27일': ['27일'],
      '변경완료': ['변경완료'],
      '다음달적용': ['다음달적용'],
      '적용완료': ['적용완료'],
    };
    
    // ⭐ 모든 Step의 키워드 가져오기 (현재 + 다음 Step 모두)
    const allStepKeywords: string[] = [];
    activeScenario.steps.forEach(step => {
      allStepKeywords.push(...step.keywords.map(k => k.text));
    });
    
    for (let i = displayedSttIndexRef.current; i < sttMessages.length; i++) {
      const sttItem = sttMessages[i];
      
      // ⭐ 현재 통화 시간이 메시지 타임스탬프에 도달하지 않았으면 루프 중단
      if (callTime < sttItem.timestamp) {
        break;
      }
      
      // ⭐ 타임스탬프에 도달했으므로 이 메시지의 모든 단어를 큐에 추가
      const words = sttItem.message.split(' ');
      
      words.forEach((word) => {
        // 키워드인지 확인: 모든 Step의 키워드와 매칭
        let isKeyword = false;
        let matchedKeyword = '';
        
        allStepKeywords.forEach(kw => {
          const mappedWords = keywordMap[kw] || [kw];
          if (mappedWords.some(mapped => word.includes(mapped))) {
            isKeyword = true;
            matchedKeyword = kw;
          }
        });
        
        // 큐에 추가
        wordQueueRef.current.push({
          text: word + ' ',
          isKeyword,
          speaker: sttItem.speaker,
          matchedKeyword,
        });
      });
      
      // 이 메시지를 처리했으므로 인덱스 증가
      displayedSttIndexRef.current = i + 1;
    }
  }, [callTime, isCallActive, activeScenario, currentStep]);

  // ⭐ Phase 3-4: 다단계 카드 시스템 - Step 자동 전환 (비활성화 - STT 키워드 기반 전환으로 대체)
  // 이제 STT에서 실제로 다음 Step의 키워드가 감지될 때만 Step이 전환됩니다.

  const handleStartCall = () => {
    // 상태 초기화
    setIsKeywordDetected(false);
    setShowNextStepCards(false);
    setIsCallActive(true);
    setCallTime(0); // 타이머 리셋
    
    // ⭐ Phase 13: 통화 시작 시 고객 정보 섹션 열기
    setIsLeftSidebarCollapsed(false);
    
    // ⭐ 큐 초기화
    wordQueueRef.current = [];
    isProcessingQueueRef.current = false;
    
    // ⭐ Phase 8-1: 클릭된 문서 목록 초기화
    localStorage.removeItem('clickedDocuments');
    
    // ⭐ 상담 메모 초기화
    setMemo('');
    localStorage.removeItem('consultationMemo');
    
    // ⭐ Phase 8-1: Step1의 카드 ID 저장 (통화 시작 시)
    if (activeScenario && activeScenario.steps.length > 0) {
      const step1Data = activeScenario.steps[0];
      const cardIds = [
        ...step1Data.currentSituationCards.map(card => card.id),
        ...step1Data.nextStepCards.map(card => card.id)
      ];
      setReferencedDocuments({
        step1: cardIds,
        step2: [],
        step3: []
      });
    }
  };

  const handleCopyScript = () => {
    navigator.clipboard.writeText(guidanceScript);
  };

  // ⭐ 드래그 시작 - Step 전환용
  const handleStepDragStart = (e: React.MouseEvent, container: 'current' | 'next') => {
    isDraggingRef.current = true;
    startXRef.current = e.pageX;
    dragDistanceRef.current = 0;
    activeContainerRef.current = container;
    e.currentTarget.style.cursor = 'grabbing';
  };

  // ⭐ 드래그 중 - Step 전환용
  const handleStepDragMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    e.preventDefault();
    const distance = e.pageX - startXRef.current;
    dragDistanceRef.current = distance;
  };

  // ⭐ 드래그 종료 - Step 전환용
  const handleStepDragEnd = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    isDraggingRef.current = false;
    activeContainerRef.current = null;
    e.currentTarget.style.cursor = 'grab';
    
    const threshold = 100; // 100px 이상 드래그하면 Step 전환
    
    if (Math.abs(dragDistanceRef.current) > threshold && activeScenario) {
      // 우→좌 드래그 (dragDistance > 0): 이전 Step으로 이동
      if (dragDistanceRef.current > 0 && currentStep > 1) {
        setPreviousStep(currentStep);
        setCurrentStep(currentStep - 1);
        
        // 이전 Step으로 이동 시 키워드는 즉시 전체 표시 (애니메이션 스킵)
        const prevStepData = activeScenario.steps[currentStep - 2]; // currentStep은 아직 업데이트 안됨
        if (prevStepData) {
          const prevStepKeywords = prevStepData.keywords.map(k => k.text);
          setIncomingKeywords(prevStepKeywords);
          setDisplayedKeywords(prevStepKeywords); // 즉시 전체 표시
          setIsExtractingKeywords(false); // 추출 완료 상태
        }
      } 
      // 좌→우 드래그 (dragDistance < 0): 다음 Step으로 이동 (이미 도달한 Step까지만)
      else if (dragDistanceRef.current < 0 && currentStep < maxReachedStep) {
        setPreviousStep(currentStep);
        setCurrentStep(currentStep + 1);
        
        // 이미 도달한 Step으로 이동하므로 키워드 즉시 전체 표시
        const nextStepData = activeScenario.steps[currentStep]; // currentStep은 아직 업데이트 안됨
        if (nextStepData) {
          const nextStepKeywords = nextStepData.keywords.map(k => k.text);
          setIncomingKeywords(nextStepKeywords);
          setDisplayedKeywords(nextStepKeywords); // 즉시 전체 표시
          setIsExtractingKeywords(false); // 추출 완료 상태
        }
      }
    }
    
    dragDistanceRef.current = 0;
  };

  // ⭐ Progress bar 클릭 핸들러
  const handleProgressClick = (stepIndex: number) => {
    if (!activeScenario) return;
    
    const targetStep = stepIndex + 1; // stepIndex는 0부터 시작, currentStep은 1부터 시작
    
    // 아직 도달하지 않은 Step은 클릭 불가 (STT 키워드로만 전환 가능)
    if (targetStep > maxReachedStep) return;
    
    // 같은 Step 클릭 시 아무 작업 안함
    if (targetStep === currentStep) return;
    
    // 이미 도달한 Step으로 이동
    setPreviousStep(currentStep);
    setCurrentStep(targetStep);
    
    // 이미 도달한 Step이므로 키워드는 즉시 전체 표시 (애니메이션 스킵)
    const targetStepData = activeScenario.steps[stepIndex];
    if (targetStepData) {
      const targetStepKeywords = targetStepData.keywords.map(k => k.text);
      setIncomingKeywords(targetStepKeywords);
      setDisplayedKeywords(targetStepKeywords); // 즉시 전체 표시
      setIsExtractingKeywords(false); // 추출 완료 상태
    }
  };

  const handleEndCallClick = () => {
    // 통화 종료 확인 모달 열기
    setIsEndCallModalOpen(true);
  };

  const handleConfirmEndCall = () => {
    // 메모를 localStorage에 저장하고 후처리로 이동
    if (memo.trim()) {
      localStorage.setItem('currentConsultationMemo', memo);
    }
    localStorage.setItem('consultationCallTime', callTime.toString());
    
    // ⭐ Phase 8-1: 참조 문서 저장
    if (activeScenario) {
      const referencedDocs: Array<{
        stepNumber: number;
        documentId: string;
        title: string;
        used: boolean;
      }> = [];
      
      // 각 Step별로 현재 상황 관련 정보 카드만 저장 (최대 도달한 Step까지)
      for (let i = 0; i < maxReachedStep; i++) {
        const stepData = activeScenario.steps[i];
        if (stepData) {
          // ⭐ currentSituationCards만 저장 (다음 예상 정보는 제외)
          stepData.currentSituationCards.forEach(card => {
            referencedDocs.push({
              stepNumber: stepData.stepNumber,
              documentId: card.id,
              title: card.title,
              used: true  // 표시된 카드는 모두 사용된 것으로 간주
            });
          });
        }
      }
      
      localStorage.setItem('referencedDocuments', JSON.stringify(referencedDocs));
      localStorage.setItem('currentScenarioCategory', activeScenario.category);
    }
    
    setIsCallActive(false);
    setIsEndCallModalOpen(false);
    
    // ⭐ �� 초기화
    wordQueueRef.current = [];
    isProcessingQueueRef.current = false;
    
    // ⭐ Phase 8-3: Frontend 데이터 생성 및 저장
    const employeeId = localStorage.getItem('employeeId') || 'EMP-001';
    const consultationId = generateConsultationId(employeeId);
    
    // ⭐ 저장된 시작 시간 사용 (없으면 현재 시간 - 방어 코드)
    let datetime = consultationStartTime;
    if (!datetime) {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hour = String(now.getHours()).padStart(2, '0');
      const minute = String(now.getMinutes()).padStart(2, '0');
      datetime = `${year}-${month}-${day} ${hour}:${minute}`;
    }
    
    const frontendData = {
      consultationId,
      employeeId,
      customerId: customerInfo.id,
      customerName: customerInfo.name,
      customerPhone: customerInfo.phone,
      category: activeScenario?.category || '일반문의',
      datetime,
      callTime,
      memo: memo.trim(),
    };
    localStorage.setItem('pendingConsultation', JSON.stringify(frontendData));
    console.log('📝 Frontend 데이터 저장 (새 형식):', frontendData);
    
    // ⭐ Phase 8-3: 로딩 페이지로 이동
    navigate('/loading', { state: { consultationId, estimatedTime: 5 } });
    
    // ⭐ Mock LLM 응답 (12초 후 - 로딩 페이지 10초 + 여유 2초)
    setTimeout(() => {
      const llmData = {
        title: '카드 분실 신고 및 재발급 처리',
        status: '완료',
        aiSummary: '문의사항: 고객이 카드를 분실하여 즉시 사용 정지 및 재발급 요청\n\n처리 결과: 카드 사용 즉시 정지 처리 완료. 재발급 카드 신청 접수하였으며, 등록된 주소(서울시 강남구 테헤란로 123)로 3-5일 내 배송 예정. 고객에게 배송 추적 안내 완료.',
        followUpTasks: '',
        handoffDepartment: '없음',
        handoffNotes: '',
      };
      localStorage.setItem('llmAnalysisResult', JSON.stringify(llmData));
      window.dispatchEvent(new CustomEvent('llmAnalysisComplete', { detail: llmData }));
      console.log('🤖 LLM 분석 완료 (Mock):', llmData);
    }, 12000);
  };

  const handleCancelEndCall = () => {
    setIsEndCallModalOpen(false);
  };

  // ⭐ Phase 8-1: 문서 클릭 추적 핸들러
  const handleCardClick = (card: ScenarioCard) => {
    setSelectedDetailCard(card);
    
    // localStorage에서 클릭된 문서 ID 목록 가져오기
    const clickedDocsStr = localStorage.getItem('clickedDocuments');
    let clickedDocs: string[] = [];
    
    if (clickedDocsStr) {
      try {
        clickedDocs = JSON.parse(clickedDocsStr);
      } catch (error) {
        console.error('클릭된 문서 파싱 오류:', error);
      }
    }
    
    // 중복 제거하고 맨 앞에 추가
    clickedDocs = clickedDocs.filter(id => id !== card.id);
    clickedDocs.unshift(card.id);
    
    // localStorage에 저장
    localStorage.setItem('clickedDocuments', JSON.stringify(clickedDocs));
  };

  const handleSaveMemo = () => {
    if (!memo.trim()) return;
    
    setSaveStatus('saving');
    
    // 메모 저장 (localStorage)
    localStorage.setItem('currentConsultationMemo', memo);
    
    // 저장 완료 표시 (1.5초 후 idle로 복귀)
    setTimeout(() => {
      setSaveStatus('saved');
      setTimeout(() => {
        setSaveStatus('idle');
      }, 2000);
    }, 500);
  };

  const handleSearch = () => {
    if (!searchQuery.trim()) return;

    const now = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    
    // 사용자 질문 추가
    const userMessage: ChatMessage = {
      id: Date.now(),
      type: 'user',
      text: searchQuery,
      timestamp: now
    };
    
    setChatMessages(prev => [...prev, userMessage]);

    // AI 답변 시���레이션
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: Date.now() + 1,
        type: 'ai',
        text: getAIResponse(searchQuery),
        timestamp: now
      };
      setChatMessages(prev => [...prev, aiMessage]);
    }, 500);

    setSearchQuery('');
  };

  const getAIResponse = (query: string): string => {
    if (query.includes('재발급') || query.includes('배송')) {
      return '재발급 카드는 신청 후 3-5 영업일 내 등록된 주소로 배송됩니다. 배송비는 무료이며, 택배 추적 번호는 SMS로 발송됩니다.';
    } else if (query.includes('수수료') || query.includes('연회비')) {
      return '연회비는 카 발급 후 1년 후 청구됩니다. 전년도 실적 조건을 충족하면 면제됩니다. 실적 기준은 월 30만원 이상 사용입니다.';
    } else if (query.includes('해외') || query.includes('결제')) {
      return '해외 결제는 기본적으로 활성화되어 있습니다. 단, 일부 국가는 보안 정책으로 인해 사전 승인이 필요할 수 있습니다. 고객센터에서 즉시 해제 가능합니다.';
    } else {
      return '해당 내용에 대한 자세한 정보를 찾았습니다. 추가 문의 사항이 있으시면 말씀해주세요.';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  // 대기 콜 클릭 시 통화 연결
  const handleCallConnect = (category: string) => {
    if (isCallActive) {
      toast.warning('이미 통화 중입니다.', {
        description: '현재 통화를 종료한 후 다시 시도해주세요.',
        duration: 2000,
      });
      return;
    }

    // ⭐ Phase 8-1: 새 상담 시작 시 localStorage 초기화 (클릭 추적 등)
    localStorage.removeItem('clickedDocuments');
    localStorage.removeItem('currentConsultationMemo');
    localStorage.removeItem('consultationCallTime');
    localStorage.removeItem('referencedDocuments');
    localStorage.removeItem('currentScenarioCategory');
    localStorage.removeItem('consultationMemo');
    
    console.log('🔄 새 상담 시작: localStorage 초기화 완료');

    // ⭐ 즉시 초기화 (React 배치 업데이트 방지)
    setDisplayedKeywords([]);
    setIncomingKeywords([]);
    setMemo('');
    setIsExtractingKeywords(false);
    setIsKeywordDetected(false);
    setShowNextStepCards(false);
    setShowCustomerInfo(false);
    setShowRecentConsultations(false);
    
    // ⭐ Phase 13: 대기콜 연결 시 고객 정보 섹션 열기
    setIsLeftSidebarCollapsed(false);
    
    // ⭐ Phase 3-2: STT 초기화
    setSttTexts([]);
    displayedSttIndexRef.current = 0;

    // ⭐ Phase 3: 시나리오 로드
    const scenario = getScenarioByCategory(category);
    if (scenario) {
      setActiveScenario(scenario);
      setPreviousStep(0); // 이전 스텝 초기화
      setCurrentStep(1); // Step 1 시작
      setMaxReachedStep(1); // 최대 도달 Step은 Step 1
      
      // 고객 정보 변경 (즉시 변경, 표시는 타이머로)
      setCustomerInfo({
        id: scenario.customer.id,
        name: scenario.customer.name,
        phone: scenario.customer.phone,
        birthDate: scenario.customer.birthDate || '1990-03-15',
        address: scenario.customer.address || '서울시 강남구 테헤란로 123',
        cardName: scenario.customer.cardName,
        cardNumber: scenario.customer.cardNumber,
        cardIssueDate: scenario.customer.cardIssueDate,
        cardExpiryDate: scenario.customer.cardExpiryDate,
      });
      
      // 최근 상담 내역 변경
      setRecentConsultations(
        scenario.recentConsultations.map((consult, idx) => ({
          id: idx + 1,
          title: consult.content,
          date: consult.date,
          category: consult.category,
          status: '완료',
        }))
      );
      
      // Step 1의 키워드 설정 (STT에서 실시간으로 감지하므로 빈 배열로 시작)
      const step1Keywords = scenario.steps[0].keywords.map(k => k.text);
      setIncomingKeywords(step1Keywords);
      setDisplayedKeywords([]); // 빈 배열로 시작 - STT에서 실시간 감지
      setIsExtractingKeywords(true); // 키워드 추출 중 상태
      
      // ⭐ Phase 3-1.5: 순차적 등장 애니메이션
      // 1. 고객 정보 표시 (500ms 후)
      setTimeout(() => {
        setShowCustomerInfo(true);
      }, 500);
      
      // 2. 최근 상담 내역 표시 (1000ms 후)
      setTimeout(() => {
        setShowRecentConsultations(true);
      }, 1000);
    } else {
      // 시나리오가 없는 경우 기본값 (기존 로직)
      setIncomingKeywords(incomingKeywordsByCase[category] || []);
      setDisplayedKeywords([]); // 빈 배열로 시작 - STT에서 실시간 감지
      setIsExtractingKeywords(true); // 키워드 추출 중 상태
      
      // 기본값도 순차 표시
      setTimeout(() => {
        setShowCustomerInfo(true);
      }, 500);
      setTimeout(() => {
        setShowRecentConsultations(true);
      }, 1000);
    }

    // ⭐ 인입 케이스 설정
    setCurrentCase(category);

    // ⭐ 상담 시작 시간 기록
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    setConsultationStartTime(`${year}-${month}-${day} ${hour}:${minute}`);

    // 상태 초기화
    setIsKeywordDetected(false);
    setShowNextStepCards(false);

    // 통화 시작
    setIsCallActive(true);
    setCallTime(0);

    // 해당 카테고리 count -1
    setWaitingCalls(prev =>
      prev.map(call =>
        call.category === category && call.count > 0
          ? { ...call, count: call.count - 1 }
          : call
      )
    );

    // 총 대기 콜 수 업데이트
    setTotalWaitingCalls(prev => Math.max(0, prev - 1));
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  return (
    <MainLayout>
      <style>{`
        @keyframes wave-pulse {
          0% {
            box-shadow: 0 0 0 0 rgba(0, 71, 171, 0.1), 
                        0 0 0 0 rgba(0, 71, 171, 0.1);
          }
          40% {
            box-shadow: 0 0 0 10px rgba(0, 71, 171, 0), 
                        0 0 0 0 rgba(0, 71, 171, 0.1);
          }
          80% {
            box-shadow: 0 0 0 10px rgba(0, 71, 171, 0), 
                        0 0 0 20px rgba(0, 71, 171, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(0, 71, 171, 0), 
                        0 0 0 20px rgba(0, 71, 171, 0);
          }
        }
        .animate-wave-pulse {
          animation: wave-pulse 2.5s infinite cubic-bezier(0.4, 0, 0.6, 1);
        }
      `}</style>
      {/* 폴딩 버튼 - MainLayout 바로 아래, 메인 컨테이너 밖에 위치 */}
      <button
        onClick={() => setIsLeftSidebarCollapsed(!isLeftSidebarCollapsed)}
        className="hidden lg:flex fixed top-1/2 -translate-y-1/2 w-6 h-6 bg-white border border-[#D1D5DB] text-[#666666] rounded-full items-center justify-center hover:border-[#0047AB] hover:text-[#0047AB] hover:shadow-md transition-all duration-300 shadow-lg"
        style={{ 
          marginTop: '30px',
          left: `${
            (isSidebarExpanded ? 200 : 56) + (isLeftSidebarCollapsed ? -12 : 200 - 12)
          }px`,
          zIndex: 60
        }}
      >
        <ChevronLeft 
          className={`w-3.5 h-3.5 transition-transform duration-300 ${
            isLeftSidebarCollapsed ? 'rotate-180' : ''
          }`}
        />
      </button>

      <div 
        className="flex bg-[#F5F5F5] fixed top-[60px] right-0 bottom-0 overflow-hidden transition-all duration-300"
        style={{ 
          left: `${isSidebarExpanded ? 200 : 56}px`
        }}
      >
        {/* 모바일/태블릿 탭 네비게이션 (lg 미만에서만 표시) */}
        <div className="lg:hidden fixed top-[60px] left-0 right-0 bg-white border-b border-[#E0E0E0] z-[40]">
          {/* 통화 상태 표시 (통화 중일 때만) */}
          {isCallActive && (
            <div className="bg-gradient-to-r from-[#34A853] to-[#2E7D32] text-white px-4 py-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span className="text-xs font-bold">통화 중</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold tabular-nums">{formatTime(callTime)}</span>
                <button 
                  onClick={handleEndCallClick}
                  className="w-7 h-7 bg-[#EA4335] rounded-lg flex items-center justify-center hover:bg-[#C62828] transition-all"
                  title="통화 종료"
                >
                  <PhoneOff className="w-3.5 h-3.5 text-white" />
                </button>
              </div>
            </div>
          )}
          
          {/* 탭 버튼들 */}
          <div className="flex">
            <button
              onClick={() => setMobileTab('customer')}
              className={`flex-1 px-4 py-3 text-xs font-medium transition-colors ${
                mobileTab === 'customer'
                  ? 'text-[#0047AB] border-b-2 border-[#0047AB] bg-[#F8FBFF]'
                  : 'text-[#666666] hover:text-[#333333] hover:bg-[#F5F5F5]'
              }`}
            >
              고객정보
            </button>
            <button
              onClick={() => setMobileTab('consultation')}
              className={`flex-1 px-4 py-3 text-xs font-medium transition-colors ${
                mobileTab === 'consultation'
                  ? 'text-[#0047AB] border-b-2 border-[#0047AB] bg-[#F8FBFF]'
                  : 'text-[#666666] hover:text-[#333333] hover:bg-[#F5F5F5]'
              }`}
            >
              상담내용
            </button>
            <button
              onClick={() => setMobileTab('control')}
              className={`flex-1 px-4 py-3 text-xs font-medium transition-colors ${
                mobileTab === 'control'
                  ? 'text-[#0047AB] border-b-2 border-[#0047AB] bg-[#F8FBFF]'
                  : 'text-[#666666] hover:text-[#333333] hover:bg-[#F5F5F5]'
              }`}
            >
              메모/검색
            </button>
          </div>
        </div>

        {/* 좌측 열 - 고객정보 (데스크톱: 조건부 표시, 모바일: 탭 전환) */}
        <div 
          className={`
            bg-[#FAFAFA] border-r border-[#E0E0E0] flex flex-col transition-all duration-300 relative
            ${mobileTab === 'customer' ? 'flex' : 'hidden lg:flex'}
            ${isLeftSidebarCollapsed ? 'lg:w-0' : 'lg:w-[200px]'}
            w-full ${isCallActive ? 'mt-[89px]' : 'mt-[49px]'} lg:mt-0
            h-full overflow-hidden
          `}
        >
          <div className={`w-full lg:w-[200px] p-3 flex flex-col h-full overflow-y-auto ${isLeftSidebarCollapsed ? 'lg:opacity-0' : 'lg:opacity-100'}`}>
            {/* 고객 정보 - Phase 10-5: 2열 레이아웃 + 나이 표시 */}
            {showCustomerInfo && (
              <div className="flex-shrink-0 animate-[slideInFromTop_0.5s_ease-out] mb-3">
                <h3 className="text-xs font-bold text-[#333333] mb-2">고객 정보</h3>
                <div className="bg-white rounded-lg border border-[#E0E0E0] p-2.5">
                  <div className="space-y-1 text-[10px]">
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">이름:</span>
                      {USE_CUSTOMER_MASKING ? (
                        <InlineMaskedText
                          originalText={customerInfo.name}
                          maskedText={maskName(customerInfo.name)}
                          duration={3000}
                        />
                      ) : (
                        <span className="text-[#666666]">{customerInfo.name}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">전화:</span>
                      {USE_CUSTOMER_MASKING ? (
                        <InlineMaskedText
                          originalText={customerInfo.phone}
                          maskedText={maskPhone(customerInfo.phone)}
                          duration={3000}
                        />
                      ) : (
                        <span className="text-[#666666]">{customerInfo.phone}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">생년월일:</span>
                      <span className="text-[#666666] text-[10px] truncate">{customerInfo.birthDate ? formatBirthDateWithAge(customerInfo.birthDate) : '-'}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">주소:</span>
                      <span className="text-[#666666] text-[10px] truncate" title={customerInfo.address}>{customerInfo.address || '-'}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">소지카드:</span>
                      <span className="text-[#666666] text-[10px] truncate">{customerInfo.cardName || '-'}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">카드번호:</span>
                      <span className="text-[#666666] text-[10px] truncate">{customerInfo.cardNumber || '-'}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">발급일:</span>
                      <span className="text-[#666666] text-[10px]">{customerInfo.cardIssueDate || '-'}</span>
                    </div>
                    <div className="flex items-center gap-0.5">
                      <span className="font-medium text-[#333333] w-11 shrink-0">만료일:</span>
                      <span className="text-[#666666] text-[10px]">{customerInfo.cardExpiryDate || '-'}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ⭐ Phase 9: 고객 특성 가이드 - 고객 정보 바로 아래 표시 */}
            {showCustomerInfo && activeScenario && activeScenario.customer.traits && activeScenario.customer.traits.length > 0 && (
              <div className="flex-shrink-0 animate-[slideInFromTop_0.5s_ease-out] mt-3">
                <h3 className="text-xs font-bold text-[#333333] mb-2">고객 특성 가이드</h3>
                
                <div className="bg-white rounded-md border border-[#E0E0E0] p-2.5">
                  {/* 태그 표시 - 최대 4개, 2열 그리드 */}
                  <div className="grid grid-cols-2 gap-1.5 mb-2">
                    {activeScenario.customer.traits.slice(0, 4).map((trait, index) => {
                      const colors = getTraitColor(trait);
                      return (
                        <span
                          key={index}
                          className="px-2 py-0.5 rounded text-[10px] font-medium text-center"
                          style={{ 
                            backgroundColor: colors.bg,
                            color: colors.text
                          }}
                        >
                          {trait}
                        </span>
                      );
                    })}
                  </div>

                  {/* 상담 가이드 */}
                  <p className="text-[11px] text-[#333333] leading-relaxed">
                    {activeScenario.customer.preferredStyle || 
                     `${getCustomerTraitSummary(activeScenario.customer)} 특성이 있습니다.`}
                  </p>
                </div>
              </div>
            )}

            {/* 최근 상담 내역 - Phase 3-1.5: 고객 정보 후 등장 */}
            {showRecentConsultations && (
              <div className="flex-shrink-0 animate-[slideInFromTop_0.5s_ease-out] mt-3">
                <h3 className="text-xs font-bold text-[#333333] mb-2">최근 상담 내역</h3>
                <div className="space-y-2">
                  {recentConsultations.map((item) => (
                    <div 
                      key={item.id}
                      className={`bg-white rounded-md p-2 cursor-pointer hover:bg-[#F8F9FA] border-l-3 ${
                        item.status === '완료' ? 'border-l-[#34A853]' : 'border-l-[#4A90E2]'
                      }`}
                      style={{ borderLeftWidth: '3px' }}
                    >
                      <div className="text-[11px] text-[#333333] line-clamp-2 mb-1 leading-relaxed">{item.title}</div>
                      <div className="text-[10px] text-[#999999] mb-1">{item.date}</div>
                      <span className="text-[10px] px-1.5 py-0.5 bg-[#E8F1FC] text-[#0047AB] rounded">
                        {item.category}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 중앙 열 - 동적 너비 (데스크톱: 동적, 모바일: 탭 전환) */}
        <div className={`
          bg-white p-5 transition-all duration-300 flex flex-col
          ${mobileTab === 'consultation' ? 'flex' : 'hidden lg:flex'}
          ${isLeftSidebarCollapsed ? 'lg:w-[calc(75%-0px)]' : 'lg:w-[calc(75%-200px)]'}
          w-full ${isCallActive ? 'mt-[89px]' : 'mt-[49px]'} lg:mt-0
          h-full overflow-y-auto
        `}>
          {/* ⭐ 대기 콜 현황 및 상담 대기중 UI */}
          {!isCallActive && (
            <div className="flex flex-col h-full">
              {/* 대기 콜 현황 */}
              <div className="flex-shrink-0 mb-4">
                <div className="bg-gradient-to-r from-[#F8FBFF] to-[#F0F7FF] rounded-lg p-4 shadow-sm border border-[#E0E0E0]">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-bold text-[#0047AB]">📞 대기 콜 현황</h3>
                    <span className="bg-[#FFE6E6] text-[#D32F2F] text-xs font-bold px-2.5 py-1 rounded-full">
                      {totalWaitingCalls}건
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {waitingCalls.map((call, index) => (
                      <div 
                        key={index}
                        className={`bg-white rounded-lg p-3 cursor-pointer hover:shadow-lg hover:border-[#0047AB]/50 transition-all border-2 ${
                          call.priority === 'urgent' ? 'border-l-4 border-l-[#FF6B6B] border-[#FFE6E6]' : 'border-[#E0E0E0]'
                        }`}
                        title={`${call.category} - ${formatTime(call.waitTimeSeconds)} 대기 중`}
                        onClick={() => handleCallConnect(call.category)}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-[#333333]">{call.category}</span>
                          <span 
                            className="text-xs font-bold px-2 py-0.5 rounded-full"
                            style={{ 
                              backgroundColor: call.priority === 'urgent' ? '#FFE6E6' : '#E8F1FC', 
                              color: call.priority === 'urgent' ? '#D32F2F' : '#0047AB'
                            }}
                          >
                            {call.count}건
                          </span>
                        </div>
                        <div className="text-[11px] text-[#666666] flex items-center gap-1">
                          <span>⏱️ 대기시간:</span>
                          <span className={`font-semibold ${call.priority === 'urgent' ? 'text-[#D32F2F]' : 'text-[#0047AB]'}`}>
                            {formatTime(call.waitTimeSeconds)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* ⭐ Phase 14: 상담 시작 안내 - 수직 중앙 배치 */}
              <div className="flex-1 flex items-center justify-center min-h-[300px]">
                <div className="text-center max-w-md">
                  <div className="w-20 h-20 mx-auto mb-8 bg-gradient-to-br from-[#0047AB] to-[#003580] rounded-full flex items-center justify-center shadow-lg animate-wave-flow">
                    <Phone className="w-9 h-9 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-[#0047AB] mb-4">상담 대기 중</h2>
                  <p className="text-base text-[#666666] mb-2">위의 대기 콜 현황에서 상담을 선택하거나</p>
                  <p className="text-base text-[#666666]">통화 시작 버튼을 클릭하여 상담을 시작하세요</p>
                </div>
              </div>
            </div>
          )}

          {/* 인입 키워드 + 상담 안내 멘트 - flex 레이아웃 */}
          {isCallActive && (
            <div 
              className="mb-4 flex gap-4 items-start"
              style={{
                animation: 'fadeInSmooth 0.6s ease-out both'
              }}
            >
              {/* 좌측: 인입 키워드 (고정 너비) */}
              <div className="flex-shrink-0" style={{ width: '240px' }}>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-xs font-bold text-[#333333]">인입 키워드</h3>
                  {isCallActive && displayedKeywords.length < 3 && (
                    <span className="text-[10px] text-[#666666] flex items-center gap-1">
                      <span className="inline-block w-1 h-1 bg-[#0047AB] rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                      <span className="inline-block w-1 h-1 bg-[#0047AB] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                      <span className="inline-block w-1 h-1 bg-[#0047AB] rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                      <span>키워드 추출 중</span>
                    </span>
                  )}
                </div>
                <div className="flex gap-1.5 flex-wrap">
                  {displayedKeywords.slice(0, 3).map((keyword, index) => (
                    <span 
                      key={`${keyword}-${currentStep}-${index}`}
                      className="px-1.5 py-0.5 bg-[#0047AB] text-white rounded-full text-[10px] font-medium"
                      style={{
                        animation: `fadeInScale 0.4s ease-out ${index * 0.15}s both`
                      }}
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              {/* 우측: 상담 안내 멘트 (남은 공간 모두 사용) */}
              {isKeywordDetected && showNextStepCards && (
                <div 
                  className="flex-1 bg-[#F0F7FF] border-l-4 border-[#0047AB] rounded-md p-2.5"
                  style={{
                    animation: 'fadeInUp 0.6s ease-out 0.3s both'
                  }}
                >
                  <div className="flex items-start gap-2">
                    <Lightbulb className="w-3.5 h-3.5 text-[#0047AB] flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h3 className="text-[10px] font-bold text-[#0047AB] mb-1">상담 안내 멘트</h3>
                      <p className="text-[10px] text-[#333333] leading-relaxed">
                        {(() => {
                          const baseMsg = activeScenario && currentStep > 0 
                            ? (activeScenario.steps[currentStep - 1]?.guidanceScript || guidanceScript)
                            : guidanceScript;
                          
                          // 고객 페르소나 특성 가져오기
                          const traits = activeScenario?.customer?.traits || [];
                          
                          // 동적 메시지 생성
                          return getPersonaMessage(baseMsg, traits);
                        })()}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 현재 상황 칸반보드 - 키워드 감지 후에만 표시 */}
          {isCallActive && (
            <div 
              className="mb-5"
              style={{
                animation: isKeywordDetected ? 'fadeInUp 0.7s ease-out 0.4s both' : 'none',
                opacity: isKeywordDetected ? 1 : 0
              }}
            >
              <h2 className="text-sm font-bold text-[#333333] mb-3 flex items-center gap-2">
                현재 상황 관련 정보
                {isAnalyzing && (
                  <span className="text-[10px] text-[#0047AB] font-normal flex items-center gap-1">
                    <div className="w-1.5 h-1.5 bg-[#0047AB] rounded-full animate-pulse"></div>
                    분석 중...
                  </span>
                )}
              </h2>
              {isAnalyzing ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 min-h-[400px]">
                {[1, 2].map((i) => (
                  <div 
                    key={i}
                    className="bg-gradient-to-br from-white to-[#F8FBFF] border-2 border-[#0047AB]/20 rounded-lg p-4 animate-pulse h-[180px]"
                  >
                    <div className="h-5 bg-[#E8F1FC] rounded w-3/4 mb-3"></div>
                    <div className="flex gap-1.5 mb-3">
                      <div className="h-5 bg-[#E8F1FC] rounded w-16"></div>
                      <div className="h-5 bg-[#E8F1FC] rounded w-20"></div>
                    </div>
                    <div className="space-y-2">
                      <div className="h-3 bg-[#F0F0F0] rounded w-full"></div>
                      <div className="h-3 bg-[#F0F0F0] rounded w-5/6"></div>
                      <div className="h-3 bg-[#F0F0F0] rounded w-4/6"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : !isKeywordDetected ? (
              <div className="flex items-center justify-center h-[400px] bg-[#F8FBFF] border-2 border-dashed border-[#0047AB]/30 rounded-lg">
                <div className="text-center">
                  <div className="w-12 h-12 bg-[#E8F1FC] rounded-full flex items-center justify-center mx-auto mb-3">
                    <Lightbulb className="w-6 h-6 text-[#0047AB]" />
                  </div>
                  <p className="text-sm text-[#666666] mb-1">STT 분석을 통해 키워드가 감지되면</p>
                  <p className="text-sm text-[#666666]">관련 정보가 자동으로 표시됩니다</p>
                </div>
              </div>
            ) : (
              // ⭐ 수평 슬라이딩 캐러셀: Step별로 좌→우 흐름
              <div className="relative">
                {/* Step 인디케이터 */}
                {activeScenario && (
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {activeScenario.steps.map((_, index) => (
                        <button
                          key={index}
                          onClick={() => handleProgressClick(index)}
                          disabled={index >= maxReachedStep}
                          className={`h-1 rounded-full transition-all duration-500 ${
                            index < maxReachedStep 
                              ? 'bg-[#0047AB] w-8 cursor-pointer hover:bg-[#003580]' 
                              : 'bg-[#E0E0E0] w-4 cursor-not-allowed'
                          }`}
                          title={index < maxReachedStep ? `Step ${index + 1}로 이동` : `Step ${index + 1} (키워드 감지 대기 중)`}
                        />
                      ))}
                      <span className="text-[10px] text-[#666666] ml-2">
                        Step {currentStep} / {maxReachedStep}
                      </span>
                    </div>
                    <div className="text-[10px] text-[#999999] flex items-center gap-1">
                      <span>← 드래그하여 Step 전환 →</span>
                    </div>
                  </div>
                )}
                
                {/* 슬라이딩 컨테이너 - 전체 Step을 포함, 드래그로 전환 가능 */}
                <div 
                  className="relative overflow-hidden cursor-grab active:cursor-grabbing"
                  onMouseDown={(e) => handleStepDragStart(e, 'current')}
                  onMouseMove={handleStepDragMove}
                  onMouseUp={handleStepDragEnd}
                  onMouseLeave={handleStepDragEnd}
                >
                  <div 
                    className="flex transition-transform duration-700 ease-in-out"
                    style={{
                      transform: `translateX(-${(currentStep - 1) * 100}%)`
                    }}
                  >
                    {activeScenario && activeScenario.steps.map((step, stepIndex) => {
                      const isCurrentStep = stepIndex === currentStep - 1;
                      const slideDirection = currentStep > previousStep ? 'left' : 'right';
                      
                      return (
                        <div 
                          key={stepIndex}
                          className="w-full flex-shrink-0 px-1"
                        >
                          {/* 카드 컨테이너 */}
                          <div className="flex gap-4 overflow-visible">
                            {step.currentSituationCards.map((card, cardIndex) => (
                              <div
                                key={card.id}
                                className="bg-gradient-to-br from-white to-[#F8FBFF] border-2 border-[#0047AB]/20 rounded-lg p-5 shadow-md hover:shadow-xl hover:border-[#0047AB]/40 transition-all flex flex-col flex-shrink-0"
                                style={{
                                  width: 'calc(50% - 8px)',
                                  minWidth: '320px',
                                  animation: isCurrentStep 
                                    ? `slideInFrom${slideDirection === 'left' ? 'Right' : 'Left'} 0.7s ease-out ${cardIndex * 0.1}s both` 
                                    : 'none'
                                }}
                              >
                              {/* Step 표시 배지 */}
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#0047AB] text-white">
                                  Step {stepIndex + 1}
                                </span>
                              </div>
                              <h3 className="text-base font-bold text-[#0047AB] mb-2.5">{card.title}</h3>
                              <div className="flex flex-wrap gap-1.5 mb-3">
                                {card.keywords.map((keyword: string, index: number) => (
                                  <span 
                                    key={index}
                                    className="text-[11px] px-2 py-0.5 bg-[#E8F1FC] text-[#0047AB] rounded font-medium"
                                  >
                                    {keyword}
                                  </span>
                                ))}
                              </div>
                              <p className="text-xs text-[#666666] leading-relaxed mb-3">{card.content}</p>
                                
                                {/* 실무 정보 */}
                                <div className="bg-white/60 rounded-md p-2.5 mb-2.5 space-y-2">
                                  <div className="text-[11px] text-[#0047AB] font-medium border-b border-[#0047AB]/10 pb-1.5">
                                    🖥️ {card.systemPath}
                                  </div>
                                  
                                  <div>
                                    <div className="text-[11px] font-semibold text-[#333333] mb-1">필수 확인 사항:</div>
                                    {card.requiredChecks.slice(0, 2).map((check: string, index: number) => (
                                      <div key={index} className="text-[10px] text-[#666666] leading-relaxed">
                                        {check}
                                      </div>
                                    ))}
                                  </div>
                                  
                                  <div>
                                    <div className="text-[11px] font-semibold text-[#333333] mb-1">예외 사항:</div>
                                    {card.exceptions.slice(0, 1).map((exception: string, index: number) => (
                                      <div key={index} className="text-[10px] text-[#EA4335] leading-relaxed">
                                        {exception}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                                
                                <div className="mt-auto space-y-1.5">
                                  <div className="flex items-center justify-between pt-2 border-t border-[#0047AB]/10">
                                    <div className="text-[11px] text-[#0047AB] font-medium">⏱️ {card.time}</div>
                                  </div>
                                  <div className="text-[11px] text-[#34A853] font-medium">✅ {card.note}</div>
                                  <button
                                    onClick={() => handleCardClick(card)}
                                    className="w-full mt-1.5 px-2.5 py-1.5 bg-[#0047AB] text-white rounded text-[11px] font-medium hover:bg-[#003580] transition-all flex items-center justify-center gap-1.5"
                                  >
                                    <FileText className="w-3.5 h-3.5" />
                                    자세히 보기 (약관 전문)
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 다음 단계 칸반보드 - 키워드 감지 후에만 표시 */}
          {isCallActive && isKeywordDetected && showNextStepCards && (
            <div 
              className="mb-5"
              style={{
                animation: 'fadeInUp 0.7s ease-out 1.1s both'
              }}
            >
              <h2 className="text-sm font-bold text-[#333333] mb-3 flex items-center justify-between">
                <span>다음 단계 예상 정보</span>
                <span className="text-[10px] text-[#999999] flex items-center gap-1">
                  ← 드래그하여 Step 전환 →
                </span>
              </h2>
              
              {/* 슬라이딩 컨테이너 - 전체 Step을 포함, 드래그로 전환 가능 */}
              <div 
                className="relative overflow-hidden cursor-grab active:cursor-grabbing"
                onMouseDown={(e) => handleStepDragStart(e, 'next')}
                onMouseMove={handleStepDragMove}
                onMouseUp={handleStepDragEnd}
                onMouseLeave={handleStepDragEnd}
              >
                <div 
                  className="flex transition-transform duration-700 ease-in-out"
                  style={{
                    transform: `translateX(-${(currentStep - 1) * 100}%)`
                  }}
                >
                  {activeScenario && activeScenario.steps.map((step, stepIndex) => {
                    const isCurrentStep = stepIndex === currentStep - 1;
                    const slideDirection = currentStep > previousStep ? 'left' : 'right';
                    
                    return (
                      <div 
                        key={stepIndex}
                        className="w-full flex-shrink-0 px-1"
                      >
                        {/* 카드 컨테이너 */}
                        <div className="flex gap-4 overflow-visible">
                          {step.nextStepCards.map((card, cardIndex) => (
                            <div
                              key={card.id}
                              className="bg-gradient-to-br from-white to-[#F8FBFF] border-2 border-[#0047AB]/20 rounded-lg p-5 shadow-md hover:shadow-xl hover:border-[#0047AB]/40 transition-all flex flex-col flex-shrink-0"
                              style={{
                                width: 'calc(50% - 8px)',
                                minWidth: '320px',
                                animation: isCurrentStep 
                                  ? `slideInFrom${slideDirection === 'left' ? 'Right' : 'Left'} 0.7s ease-out ${cardIndex * 0.1}s both` 
                                  : 'none'
                              }}
                            >
                            {/* Step 표시 배지 */}
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#FBBC04] text-[#333333]">
                                Step {stepIndex + 1} 예상
                              </span>
                            </div>
                            <h3 className="text-base font-bold text-[#0047AB] mb-2.5">{card.title}</h3>
                            <div className="flex flex-wrap gap-1.5 mb-3">
                              {card.keywords.map((keyword: string, index: number) => (
                                <span 
                                  key={index}
                                  className="text-[11px] px-2 py-0.5 bg-[#FFF4E0] text-[#FBBC04] border border-[#FBBC04]/30 rounded font-medium"
                                >
                                  {keyword}
                                </span>
                              ))}
                            </div>
                            <p className="text-xs text-[#666666] leading-relaxed mb-3">{card.content}</p>
                            
                            {/* 실무 정보 */}
                            <div className="bg-white/60 rounded-md p-2.5 mb-2.5 space-y-2">
                              <div className="text-[11px] text-[#0047AB] font-medium border-b border-[#0047AB]/10 pb-1.5">
                                🖥️ {card.systemPath}
                              </div>
                              <div>
                                <div className="text-[11px] font-semibold text-[#333333] mb-1">필수 확인 사항:</div>
                                {card.requiredChecks.slice(0, 2).map((check: string, index: number) => (
                                  <div key={index} className="text-[10px] text-[#666666] leading-relaxed">
                                    {check}
                                  </div>
                                ))}
                              </div>
                              <div>
                                <div className="text-[11px] font-semibold text-[#333333] mb-1">예외 사항:</div>
                                {card.exceptions.slice(0, 1).map((exception: string, index: number) => (
                                  <div key={index} className="text-[10px] text-[#EA4335] leading-relaxed">
                                    {exception}
                                  </div>
                                ))}
                              </div>
                            </div>
                            
                            <div className="mt-auto space-y-1.5">
                              <div className="flex items-center justify-between pt-2 border-t border-[#0047AB]/10">
                                <div className="text-[11px] text-[#0047AB] font-medium">⏱️ {card.time}</div>
                              </div>
                              <div className="text-[11px] text-[#34A853] font-medium">✅ {card.note}</div>
                              <button
                                onClick={() => handleCardClick(card)}
                                className="w-full mt-1.5 px-2.5 py-1.5 bg-[#0047AB] text-white rounded text-[11px] font-medium hover:bg-[#003580] transition-all flex items-center justify-center gap-1.5"
                              >
                                <FileText className="w-3.5 h-3.5" />
                                자세히 보기 (약관 전문)
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 우측 열 - 고정 너비 25% (데스크톱: 고정, 모바일: 탭 전환) */}
        <div className={`
          bg-[#FAFAFA] p-4 flex flex-col
          ${mobileTab === 'control' ? 'flex' : 'hidden lg:flex'}
          lg:w-[25%]
          w-full ${isCallActive ? 'mt-[89px]' : 'mt-[49px]'} lg:mt-0
          h-full overflow-hidden
        `}>
          {/* 통화 컨트롤 - PC에서만 표시 (모바일은 상단 통화 상태바 사용) */}
          <div className="hidden lg:block bg-gradient-to-r from-white to-[#F8FBFF] rounded-lg border border-[#E0E0E0] p-2 mb-2 flex-shrink-0 shadow-sm">
            <div className="flex items-center justify-between">
              {/* 통화 시간 */}
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 bg-[#34A853] rounded-full animate-pulse"></div>
                <span className="text-xs font-bold text-[#333333] tabular-nums">{formatTime(callTime)}</span>
              </div>
              
              {/* 통화 버튼들 */}
              <div className="flex gap-1.5">
                {!isCallActive ? (
                  <button 
                    onClick={handleStartCall}
                    className="w-7 h-7 bg-[#34A853] rounded-lg flex items-center justify-center hover:bg-[#2E7D32] transition-all shadow-sm hover:shadow-md"
                    title="통화 시작"
                  >
                    <Phone className="w-3.5 h-3.5 text-white" />
                  </button>
                ) : (
                  <>
                    <button 
                      className="w-7 h-7 bg-[#34A853] rounded-lg flex items-center justify-center cursor-default"
                      title="통화 중"
                    >
                      <Phone className="w-3.5 h-3.5 text-white animate-pulse" />
                    </button>
                    <button 
                      onClick={handleEndCallClick}
                      className="w-7 h-7 bg-[#EA4335] rounded-lg flex items-center justify-center hover:bg-[#C62828] transition-all shadow-sm hover:shadow-md"
                      title="통화 종료"
                    >
                      <PhoneOff className="w-3.5 h-3.5 text-white" />
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* ⭐ STT 실시간 스트림 - 스크롤 가능 영역 */}
          <div className="flex flex-col bg-white rounded-lg border border-[#E0E0E0] mb-3 shadow-sm overflow-hidden h-[100px] flex-shrink-0">
            <h3 className="text-xs font-bold text-[#333333] p-2.5 pb-2 flex items-center gap-1.5 flex-shrink-0">
              <div className={`w-2 h-2 rounded-full ${isCallActive ? 'bg-[#EA4335] animate-pulse' : 'bg-[#999999]'}`}></div>
              실시간 STT 분석
              {isCallActive && (
                <span className="text-[9px] text-[#0047AB] font-normal flex items-center gap-1 ml-auto">
                  <div className="w-1 h-1 bg-[#0047AB] rounded-full animate-pulse"></div>
                  분석 중
                </span>
              )}
            </h3>
            <div className="flex-1 bg-[#F8F9FA] rounded-md mx-2.5 mb-2.5 p-2 overflow-y-auto flex items-start min-h-0">
              {!isCallActive ? (
                // 통화 대기 중 상태
                <div className="w-full h-full flex items-center justify-center">
                  <div className="flex flex-col items-center gap-2">
                    <Bot className="w-4 h-4 text-[#999999]" />
                    <p className="text-[10px] text-[#999999]">통화를 시작하면 음성이 실시간으로 분석됩니다</p>
                  </div>
                </div>
              ) : sttTexts.length === 0 ? (
                // 통화 중이지만 아직 음성 없음
                <div className="w-full h-full flex items-center justify-center">
                  <div className="flex flex-col items-center gap-2">
                    <div className="flex gap-1">
                      <div className="w-1.5 h-1.5 bg-[#0047AB] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-1.5 h-1.5 bg-[#0047AB] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-1.5 h-1.5 bg-[#0047AB] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <p className="text-[10px] text-[#999999]">음성 인식 대기 중...</p>
                  </div>
                </div>
              ) : (
                // STT 텍스트 표시
                <div className="leading-relaxed w-full space-y-2">
                  {sttTexts.map((item, index) => {
                    const category = getKeywordCategory(item.text);
                    const colorClass = category ? categoryColors[category] : '';
                    
                    return (
                      <span 
                        key={index}
                        className={`text-[10px] inline transition-all duration-300 ${
                          item.isKeyword 
                            ? `font-bold px-1.5 py-0.5 rounded-md ${colorClass || 'bg-[#E8F1FC] text-[#0047AB]'}` 
                            : 'text-[#666666]'
                        }`}
                        style={{ 
                          opacity: index >= sttTexts.length - 15 ? 1 : 0.5,
                          animation: index === sttTexts.length - 1 ? 'fadeIn 0.4s ease-out' : 'none'
                        }}
                      >
                        {item.text}
                      </span>
                    );
                  })}
                  <div ref={sttEndRef} />
                </div>
              )}
            </div>
          </div>

          {/* 메모장 */}
          <div className="flex-shrink-0 mb-3">
            <h3 className="text-xs font-bold text-[#333333] mb-2">상담 메모</h3>
            <textarea
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              className="w-full bg-white border border-[#E0E0E0] rounded-md p-2.5 text-xs text-[#333333] resize-none focus:outline-none focus:border-[#0047AB] focus:ring-1 focus:ring-[#0047AB] h-[80px] overflow-y-auto"
              placeholder="상담 중 메모를 입력하세요..."
            />
            <Button 
              onClick={handleSaveMemo}
              disabled={saveStatus === 'saving' || saveStatus === 'saved'}
              className={`w-full mt-1.5 h-6 text-[9px] flex items-center justify-center gap-1 transition-colors ${
                saveStatus === 'saved' 
                  ? 'bg-[#34A853] hover:bg-[#34A853]' 
                  : 'bg-[#0047AB] hover:bg-[#003580]'
              }`}
            >
              <Save className="w-2.5 h-2.5" />
              {saveStatus === 'idle' && '저장'}
              {saveStatus === 'saving' && '저장 중...'}
              {saveStatus === 'saved' && '✓ 저장 완료'}
            </Button>
          </div>

          {/* AI 검색 어시스턴트 - 채팅 형식 */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <h3 className="text-xs font-bold text-[#333333] mb-1 flex-shrink-0">AI 검색 어시스턴트</h3>
            <p className="text-[10px] text-[#999999] mb-2 flex-shrink-0">궁금한 내용을 질문하세요</p>
            
            {/* 채팅 메시지 영역 */}
            <div className="flex-1 min-h-0 bg-white border border-[#E0E0E0] rounded-md p-2 overflow-y-auto mb-1.5">
              {chatMessages.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Bot className="w-8 h-8 text-[#999999] mx-auto mb-3" />
                    <p className="text-xs text-[#999999]">질문을 입력해보세요</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  {chatMessages.map((msg) => (
                    <div 
                      key={msg.id}
                      className={`flex gap-1.5 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {msg.type === 'ai' && (
                        <div className="flex-shrink-0 w-5 h-5 bg-[#0047AB] rounded-full flex items-center justify-center">
                          <Bot className="w-3 h-3 text-white" />
                        </div>
                      )}
                      <div className={`max-w-[80%] ${msg.type === 'user' ? 'bg-[#0047AB] text-white' : 'bg-[#F5F5F5] text-[#333333]'} rounded-lg p-2`}>
                        <p className="text-[10px] leading-relaxed">{msg.text}</p>
                        <span className="text-[8px] opacity-70 mt-0.5 block">{msg.timestamp}</span>
                      </div>
                      {msg.type === 'user' && (
                        <div className="flex-shrink-0 w-5 h-5 bg-[#4A90E2] rounded-full flex items-center justify-center">
                          <User className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
              )}
            </div>

            {/* 검색 입력 영역 */}
            <div className="flex-shrink-0 flex gap-1.5">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 h-7 bg-white border border-[#E0E0E0] rounded-md px-2 text-[9px] focus:outline-none focus:border-[#0047AB] focus:ring-1 focus:ring-[#0047AB]"
                placeholder="질문을 입력하세요..."
              />
              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim()}
                className="w-7 h-7 bg-[#0047AB] text-white rounded-md flex items-center justify-center hover:bg-[#003580] transition-colors disabled:bg-[#CCCCCC] disabled:cursor-not-allowed"
              >
                <Send className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 약관 전문 모달 */}
      {selectedDetailCard && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[70] p-4" onClick={() => setSelectedDetailCard(null)}>
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
            {/* 모달 헤더 */}
            <div className="bg-gradient-to-r from-[#0047AB] to-[#003580] text-white p-4 rounded-t-lg flex items-center justify-between">
              <div className="flex-1">
                <h2 className="text-base font-bold mb-1">{selectedDetailCard.title}</h2>
                <p className="text-xs opacity-90">{selectedDetailCard.regulation}</p>
              </div>
              <button
                onClick={() => setSelectedDetailCard(null)}
                className="w-8 h-8 flex items-center justify-center hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 모달 바디 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* 요약 정보 */}
              <div className="bg-[#F8FBFF] border-l-4 border-[#0047AB] rounded-md p-4 space-y-3">
                <div>
                  <h3 className="text-sm font-bold text-[#0047AB] mb-2">📋 요약</h3>
                  <p className="text-xs text-[#333333] leading-relaxed">{selectedDetailCard.content}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-2 border-t border-[#0047AB]/20">
                  <div>
                    <p className="text-[10px] text-[#0047AB] font-medium">⏱️ {selectedDetailCard.time}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-[#34A853] font-medium">✅ {selectedDetailCard.note}</p>
                  </div>
                </div>
              </div>

              {/* 시스템 경로 */}
              <div>
                <h3 className="text-sm font-bold text-[#333333] mb-2">🖥️ 시스템 처리 경로</h3>
                <div className="bg-[#F5F5F5] rounded-md p-3">
                  <p className="text-xs text-[#0047AB] font-medium">{selectedDetailCard.systemPath}</p>
                </div>
              </div>

              {/* 필수 확인 사항 */}
              <div>
                <h3 className="text-sm font-bold text-[#333333] mb-2">✅ 필수 확인 사항</h3>
                <div className="space-y-2">
                  {selectedDetailCard.requiredChecks.map((check, index) => (
                    <div key={index} className="flex items-start gap-2 bg-white border border-[#E0E0E0] rounded-md p-2.5">
                      <div className="w-5 h-5 bg-[#34A853] text-white rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-bold">
                        {index + 1}
                      </div>
                      <p className="text-xs text-[#333333] flex-1">{check}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 예외 사항 */}
              <div>
                <h3 className="text-sm font-bold text-[#333333] mb-2">⚠️ 예외 사항</h3>
                <div className="space-y-2">
                  {selectedDetailCard.exceptions.map((exception, index) => (
                    <div key={index} className="flex items-start gap-2 bg-[#FFF3E0] border border-[#EA4335]/20 rounded-md p-2.5">
                      <div className="w-5 h-5 bg-[#EA4335] text-white rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-bold">
                        !
                      </div>
                      <p className="text-xs text-[#333333] flex-1">{exception}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 약관 전문 */}
              <div>
                <h3 className="text-sm font-bold text-[#333333] mb-2">📜 약관 전문</h3>
                <div className="bg-white border-2 border-[#0047AB]/30 rounded-md p-4">
                  <pre className="text-xs text-[#333333] leading-relaxed whitespace-pre-wrap font-sans">
                    {selectedDetailCard.fullText}
                  </pre>
                </div>
              </div>
            </div>

            {/* 모달 푸터 */}
            <div className="border-t border-[#E0E0E0] p-4 flex justify-end">
              <Button 
                onClick={() => setSelectedDetailCard(null)}
                className="bg-[#0047AB] text-white hover:bg-[#003580] h-9 text-xs px-6"
              >
                닫기
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* 통화 종료 확인 모달 */}
      {isEndCallModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[80] p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
            {/* 모달 헤더 */}
            <div className="bg-gradient-to-r from-[#0047AB] to-[#003580] text-white p-4 rounded-t-lg flex items-center justify-between">
              <div className="flex-1">
                <h2 className="text-base font-bold mb-1">통화 종료 확인</h2>
                <p className="text-xs opacity-90">현재 상담을 종료하시겠습니까?</p>
              </div>
              <button
                onClick={handleCancelEndCall}
                className="w-8 h-8 flex items-center justify-center hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 모달 바디 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* 메모 내용 */}
              <div className="bg-[#F8FBFF] border-l-4 border-[#0047AB] rounded-md p-4 space-y-3">
                <div>
                  <h3 className="text-sm font-bold text-[#0047AB] mb-2">📋 메모 내용</h3>
                  <p className="text-xs text-[#333333] leading-relaxed">{memo}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-2 border-t border-[#0047AB]/20">
                  <div>
                    <p className="text-[10px] text-[#0047AB] font-medium">⏱️ {formatTime(callTime)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 모달 푸터 */}
            <div className="border-t border-[#E0E0E0] p-4 flex justify-end gap-2">
              <Button 
                onClick={handleCancelEndCall}
                className="bg-white text-[#0047AB] border border-[#0047AB] hover:bg-[#F8FBFF] h-9 text-xs"
              >
                취소
              </Button>
              <Button 
                onClick={handleConfirmEndCall}
                className="bg-[#0047AB] text-white hover:bg-[#003580] h-9 text-xs"
              >
                확인
              </Button>
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}