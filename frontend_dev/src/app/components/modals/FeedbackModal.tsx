import { X, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '../ui/button';
import { useState, useEffect } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { 
  mockFeedbackData,
  calculateAcwTimeScore,
  getManualComplianceMessage,
  getGratitudeMessage,
  getAcwTimeMessage,
  getEmotionTransitionMessage,
  getAhtMessage
} from '../../../data/feedbackRules';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  acwTimeSeconds?: number; // ⭐ 실제 후처리 시간 (초 단위)
  callTimeSeconds?: number; // ⭐ 통화 시간 (초 단위)
}

export default function FeedbackModal({ 
  isOpen, 
  onClose, 
  onConfirm, 
  acwTimeSeconds = 0,
  callTimeSeconds = 0
}: FeedbackModalProps) {
  const [dontShowToday, setDontShowToday] = useState(false);
  const [showDetailScores, setShowDetailScores] = useState(false);

  // ⭐ 후처리 시간 점수 계산 (업계 표준 기준: 45초 기준)
  const acwScore = acwTimeSeconds > 0 ? calculateAcwTimeScore(acwTimeSeconds) : mockFeedbackData.acwTime;
  
  // ⭐ 시간 포맷팅 함수
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}분 ${secs}초`;
  };

  const acwTimeDisplay = acwTimeSeconds > 0 ? formatTime(acwTimeSeconds) : '측정 중';
  const callTimeDisplay = callTimeSeconds > 0 ? formatTime(callTimeSeconds) : localStorage.getItem('consultationCallTime') 
    ? formatTime(parseInt(localStorage.getItem('consultationCallTime') || '0'))
    : '0분 0초';
  
  // ⭐ AHT 계산 (Average Handle Time)
  const actualCallTime = callTimeSeconds > 0 
    ? callTimeSeconds 
    : parseInt(localStorage.getItem('consultationCallTime') || '0');
  const ahtSeconds = actualCallTime + (acwTimeSeconds > 0 ? acwTimeSeconds : 0);
  const ahtDisplay = formatTime(ahtSeconds);

  // ⭐ 총점 재계산 (후처리 시간 반영)
  const totalScore = mockFeedbackData.manualCompliance + 
                     mockFeedbackData.customerGratitude + 
                     acwScore + 
                     mockFeedbackData.emotionTransition;

  // ⭐ 오각형 차트 데이터 (5개 항목: 도입부, 응대, 설명, 적극성, 정확성)
  const radarData = [
    { category: '도입부', score: 9.5, maxScore: 10 },
    { category: '응대', score: 10, maxScore: 10 },
    { category: '설명', score: 10, maxScore: 10 },
    { category: '적극성', score: 10, maxScore: 10 },
    { category: '정확성', score: 10, maxScore: 10 },
  ];

  // ⭐ 감정 이모지 매핑
  const emotionEmoji = {
    negative: '😠',
    neutral: '😐',
    positive: '😊',
  };

  const emotionColor = {
    negative: '#EA4335',
    neutral: '#666666',
    positive: '#34A853',
  };

  const emotionText = {
    negative: '부정적',
    neutral: '중립',
    positive: '긍정적',
  };

  // ⭐ 메시지 함수 호출
  const manualMessage = getManualComplianceMessage(mockFeedbackData.manualCompliance);
  const gratitudeMessage = getGratitudeMessage(mockFeedbackData.customerGratitude);
  const acwMessage = getAcwTimeMessage(acwTimeSeconds > 0 ? acwTimeSeconds : mockFeedbackData.acwTimeSeconds);
  const emotionMessage = getEmotionTransitionMessage(mockFeedbackData.emotionTransition, mockFeedbackData.emotion);
  const ahtMessage = getAhtMessage(ahtSeconds);

  // ⭐ "확인" 버튼 클릭
  const handleConfirm = () => {
    if (dontShowToday) {
      const today = new Date().toDateString();
      localStorage.setItem('feedbackDontShowUntil', today);
    }
    onConfirm();
  };

  // ⭐ ESC 키로 모달 닫기, Enter 키로 확인
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (!isOpen) return;
      
      if (event.key === 'Escape') {
        onClose();
      } else if (event.key === 'Enter') {
        event.preventDefault();
        handleConfirm();
      }
    };

    if (isOpen) {
      window.addEventListener('keydown', handleEscKey);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      window.removeEventListener('keydown', handleEscKey);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose, handleConfirm]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        {/* 헤더 */}
        <div className="bg-gradient-to-r from-[#0047AB] to-[#003580] text-white p-4 rounded-t-lg flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div>
              <h2 className="text-lg font-bold">🎯 상담 품질 피드백</h2>
              <p className="text-xs opacity-90">AI 분석 기반 상담 품질 평가</p>
            </div>
            <div className="flex items-center gap-2 ml-6">
              <span className="text-2xl font-bold">{totalScore}</span>
              <span className="text-sm opacity-90">/ 100점</span>
              <span className="ml-2 px-3 py-1 bg-white/20 rounded-full text-xs font-semibold">
                {totalScore >= 90 ? '우수' : totalScore >= 80 ? '양호' : totalScore >= 70 ? '보통' : '개선 필요'}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 본문 */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* 2열 레이아웃: 좌측 오각형 차트 + 우측 점수 */}
          <div className="grid grid-cols-2 gap-6 mb-5">
            {/* 좌측: 오각형 차트 */}
            <div className="bg-[#F8FBFF] rounded-lg p-4 border border-[#0047AB]/10">
              <p className="text-sm font-semibold text-[#333333] mb-3 text-center">매뉴얼 준수 5개 항목</p>
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#E0E0E0" />
                  <PolarAngleAxis 
                    dataKey="category" 
                    tick={({ payload, x, y, textAnchor, index }: any) => {
                      const data = radarData[index];
                      return (
                        <g>
                          <text 
                            x={x} 
                            y={y - 5} 
                            textAnchor={textAnchor} 
                            fill="#666666" 
                            fontSize="12" 
                            fontWeight="500"
                          >
                            {payload.value}
                          </text>
                          <text 
                            x={x} 
                            y={y + 9} 
                            textAnchor={textAnchor} 
                            fill="#999999" 
                            fontSize="9"
                          >
                            ({data.score})
                          </text>
                        </g>
                      );
                    }}
                  />
                  <PolarRadiusAxis 
                    angle={90} 
                    domain={[0, 10]} 
                    tick={false}
                  />
                  <Radar 
                    name="점수" 
                    dataKey="score" 
                    stroke="#0047AB" 
                    fill="#0047AB" 
                    fillOpacity={0.6}
                    strokeWidth={2}
                  />
                </RadarChart>
              </ResponsiveContainer>
              <p className="text-center text-xs text-[#666666] mt-2">
                각 항목 10점 만점
              </p>
            </div>

            {/* 우측: 4개 주요 점수 */}
            <div className="space-y-3">
              {/* 1. 매뉴얼 준수 */}
              <div className="p-3 bg-[#F8FBFF] rounded-lg border border-[#0047AB]/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-[#333333]">
                    1. 매뉴얼 준수 <span className="text-xs text-[#666666]">- {manualMessage}</span>
                  </span>
                  <span className="text-sm font-bold text-[#0047AB]">
                    {mockFeedbackData.manualCompliance}/50
                  </span>
                </div>
                <div className="bg-[#E0E0E0] h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#0047AB] h-full rounded-full transition-all duration-500"
                    style={{ width: `${(mockFeedbackData.manualCompliance / 50) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-[#666666] mt-1">
                  {Math.round((mockFeedbackData.manualCompliance / 50) * 100)}%
                </p>
              </div>

              {/* 2. 고객 감사 표현 */}
              <div className="p-3 bg-[#F8FBFF] rounded-lg border border-[#34A853]/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-[#333333]">
                    2. 고객 감사 <span className="text-xs text-[#666666]">- {gratitudeMessage}</span>
                  </span>
                  <span className="text-sm font-bold text-[#34A853]">
                    {mockFeedbackData.customerGratitude}/10
                  </span>
                </div>
                <div className="bg-[#E0E0E0] h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#34A853] h-full rounded-full transition-all duration-500"
                    style={{ width: `${(mockFeedbackData.customerGratitude / 10) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-[#666666] mt-1">
                  {Math.round((mockFeedbackData.customerGratitude / 10) * 100)}%
                </p>
              </div>

              {/* 3. 후처리 시간 */}
              <div className="p-3 bg-[#F8FBFF] rounded-lg border border-[#34A853]/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-[#333333]">
                    3. 후처리 <span className="text-xs text-[#666666]">- ⌛{acwTimeDisplay} {acwMessage}</span>
                  </span>
                  <span className="text-sm font-bold text-[#34A853]">
                    {acwScore}/20
                  </span>
                </div>
                <div className="bg-[#E0E0E0] h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#34A853] h-full rounded-full transition-all duration-500"
                    style={{ width: `${(acwScore / 20) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-[#666666] mt-1">
                  {Math.round((acwScore / 20) * 100)}%
                </p>
              </div>

              {/* 4. 감정 전환 */}
              <div className="p-3 bg-[#F8FBFF] rounded-lg border border-[#FBBC04]/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-[#333333]">
                    4. 감정 전환 <span className="text-xs text-[#666666]">- {emotionMessage}</span>
                  </span>
                  <span className="text-sm font-bold text-[#FBBC04]">
                    {mockFeedbackData.emotionTransition}/20
                  </span>
                </div>
                <div className="bg-[#E0E0E0] h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#FBBC04] h-full rounded-full transition-all duration-500"
                    style={{ width: `${(mockFeedbackData.emotionTransition / 20) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-[#666666] mt-1">
                  {Math.round((mockFeedbackData.emotionTransition / 20) * 100)}%
                </p>
              </div>
            </div>
          </div>

          {/* AHT (Average Handle Time) */}
          <div className="mb-5 p-4 bg-gradient-to-r from-[#F8FBFF] to-[#FFF9F0] rounded-lg border border-[#0047AB]/20">
            <p className="text-sm font-semibold text-[#333333] mb-3 text-center">💼 총 처리 시간 (AHT)</p>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-[#666666] mb-1">📞 통화 시간</p>
                <p className="text-lg font-bold text-[#0047AB]">{callTimeDisplay}</p>
              </div>
              <div>
                <p className="text-xs text-[#666666] mb-1">⏱️ 후처리 시간</p>
                <p className="text-lg font-bold text-[#34A853]">{acwTimeDisplay}</p>
              </div>
              <div>
                <p className="text-xs text-[#666666] mb-1">💼 총 AHT</p>
                <p className="text-lg font-bold text-[#FBBC04]">{ahtDisplay}</p>
              </div>
            </div>
            <p className="text-center text-xs text-[#666666] mt-3">
              {ahtMessage}
            </p>
          </div>

          {/* 감정 변화 */}
          <div className="mb-5 p-4 bg-[#F8FBFF] rounded-lg border border-[#0047AB]/20">
            <p className="text-sm font-semibold text-[#333333] mb-3">감정 변화</p>
            <div className="flex items-center justify-center gap-3">
              <div className="text-center">
                <div className="text-3xl mb-1">{emotionEmoji[mockFeedbackData.emotion.early]}</div>
                <div className="text-xs font-semibold" style={{ color: emotionColor[mockFeedbackData.emotion.early] }}>
                  초반: {emotionText[mockFeedbackData.emotion.early]}
                </div>
              </div>
              <div className="text-[#666666] text-xl">→</div>
              <div className="text-center">
                <div className="text-3xl mb-1">{emotionEmoji[mockFeedbackData.emotion.middle]}</div>
                <div className="text-xs font-semibold" style={{ color: emotionColor[mockFeedbackData.emotion.middle] }}>
                  중반: {emotionText[mockFeedbackData.emotion.middle]}
                </div>
              </div>
              <div className="text-[#666666] text-xl">→</div>
              <div className="text-center">
                <div className="text-3xl mb-1">{emotionEmoji[mockFeedbackData.emotion.late]}</div>
                <div className="text-xs font-semibold" style={{ color: emotionColor[mockFeedbackData.emotion.late] }}>
                  후반: {emotionText[mockFeedbackData.emotion.late]}
                </div>
              </div>
            </div>
          </div>

          {/* 개선 필요 사항 */}
          {mockFeedbackData.manualDetails.customerCheck < 0 && (
            <div className="mb-5 p-3 bg-[#FFF9E6] border border-[#FBBC04] rounded-lg">
              <p className="text-sm text-[#666666]">
                ⚠️ <span className="font-semibold text-[#EA4335]">개선 필요:</span> 고객확인 시 정보 누출 (
                {mockFeedbackData.manualDetails.customerCheck}점)
              </p>
            </div>
          )}

          {/* 매뉴얼 상세 점수 보기 (접었다 폈다) */}
          <div className="mb-5">
            <button
              onClick={() => setShowDetailScores(!showDetailScores)}
              className="w-full p-3 bg-[#F5F5F5] hover:bg-[#E0E0E0] rounded-lg flex items-center justify-between transition-colors"
            >
              <span className="text-sm font-semibold text-[#666666]">
                {showDetailScores ? '▼' : '▶'} 매뉴얼 상세 점수 보기 (9개 항목)
              </span>
              {showDetailScores ? (
                <ChevronUp className="w-4 h-4 text-[#666666]" />
              ) : (
                <ChevronDown className="w-4 h-4 text-[#666666]" />
              )}
            </button>

            {showDetailScores && (
              <div className="mt-3 grid grid-cols-2 gap-2">
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">첫/끝인사</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.greeting === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.greeting}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">고객확인</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.customerCheck === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.customerCheck}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">호응어</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.empathy === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.empathy}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">사과/대기표현</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.apology === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.apology}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">커뮤니케이션</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.communication === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.communication}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">알기 쉬운 설명</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.explanation === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.explanation}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">적극성</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.proactiveness === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.proactiveness}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0]">
                  <span className="text-xs text-[#666666]">언어표현</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.language === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.language}점
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 bg-white rounded border border-[#E0E0E0] col-span-2">
                  <span className="text-xs text-[#666666]">정확한 업무처리</span>
                  <span className={`text-xs font-semibold ${mockFeedbackData.manualDetails.accuracy === 0 ? 'text-[#34A853]' : 'text-[#EA4335]'}`}>
                    {mockFeedbackData.manualDetails.accuracy}점
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* "오늘 하루 보지 않기" 체크박스 */}
          <div className="bg-[#FFF9E6] border border-[#FBBC04] rounded-lg p-3 flex items-center gap-3">
            <input
              type="checkbox"
              id="dontShowToday"
              checked={dontShowToday}
              onChange={(e) => setDontShowToday(e.target.checked)}
              className="w-4 h-4 rounded border-[#FBBC04] text-[#FBBC04] focus:ring-[#FBBC04]"
            />
            <label htmlFor="dontShowToday" className="text-sm text-[#666666] cursor-pointer flex-1">
              오늘 하루 피드백 보지 않고 업무 집중하기
            </label>
          </div>
        </div>

        {/* 푸터 */}
        <div className="p-4 border-t border-[#E0E0E0] flex gap-3 justify-end bg-[#FAFAFA] rounded-b-lg">
          <Button
            variant="outline"
            onClick={onClose}
            className="px-6"
          >
            닫기
          </Button>
          <Button
            onClick={handleConfirm}
            className="px-6 bg-[#0047AB] hover:bg-[#003580]"
          >
            확인
          </Button>
        </div>
      </div>
    </div>
  );
}