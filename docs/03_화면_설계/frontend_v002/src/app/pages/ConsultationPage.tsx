import MainLayout from '../components/layout/MainLayout';
import { Phone, PhoneOff, Save, Search, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { useNavigate } from 'react-router-dom';

export default function ConsultationPage() {
  const navigate = useNavigate();

  return (
    <MainLayout>
      <div className="h-[calc(100vh-60px)] overflow-hidden p-2 sm:p-0">
        {/* 모바일: 세로 스크롤, 데스크톱: 3컬럼 그리드 */}
        <div className="hidden lg:grid lg:grid-cols-12 lg:gap-4 h-full">
          {/* Column 1 - Left (~10%) - Customer Info */}
          <div className="col-span-1 space-y-4 overflow-y-auto">
            {/* Call Controls */}
            <div className="bg-white rounded-lg shadow-sm p-4 text-center">
              <div className="text-3xl font-bold text-[#333333] mb-4">05:32</div>
              <Button className="w-full bg-[#34A853] hover:bg-[#2D8F47] mb-2 h-14">
                <Phone className="w-6 h-6" />
              </Button>
              <Button 
                className="w-full bg-[#EA4335] hover:bg-[#C8362D] mb-2 h-14"
                onClick={() => navigate('/acw')}
              >
                <PhoneOff className="w-6 h-6" />
              </Button>
              <Button 
                className="w-full bg-[#0047AB] hover:bg-[#003580] h-10 text-xs"
                onClick={() => navigate('/acw')}
              >
                후처리 <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </div>

            {/* Customer Info */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-semibold text-[#333333] mb-3">고객 정보</h3>
              <div className="space-y-2 text-xs text-[#666666]">
                <div><span className="font-medium">ID:</span> CUST-001</div>
                <div><span className="font-medium">이름:</span> 홍길동</div>
                <div><span className="font-medium">전화:</span> 010-1234-5678</div>
                <div><span className="font-medium">생년월일:</span> 1985-03-15</div>
              </div>
            </div>

            {/* Recent History */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-semibold text-[#333333] mb-3">최근 상담</h3>
              <div className="space-y-2">
                <div className="text-xs p-2 bg-[#F5F5F5] rounded border-l-2 border-[#34A853]">
                  <div className="font-medium text-[#333333] line-clamp-1">카드 재발급 문의</div>
                  <div className="text-[#999999] mt-1">2025-01-03 10:30</div>
                </div>
              </div>
            </div>
          </div>

          {/* Column 2 - Center (~65%) - AI Kanban Board */}
          <div className="col-span-7 space-y-4 overflow-y-auto">
            {/* STT Keywords */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-sm text-[#666666]">인입 키워드</span>
              </div>
              <div className="flex gap-2">
                <span className="px-4 py-2 bg-[#0047AB] text-white rounded-full text-sm font-medium">카드분실</span>
                <span className="px-4 py-2 bg-[#0047AB] text-white rounded-full text-sm font-medium">재발급</span>
              </div>
            </div>

            {/* Current Situation Kanban */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-lg font-semibold text-[#333333] mb-4">현재 상황 관련 정보</h3>
              <div className="grid grid-cols-2 gap-4">
                {[1, 2].map((i) => (
                  <div key={i} className="border border-[#E0E0E0] rounded-lg p-4 shadow-sm">
                    <h4 className="font-semibold text-[#0047AB] mb-2">카드 분실 신고 처리 절차</h4>
                    <div className="flex gap-2 mb-3">
                      <span className="text-xs bg-[#E8F1FC] text-[#0047AB] px-2 py-1 rounded">#분실신고</span>
                      <span className="text-xs bg-[#E8F1FC] text-[#0047AB] px-2 py-1 rounded">#즉시정지</span>
                    </div>
                    <p className="text-sm text-[#333333] line-clamp-3">
                      고객의 카드 분실 신고 시 즉시 카드 사용을 정지하고, 
                      <mark className="bg-[#FFF9C4] font-semibold">즉시 정지</mark> 처리 후 
                      <mark className="bg-[#FFF9C4] font-semibold">재발급</mark> 절차를 안내합니다.
                    </p>
                    <button className="text-sm text-[#0047AB] mt-3 hover:underline">자세히 보기</button>
                  </div>
                ))}
              </div>
            </div>

            {/* Next Steps Kanban */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-lg font-semibold text-[#333333] mb-4">다음 단계 예상 정보</h3>
              <div className="grid grid-cols-2 gap-4">
                {[1, 2].map((i) => (
                  <div key={i} className="border border-[#E0E0E0] rounded-lg p-4 shadow-sm">
                    <h4 className="font-semibold text-[#0047AB] mb-2">재발급 카드 배송 안내</h4>
                    <div className="flex gap-2 mb-3">
                      <span className="text-xs bg-[#E8F1FC] text-[#0047AB] px-2 py-1 rounded">#재발급</span>
                      <span className="text-xs bg-[#E8F1FC] text-[#0047AB] px-2 py-1 rounded">#배송</span>
                    </div>
                    <p className="text-sm text-[#333333] line-clamp-3">
                      재발급 카드는 등록된 주소로 3-5일 내 배송됩니다. 배송 추적은 모바일 앱에서 확인 가능합니다.
                    </p>
                    <button className="text-sm text-[#0047AB] mt-3 hover:underline">자세히 보기</button>
                  </div>
                ))}
              </div>
            </div>

            {/* Consultation Guide */}
            <div className="bg-[#F0F7FF] border-l-4 border-[#0047AB] rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="text-base">💡</span>
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-[#0047AB] mb-2">권장 안내 멘트</h4>
                  <p className="text-sm text-[#333333] leading-relaxed">
                    "고객님, 카드 분실 신고 접수되었습니다. 즉시 카드 사용이 정지되며, 
                    3-5일 내 재발급 카드가 등록된 주소로 배송됩니다."
                  </p>
                  <button className="text-xs text-[#0047AB] mt-2 hover:underline flex items-center gap-1">
                    <span>복사</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Column 3 - Right (~25%) - Tools */}
          <div className="col-span-4 space-y-4 overflow-y-auto">
            {/* Memo Pad */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-semibold text-[#333333] mb-3">상담 메모</h3>
              <Textarea 
                className="h-[200px] text-sm resize-none" 
                placeholder="상담 중 메모를 입력하세요..."
              />
              <Button className="w-full mt-3 bg-[#0047AB] hover:bg-[#003580]">
                <Save className="w-4 h-4 mr-2" />
                저장
              </Button>
            </div>

            {/* KMS Search */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="text-sm font-semibold text-[#333333] mb-2">직접 검색</h3>
              <p className="text-xs text-[#999999] mb-3">AI가 놓친 정보를 직접 검색하세요</p>
              <div className="relative mb-3">
                <Input 
                  className="pr-10" 
                  placeholder="검색어 입력"
                />
                <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#999999]" />
              </div>
              <Button className="w-full bg-[#4A90E2] hover:bg-[#3A7BC8]">
                검색
              </Button>
            </div>
          </div>
        </div>

        {/* 모바일 레이아웃 */}
        <div className="lg:hidden h-full overflow-y-auto space-y-3">
          {/* Call Controls - 모바일 */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <div className="flex items-center justify-between mb-3">
              <div className="text-2xl font-bold text-[#333333]">05:32</div>
              <div className="flex gap-2">
                <Button size="sm" className="bg-[#34A853] hover:bg-[#2D8F47] h-10 px-4">
                  <Phone className="w-4 h-4" />
                </Button>
                <Button 
                  size="sm"
                  className="bg-[#EA4335] hover:bg-[#C8362D] h-10 px-4"
                  onClick={() => navigate('/acw')}
                >
                  <PhoneOff className="w-4 h-4" />
                </Button>
                <Button 
                  size="sm"
                  className="bg-[#0047AB] hover:bg-[#003580] h-10 px-3"
                  onClick={() => navigate('/acw')}
                >
                  후처리
                </Button>
              </div>
            </div>
          </div>

          {/* Customer Info - 모바일 */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <h3 className="text-xs font-semibold text-[#333333] mb-2">고객 정보</h3>
            <div className="grid grid-cols-2 gap-2 text-xs text-[#666666]">
              <div><span className="font-medium">ID:</span> CUST-001</div>
              <div><span className="font-medium">이름:</span> 홍길동</div>
              <div><span className="font-medium">전화:</span> 010-1234-5678</div>
              <div><span className="font-medium">생년월일:</span> 1985-03-15</div>
            </div>
          </div>

          {/* STT Keywords - 모바일 */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <span className="text-xs text-[#666666] block mb-2">인입 키워드</span>
            <div className="flex gap-2">
              <span className="px-3 py-1.5 bg-[#0047AB] text-white rounded-full text-xs font-medium">카드분실</span>
              <span className="px-3 py-1.5 bg-[#0047AB] text-white rounded-full text-xs font-medium">재발급</span>
            </div>
          </div>

          {/* Current Situation Kanban - 모바일 */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <h3 className="text-sm font-semibold text-[#333333] mb-3">현재 상황 관련 정보</h3>
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div key={i} className="border border-[#E0E0E0] rounded-lg p-3 shadow-sm">
                  <h4 className="text-sm font-semibold text-[#0047AB] mb-2">카드 분실 신고 처리 절차</h4>
                  <div className="flex gap-1.5 mb-2">
                    <span className="text-[10px] bg-[#E8F1FC] text-[#0047AB] px-1.5 py-0.5 rounded">#분실신고</span>
                    <span className="text-[10px] bg-[#E8F1FC] text-[#0047AB] px-1.5 py-0.5 rounded">#즉시정지</span>
                  </div>
                  <p className="text-xs text-[#333333] line-clamp-3">
                    고객의 카드 분실 신고 시 즉시 카드 사용을 정지하고, 
                    <mark className="bg-[#FFF9C4] font-semibold">즉시 정지</mark> 처리 후 
                    <mark className="bg-[#FFF9C4] font-semibold">재발급</mark> 절차를 안내합니다.
                  </p>
                  <button className="text-xs text-[#0047AB] mt-2 hover:underline">자세히 보기</button>
                </div>
              ))}
            </div>
          </div>

          {/* Next Steps Kanban - 모바일 */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <h3 className="text-sm font-semibold text-[#333333] mb-3">다음 단계 예상 정보</h3>
            <div className="space-y-3">
              {[1, 2].map((i) => (
                <div key={i} className="border border-[#E0E0E0] rounded-lg p-3 shadow-sm">
                  <h4 className="text-sm font-semibold text-[#0047AB] mb-2">재발급 카드 배송 안내</h4>
                  <div className="flex gap-1.5 mb-2">
                    <span className="text-[10px] bg-[#E8F1FC] text-[#0047AB] px-1.5 py-0.5 rounded">#재발급</span>
                    <span className="text-[10px] bg-[#E8F1FC] text-[#0047AB] px-1.5 py-0.5 rounded">#배송</span>
                  </div>
                  <p className="text-xs text-[#333333] line-clamp-3">
                    재발급 카드는 등록된 주소로 3-5일 내 배송됩니다. 배송 추적은 모바일 앱에서 확인 가능합니다.
                  </p>
                  <button className="text-xs text-[#0047AB] mt-2 hover:underline">자세히 보기</button>
                </div>
              ))}
            </div>
          </div>

          {/* Consultation Guide - 모바일 */}
          <div className="bg-[#F0F7FF] border-l-4 border-[#0047AB] rounded-lg p-3">
            <div className="flex items-start gap-2">
              <span className="text-sm">💡</span>
              <div className="flex-1">
                <h4 className="text-xs font-semibold text-[#0047AB] mb-1">권장 안내 멘트</h4>
                <p className="text-xs text-[#333333] leading-relaxed">
                  "고객님, 카드 분실 신고 접수되었습니다. 즉시 카드 사용이 정지되며, 
                  3-5일 내 재발급 카드가 등록된 주소로 배송됩니다."
                </p>
                <button className="text-xs text-[#0047AB] mt-1.5 hover:underline">복사</button>
              </div>
            </div>
          </div>

          {/* Memo Pad - 모바일 */}
          <div className="bg-white rounded-lg shadow-sm p-3">
            <h3 className="text-xs font-semibold text-[#333333] mb-2">상담 메모</h3>
            <Textarea 
              className="h-[120px] text-xs resize-none" 
              placeholder="상담 중 메모를 입력하세요..."
            />
            <Button className="w-full mt-2 bg-[#0047AB] hover:bg-[#003580] h-9 text-xs">
              <Save className="w-3 h-3 mr-1.5" />
              저장
            </Button>
          </div>

          {/* KMS Search - 모바일 */}
          <div className="bg-white rounded-lg shadow-sm p-3 mb-3">
            <h3 className="text-xs font-semibold text-[#333333] mb-1.5">직접 검색</h3>
            <p className="text-[10px] text-[#999999] mb-2">AI가 놓친 정보를 직접 검색하세요</p>
            <div className="relative mb-2">
              <Input 
                className="pr-8 h-9 text-xs" 
                placeholder="검색어 입력"
              />
              <Search className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#999999]" />
            </div>
            <Button className="w-full bg-[#4A90E2] hover:bg-[#3A7BC8] h-9 text-xs">
              검색
            </Button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}