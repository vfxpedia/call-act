import MainLayout from '../components/layout/MainLayout';
import { Phone, PhoneOff, Save, Send, Lightbulb, Copy, Bot, User, ChevronLeft, ChevronRight, X, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSidebar } from '../contexts/SidebarContext';

// Mock Data
const customerInfo = {
  id: 'CUST-001',
  name: '홍길동',
  phone: '010-1234-5678',
  birthDate: '1985-03-15',
  address: '서울시 강남구 테헤란로 123'
};

const recentConsultations = [
  { id: 1, title: '카드 재발급 문의', date: '2025-01-03 10:30', category: '카드분실', status: '완료' },
  { id: 2, title: '해외 결제 문의', date: '2024-12-28 14:20', category: '해외결제', status: '진행중' },
  { id: 3, title: '수수료 환불 요청', date: '2024-12-20 09:15', category: '수수료문의', status: '완료' },
];

const sttKeywords = ['카드분실', '해외결제', '수수료문의'];

const currentSituationCards: DetailCard[] = [
  {
    id: 1,
    title: '카드 분실 신고 처리 절차',
    keywords: ['#분실신고', '#즉시정지', '#재발급'],
    content: '고객의 카드 분실 신고를 접수하고 즉시 카드 사용을 정지합니다.',
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
    detailContent: `제34조 (카드의 분실신고 및 재발급)

① 회원은 카드를 분실한 경우 즉시 회사에 신고하여야 하며, 회사는 신고 접수 즉시 해당 카드의 이용을 정지하여야 한다.

② 회사는 회원의 분실신고 접수 시점 이후 발생한 제3자의 부정사용으로 인한 손해에 대하여 책임을 지며, 신고 접수 이전 72시간 이내 발생한 손해에 대해서는 보험 처리를 통해 보상한다.

③ 재발급 신청 시 회원은 본인확인 절차를 거쳐야 하며, 재발급 수수료는 면제한다. 단, 긴급 재발급의 경우 별도 수수료가 부과될 수 있다.

④ 재발급 카드는 신청일로부터 3-5 영업일 내 등록된 주소로 등기우편으로 발송되며, 회원은 SMS를 통해 배송 추적 번호를 제공받는다.

⑤ 법인카드의 경우 법인 담당자의 서면 승인이 필요하며, 가족카드는 주카드 회원의 동의가 필요하다.`,
    time: '처리 시간: 약 3-5분',
    note: '분실 신고 후 72시간 내 부정 사용 보상 가능'
  },
  {
    id: 2,
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
    detailContent: `제8조 (카드의 이용정지)

① 회원이 카드의 이용정지를 요청하는 경우 회사는 즉시 카드 이용을 정지하며, 정지 시점은 시스템에 자동 기록된다.

② 카드 이용정지 시 회사는 회원에게 SMS, 이메일, 앱 푸시 알림을 통해 정지 사실을 통지한다.

③ 정지된 카드로는 신규 거래가 불가능하나, 정지 이전 승인된 거래 중 아직 매입되지 않은 거래는 정상 처리될 수 있다.

④ 정기결제 및 자동이체는 정지 시점으로부터 72시간의 유예기간이 부여되며, 이 기간 내 회원은 대체 결제수단을 등록해야 한다.

⑤ 해외 가맹점의 경우 네트워크 지연으로 인해 정지 처리가 최대 24시간 소요될 수 있으며, 이 기간 내 발생한 거래에 대해서는 회사가 책임을 진다.

⑥ 교통카드 기능이 포함된 카드의 경우 별도의 교통카드 정지 절차를 진행해야 한다.`,
    time: '처리 시간: 즉시',
    note: '정지 후에도 정기 결제는 72시간 유예'
  }
];

