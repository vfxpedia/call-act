import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './button';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems?: number;
  itemsPerPage?: number;
}

export function Pagination({ 
  currentPage, 
  totalPages, 
  onPageChange,
  totalItems,
  itemsPerPage 
}: PaginationProps) {
  const startItem = (currentPage - 1) * (itemsPerPage || 0) + 1;
  const endItem = Math.min(currentPage * (itemsPerPage || 0), totalItems || 0);

  return (
    <div className="flex items-center justify-between py-3 px-4 border-t border-[#E0E0E0] bg-white">
      {totalItems && itemsPerPage ? (
        <div className="text-xs text-[#666666]">
          전체 <span className="font-semibold text-[#333333]">{totalItems}</span>건 중{' '}
          <span className="font-semibold text-[#333333]">{startItem}-{endItem}</span>건 표시
        </div>
      ) : (
        <div></div>
      )}
      
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="h-8 px-3 text-xs"
        >
          <ChevronLeft className="w-3.5 h-3.5 mr-1" />
          이전
        </Button>
        
        <div className="flex items-center gap-1">
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
            let pageNum;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }
            
            return (
              <Button
                key={pageNum}
                variant={currentPage === pageNum ? "default" : "outline"}
                size="sm"
                onClick={() => onPageChange(pageNum)}
                className={`h-8 w-8 p-0 text-xs ${
                  currentPage === pageNum 
                    ? 'bg-[#0047AB] text-white hover:bg-[#003580]' 
                    : 'hover:bg-[#F5F5F5]'
                }`}
              >
                {pageNum}
              </Button>
            );
          })}
        </div>
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="h-8 px-3 text-xs"
        >
          다음
          <ChevronRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>
    </div>
  );
}
