import { useEffect } from 'react';
import { X, FileText } from 'lucide-react';
import { scenarios } from '@/data/scenarios';

interface DocumentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;  // 'card-1-1-1' 형식
}

export default function DocumentDetailModal({ isOpen, onClose, documentId }: DocumentDetailModalProps) {
  // ⭐ scenarios에서 document_id로 문서 찾기
  const findDocument = () => {
    for (const scenario of scenarios) {
      for (const step of scenario.steps) {
        // currentSituationCards 검색
        const foundInCurrent = step.currentSituationCards.find(card => card.id === documentId);
        if (foundInCurrent) return foundInCurrent;
        
        // nextStepCards 검색
        const foundInNext = step.nextStepCards.find(card => card.id === documentId);
        if (foundInNext) return foundInNext;
      }
    }
    return null;
  };

  const docData = findDocument();  // ⭐ 변수명 변경: document → docData

  // ⭐ ESC 키 이벤트 리스너 추가
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        e.stopPropagation();  // ⭐ 이벤트 전파 중단 (상위 모달로 전달 방지)
        onClose();
      }
    };

    if (isOpen) {
      window.document.addEventListener('keydown', handleEscape);
      // 모달 열릴 때 body 스크롤 잠금 (이미 FrequentInquiryModal에서 설정되어 있으므로 중복 방지)
      // window.document.body.style.overflow = 'hidden';
    }

    return () => {
      window.document.removeEventListener('keydown', handleEscape);
      // 스크롤 복원은 FrequentInquiryModal이 처리하므로 여기서는 하지 않음
      // window.document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !docData) return null;  // ⭐ document → docData

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60]"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-lg w-full max-w-3xl max-h-[90vh] overflow-hidden shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-[#0047AB] to-[#4A90E2] p-4 text-white flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="w-5 h-5" />
              <span className="text-xs opacity-90">문서 상세보기</span>
            </div>
            <h2 className="text-lg font-bold">{docData.title}</h2>
            <div className="flex items-center gap-3 mt-2 text-xs opacity-90">
              <span>근거 규정: {docData.regulation}</span>
              <span>•</span>
              <span>처리 시간: {docData.time}</span>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-white hover:bg-white/20 p-1.5 rounded transition-colors flex-shrink-0"
            aria-label="닫기 (ESC)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
          {/* 요약 */}
          <div className="mb-4 bg-[#F8FAFB] rounded-lg border border-[#E0E0E0] p-3">
            <h3 className="text-xs font-bold text-[#333333] mb-2">📋 요약</h3>
            <p className="text-xs text-[#666666] leading-relaxed">
              {docData.content}
            </p>
          </div>

          {/* 시스템 경로 */}
          <div className="mb-4 bg-[#FFF9E6] rounded-lg border border-[#FBBC04]/30 p-3">
            <h3 className="text-xs font-bold text-[#333333] mb-2">💻 시스템 경로</h3>
            <p className="text-xs text-[#666666] font-mono">
              {docData.systemPath}
            </p>
          </div>

          {/* 필수 확인 사항 */}
          <div className="mb-4">
            <h3 className="text-xs font-bold text-[#333333] mb-2">✅ 필수 확인 사항</h3>
            <div className="space-y-1.5">
              {docData.requiredChecks.map((check, index) => (
                <div key={index} className="flex items-start gap-2 text-xs text-[#333333]">
                  <span className="text-[#0047AB] flex-shrink-0">•</span>
                  <span>{check}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 예외 사항 */}
          {docData.exceptions.length > 0 && (
            <div className="mb-4">
              <h3 className="text-xs font-bold text-[#333333] mb-2">⚠️ 예외 사항</h3>
              <div className="space-y-1.5">
                {docData.exceptions.map((exception, index) => (
                  <div key={index} className="flex items-start gap-2 text-xs text-[#EA4335]">
                    <span className="flex-shrink-0">•</span>
                    <span>{exception}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 참고사항 */}
          {docData.note && (
            <div className="mb-4 bg-[#E8F1FC] rounded-lg border border-[#0047AB]/30 p-3">
              <h3 className="text-xs font-bold text-[#333333] mb-2">💡 참고사항</h3>
              <p className="text-xs text-[#666666]">
                {docData.note}
              </p>
            </div>
          )}

          {/* 전체 약관 */}
          <div className="border-t border-[#E0E0E0] pt-4">
            <h3 className="text-xs font-bold text-[#333333] mb-3">📄 전체 약관</h3>
            <div className="text-xs text-[#333333] leading-relaxed whitespace-pre-wrap bg-[#FAFAFA] rounded-lg p-4 border border-[#E0E0E0]">
              {docData.fullText}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-[#E0E0E0] p-3 bg-[#F8F9FA] flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs bg-[#0047AB] hover:bg-[#003580] text-white rounded-md transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}