const nextStepCards: DetailCard[] = [
  {
    id: 1,
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
    detailContent: `제35조 (카드의 배송 및 수령)

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
    id: 2,
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
    detailContent: `제23조 (분실·도난 카드의 부정사용)

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

interface ChatMessage {
  id: number;
  type: 'user' | 'ai';
  text: string;
  timestamp: string;
}

interface DetailCard {
  id: number;
  title: string;
  keywords: string[];
  content: string;
  systemPath: string;
  requiredChecks: string[];
  exceptions: string[];
  regulation: string;
  detailContent: string;
  time: string;
  note: string;
}

export default function RealTimeConsultationPage() {
  const navigate = useNavigate();
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  // Sidebar Context 사용
  const { isSidebarExpanded } = useSidebar();
  
  // Local state
  const [isCallActive, setIsCallActive] = useState(false);
  const [callTime, setCallTime] = useState(332); // 5:32 in seconds
  const [memo, setMemo] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isLeftSidebarCollapsed, setIsLeftSidebarCollapsed] = useState(false);
  const [selectedDetailCard, setSelectedDetailCard] = useState<DetailCard | null>(null);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleCopyScript = () => {
    navigator.clipboard.writeText(guidanceScript);
  };

  const handleEndCall = () => {
    navigate('/acw');
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

    // AI 답변 시뮬레이션
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
      return '연회비는 카드 발급 후 1년 후 청구됩니다. 전년도 실적 조건을 충족하면 면제됩니다. 실적 기준은 월 30만원 이상 사용입니다.';
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

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  return (
    <MainLayout>
      <div className="h-[calc(100vh-60px)] flex bg-[#F5F5F5] relative">
        {/* 폴딩 버튼 - 미니멀 디자인 */}
        <button
          onClick={() => setIsLeftSidebarCollapsed(!isLeftSidebarCollapsed)}
          className="fixed top-1/2 -translate-y-1/2 z-[60] w-6 h-6 bg-white border border-[#D1D5DB] text-[#666666] rounded-full flex items-center justify-center hover:border-[#0047AB] hover:text-[#0047AB] hover:shadow-md transition-all duration-300 shadow-sm"
          style={{ 
            marginTop: '30px',
            left: `${
              isLeftSidebarCollapsed 
                ? (isSidebarExpanded ? 188 : 44)  // 고객정보 접혔을 때: 네비게이션 너비 - 12px
                : (isSidebarExpanded ? 388 : 244)  // 고객정보 펼쳐졌을 때: 네비게이션 + 200px - 12px
            }px`
          }}
        >
          <ChevronLeft 
            className={`w-3.5 h-3.5 transition-transform duration-300 ${
              isLeftSidebarCollapsed ? 'rotate-180' : ''
            }`}
          />
        </button>

        {/* 좌측 열 - 폴딩 가능 */}
        <div 
          className={`bg-[#FAFAFA] border-r border-[#E0E0E0] flex flex-col overflow-y-auto overflow-x-hidden transition-all duration-300 relative ${
            isLeftSidebarCollapsed ? 'w-0' : 'w-[200px]'
          }`}
        >
          <div className={`w-[200px] p-3 flex flex-col overflow-y-auto ${isLeftSidebarCollapsed ? 'opacity-0' : 'opacity-100'}`}>
            {/* 고객 정보 카드 */}
            <div className="bg-white rounded-lg border border-[#E0E0E0] p-2.5 mb-3 flex-shrink-0">
              <h3 className="text-xs font-bold text-[#333333] mb-2">고객 정보</h3>
              <div className="space-y-1 text-[11px] text-[#666666]">
                <div><span className="font-medium text-[#333333]">ID:</span> {customerInfo.id}</div>
                <div><span className="font-medium text-[#333333]">이름:</span> {customerInfo.name}</div>
                <div><span className="font-medium text-[#333333]">전화:</span> {customerInfo.phone}</div>
                <div><span className="font-medium text-[#333333]">생년월일:</span> {customerInfo.birthDate}</div>
                <div><span className="font-medium text-[#333333]">주소:</span> {customerInfo.address}</div>
              </div>
            </div>

            {/* 최근 상담 내역 */}
            <div className="flex-1 overflow-y-auto">
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
          </div>
        </div>

        {/* 중앙 열 - 동적 너비 */}
        <div className={`bg-white p-4 overflow-y-auto transition-all duration-300 ${
          isLeftSidebarCollapsed ? 'w-[calc(75%-0px)]' : 'w-[calc(75%-200px)]'
        }`}>
          {/* STT 키워드 배지 */}
          <div className="mb-3">
            <h3 className="text-xs font-bold text-[#333333] mb-2">인입 키워드</h3>
            <div className="flex gap-1.5">
              {sttKeywords.map((keyword, index) => (
                <span 
                  key={index}
                  className="px-1.5 py-0.5 bg-[#0047AB] text-white rounded-full text-[10px] font-medium"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          {/* 현재 상황 칸반보드 */}
          <div className="mb-4">
            <h2 className="text-xs font-bold text-[#333333] mb-2">현재 상황 관련 정보</h2>
            <div className="grid grid-cols-2 gap-3">
              {currentSituationCards.map((card) => (
                <div 
                  key={card.id}
                  className="bg-gradient-to-br from-white to-[#F8FBFF] border-2 border-[#0047AB]/20 rounded-lg p-4 shadow-md hover:shadow-xl hover:border-[#0047AB]/40 transition-all flex flex-col"
                >
                  <h3 className="text-base font-bold text-[#0047AB] mb-2.5">{card.title}</h3>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {card.keywords.map((keyword, index) => (
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
                    {/* 시스템 경로 */}
                    <div className="text-[11px] text-[#0047AB] font-medium border-b border-[#0047AB]/10 pb-1.5">
                      🖥️ {card.systemPath}
                    </div>
                    
                    {/* 필수 확인 사항 */}
                    <div>
                      <div className="text-[11px] font-semibold text-[#333333] mb-1">필수 확인 사항:</div>
                      {card.requiredChecks.slice(0, 2).map((check, index) => (
                        <div key={index} className="text-[10px] text-[#666666] leading-relaxed">
                          {check}
                        </div>
                      ))}
                    </div>
                    
                    {/* 예외 사항 */}
                    <div>
                      <div className="text-[11px] font-semibold text-[#333333] mb-1">예외 사항:</div>
                      {card.exceptions.slice(0, 1).map((exception, index) => (
                        <div key={index} className="text-[10px] text-[#EA4335] leading-relaxed">
                          {exception}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* 하단 정보 */}
                  <div className="mt-auto space-y-1.5">
                    <div className="flex items-center justify-between pt-2 border-t border-[#0047AB]/10">
                      <div className="text-[11px] text-[#0047AB] font-medium">⏱️ {card.time}</div>
                    </div>
                    <div className="text-[11px] text-[#34A853] font-medium">✅ {card.note}</div>
                    <button
                      onClick={() => setSelectedDetailCard(card)}
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

          {/* 다음 단계 칸반보드 */}
          <div className="mb-4">
            <h2 className="text-xs font-bold text-[#333333] mb-2">다음 단계 예상 정보</h2>
            <div className="grid grid-cols-2 gap-3">
              {nextStepCards.map((card) => (
                <div 
                  key={card.id}
                  className="bg-gradient-to-br from-white to-[#F8FBFF] border-2 border-[#0047AB]/20 rounded-lg p-4 shadow-md hover:shadow-xl hover:border-[#0047AB]/40 transition-all flex flex-col"
                >
                  <h3 className="text-base font-bold text-[#0047AB] mb-2.5">{card.title}</h3>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {card.keywords.map((keyword, index) => (
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
                    {/* 시스템 경로 */}
                    <div className="text-[11px] text-[#0047AB] font-medium border-b border-[#0047AB]/10 pb-1.5">
                      🖥️ {card.systemPath}
                    </div>
                    
                    {/* 필수 확인 사항 */}
                    <div>
                      <div className="text-[11px] font-semibold text-[#333333] mb-1">필수 확인 사항:</div>
                      {card.requiredChecks.slice(0, 2).map((check, index) => (
                        <div key={index} className="text-[10px] text-[#666666] leading-relaxed">
                          {check}
                        </div>
                      ))}
                    </div>
                    
                    {/* 예외 사항 */}
                    <div>
                      <div className="text-[11px] font-semibold text-[#333333] mb-1">예외 사항:</div>
                      {card.exceptions.slice(0, 1).map((exception, index) => (
                        <div key={index} className="text-[10px] text-[#EA4335] leading-relaxed">
                          {exception}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* 하단 정보 */}
                  <div className="mt-auto space-y-1.5">
                    <div className="flex items-center justify-between pt-2 border-t border-[#0047AB]/10">
                      <div className="text-[11px] text-[#0047AB] font-medium">⏱️ {card.time}</div>
                    </div>
                    <div className="text-[11px] text-[#34A853] font-medium">✅ {card.note}</div>
                    <button
                      onClick={() => setSelectedDetailCard(card)}
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

          {/* 상담 가이드 */}
          <div className="bg-[#F0F7FF] border-l-4 border-[#0047AB] rounded-md p-2.5">
            <div className="flex items-start gap-2">
              <Lightbulb className="w-3.5 h-3.5 text-[#0047AB] flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-[10px] font-bold text-[#0047AB] mb-1">상담 안내 멘트</h3>
                <p className="text-[10px] text-[#333333] leading-relaxed">{guidanceScript}</p>
              </div>
              <button 
                onClick={handleCopyScript}
                className="flex-shrink-0 w-5 h-5 flex items-center justify-center hover:bg-[#0047AB]/10 rounded transition-colors"
              >
                <Copy className="w-3 h-3 text-[#0047AB]" />
              </button>
            </div>
          </div>
        </div>

        {/* 우측 열 - 고정 너비 25% */}
        <div className="w-[25%] bg-[#FAFAFA] p-3 flex flex-col overflow-hidden">
          {/* 통화 컨트롤 - 세련된 디자인 */}
          <div className="bg-gradient-to-r from-white to-[#F8FBFF] rounded-lg border border-[#E0E0E0] p-3 mb-3 flex-shrink-0 shadow-sm">
            <div className="flex items-center justify-between">
              {/* 통화 시간 */}
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-[#34A853] rounded-full animate-pulse"></div>
                <span className="text-sm font-bold text-[#333333] tabular-nums">{formatTime(callTime)}</span>
              </div>
              
              {/* 통화 버튼들 */}
              <div className="flex gap-2">
                <button 
                  className="w-8 h-8 bg-[#34A853] rounded-lg flex items-center justify-center hover:bg-[#2E7D32] transition-all shadow-sm hover:shadow-md"
                  title="통화 중"
                >
                  <Phone className="w-4 h-4 text-white" />
                </button>
                <button 
                  onClick={handleEndCall}
                  className="w-8 h-8 bg-[#EA4335] rounded-lg flex items-center justify-center hover:bg-[#C62828] transition-all shadow-sm hover:shadow-md"
                  title="통화 종료"
                >
                  <PhoneOff className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
          </div>

          {/* 메모장 */}
          <div className="flex-shrink-0 mb-3">
            <h3 className="text-xs font-bold text-[#333333] mb-2">상담 메모</h3>
            <textarea
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              className="w-full bg-white border border-[#E0E0E0] rounded-md p-2 text-[10px] text-[#333333] resize-none focus:outline-none focus:border-[#0047AB] focus:ring-1 focus:ring-[#0047AB]"
              placeholder="상담 중 메모를 입력하세요..."
              rows={8}
            />
            <Button className="w-full mt-2 bg-[#0047AB] hover:bg-[#003580] h-7 text-[10px]">
              <Save className="w-3 h-3 mr-1" />
              저장
            </Button>
          </div>

          {/* AI 검색 어시스턴트 - 채팅 형식 */}
          <div className="flex-1 flex flex-col overflow-hidden min-h-0">
            <h3 className="text-xs font-bold text-[#333333] mb-1 flex-shrink-0">AI 검색 어시스턴트</h3>
            <p className="text-[9px] text-[#999999] mb-2 flex-shrink-0">궁금한 내용을 질문하세요</p>
            
            {/* 채팅 메시지 영역 */}
            <div className="flex-1 bg-white border border-[#E0E0E0] rounded-md p-2 overflow-y-auto mb-2 min-h-0">
              {chatMessages.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Bot className="w-7 h-7 text-[#999999] mx-auto mb-2" />
                    <p className="text-[10px] text-[#999999]">질문을 입력해보세요</p>
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
            <div className="flex-shrink-0 flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 h-8 bg-white border border-[#E0E0E0] rounded-md px-2 text-[10px] focus:outline-none focus:border-[#0047AB] focus:ring-1 focus:ring-[#0047AB]"
                placeholder="질문을 입력하세요..."
              />
              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim()}
                className="w-8 h-8 bg-[#0047AB] text-white rounded-md flex items-center justify-center hover:bg-[#003580] transition-colors disabled:bg-[#CCCCCC] disabled:cursor-not-allowed"
              >
                <Send className="w-3.5 h-3.5" />
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
                    {selectedDetailCard.detailContent}
                  </pre>
                </div>
              </div>
            </div>

            {/* 모달 푸터 */}
            <div className="border-t border-[#E0E0E0] p-4 flex justify-end gap-2">
              <Button 
                onClick={() => {
                  navigator.clipboard.writeText(selectedDetailCard.detailContent);
                }}
                className="bg-white text-[#0047AB] border border-[#0047AB] hover:bg-[#F8FBFF] h-9 text-xs"
              >
                <Copy className="w-3.5 h-3.5 mr-1.5" />
                전문 복사
              </Button>
              <Button 
                onClick={() => setSelectedDetailCard(null)}
                className="bg-[#0047AB] text-white hover:bg-[#003580] h-9 text-xs"
              >
                닫기
              </Button>
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}