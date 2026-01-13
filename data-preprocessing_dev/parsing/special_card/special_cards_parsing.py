import pdfplumber
import json
import re
import argparse
import os

class Manager:
    def __init__(self):
        self.parsed_file = 'special_cards.json'          # 1차 처리
        self.output_file = './../../data/special_card/special_cards_vector.json'   # 2차 처리
        self.INDEX = None

    # json 파일 이어 붙이기
    def append_to_json(self, file_path, new_data):
        data_list = []
        
        # 기존 파일이 존재하면 읽어오기
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
                    if not isinstance(data_list, list):
                        data_list = []
            except (json.JSONDecodeError, ValueError):
                data_list = []

        # 새로운 데이터 추가
        if isinstance(new_data, list):
            data_list.extend(new_data)  # 리스트
        else:
            data_list.append(new_data)  # 단일 객체

        # 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)
        
        print(f"{file_path}에 데이터 추가 완료 (총 {len(data_list)}건)")


class PdfParsing(Manager):
    def __init__(self):
        super().__init__()

    # 3단 레이아웃 텍스트 추출
    def get_text_three_columns(self, fname, cardname):
        full_text = []
        print(f"{fname} 텍스트 추출")

        with pdfplumber.open(fname) as pdf:
            for i, page in enumerate(pdf.pages):
                width = page.width
                height = page.height

                one_third = width / 3
                two_third = one_third * 2

                left_bbox = (0, 0, one_third, height)
                center_bbox = (one_third, 0, two_third, height)
                right_bbox = (two_third, 0, width, height)      

                try:
                    crop_1 = page.crop(left_bbox)
                    crop_2 = page.crop(center_bbox)
                    crop_3 = page.crop(right_bbox)              

                    text_1 = crop_1.extract_text(x_tolerance=0.5) or ""
                    text_2 = crop_2.extract_text(x_tolerance=0.5) or ""
                    text_3 = crop_3.extract_text(x_tolerance=0.5) or ""        

                    page_text = text_1 + "\n" + text_2 + "\n" + text_3            
                    full_text.append(page_text)   

                except Exception as e:
                    print(f"[Page {i+1}] 오류: {e}")
                    full_text.append(page.extract_text() or "")
        
        return { "card": cardname, "content": full_text }
    
    # 2단 레이아웃 텍스트 추출
    def get_text_two_columns(self, fname, cardname):
        full_text = []
        print(f"{fname} 텍스트 추출")

        with pdfplumber.open(fname) as pdf:
            for i, page in enumerate(pdf.pages):
                width = page.width
                height = page.height

                one_second = width / 2

                left_bbox = (0, 0, one_second, height)
                right_bbox = (one_second, 0, width, height)      

                try:
                    crop_1 = page.crop(left_bbox)
                    crop_2 = page.crop(right_bbox)              

                    text_1 = crop_1.extract_text(x_tolerance=0.5) or ""
                    text_2 = crop_2.extract_text(x_tolerance=0.5) or ""        

                    page_text = text_1 + "\n" + text_2           
                    full_text.append(page_text)   

                except Exception as e:
                    print(f"[Page {i+1}] 오류: {e}")
                    full_text.append(page.extract_text() or "")
        
        return { "card": cardname, "content": full_text }

    # 4단 레이아웃 텍스트 추출
    def get_text_four_columns(self, fname, cardname):
        full_text = []
        print(f"{fname} 텍스트 추출")

        with pdfplumber.open(fname) as pdf:
            for i, page in enumerate(pdf.pages):
                width = page.width
                height = page.height

                one_fourth = width / 4
                two_fourth = one_fourth * 2
                three_fourth = one_fourth * 3

                left1_bbox = (0, 0, one_fourth, height)
                left2_bbox = (one_fourth, 0, two_fourth, height)
                right1_bbox = (two_fourth, 0, three_fourth, height)      
                right2_bbox = (three_fourth, 0, width, height)      

                try:
                    crop_1 = page.crop(left1_bbox)
                    crop_2 = page.crop(left2_bbox)
                    crop_3 = page.crop(right1_bbox)              
                    crop_4 = page.crop(right2_bbox)              

                    text_1 = crop_1.extract_text(x_tolerance=0.5) or ""
                    text_2 = crop_2.extract_text(x_tolerance=0.5) or ""
                    text_3 = crop_3.extract_text(x_tolerance=0.5) or ""        
                    text_4 = crop_4.extract_text(x_tolerance=0.5) or ""        

                    page_text = text_1 + "\n" + text_2 + "\n" + text_3 + "\n" + text_4          
                    full_text.append(page_text)   

                except Exception as e:
                    print(f"[Page {i+1}] 오류: {e}")
                    full_text.append(page.extract_text() or "")
        
        return { "card": cardname, "content": full_text }

    # 1단 레이아웃 텍스트 추출
    def get_text_one_column(self, fname, cardname):
        full_text = []
        print(f"{fname} 텍스트 추출")

        with pdfplumber.open(fname) as pdf:
            for i, page in enumerate(pdf.pages):
                try:          
                    page_text = page.extract_text(x_tolerance=0.5) or ""  
                    full_text.append(page_text)   
                except Exception as e:
                    print(f"[Page {i+1}] 오류: {e}")
        
        return { "card": cardname, "content": full_text }

    def clean_text(self, text):
        if not text:
            return ""
        
        text = text.replace('\n', ' ')
        
        # INDEX에 따라 헤더 분기 처리
        headers = []

        if self.INDEX == 0:
            headers = [
                "연회비", "할인 서비스 제외 대상", "전월 이용실적 기준", "전월 이용실적 제외 대상", 
                "실적 유예기간 적용", "부가서비스 변경 안내", "연체이자율", "해외이용 확인사항", "기 타", "지원가능 국가바우처 안내",
                "대상 가맹점에서 5% 청구할인", "단체보험 무료가입 및 사고 보장"
            ]
        elif self.INDEX == 1:
            headers = [
                "포인트리", "후불 교통기능 탑재", "공통 확인사항", "[연체이자율] 회원별, 이용상품별", 
                "군마트(P.X) 및 GS25 해군마트 환급할인", "군 KT공중전화 할인", "상해보험 무료 가입 및 사고 보장", 
                "경조사 서비스 제공", "금융수수료 면제", "발급 안내",
                "GS리테일 팝서비스", "대중교통 할인", "CGV 할인", "스타벅스 할인", "놀이공원 할인", 
                "패밀리 레스토랑 할인", "교보문고 할인", "어학시험 할인", "통신요금 자동이체 할인", "쇼핑 할인"
            ]
        elif self.INDEX == 2:
            headers = [
                "쿠팡 2% 쿠팡캐시 적립", "쿠팡 외 모든 가맹점 0.2% 쿠팡캐시 적립", "쿠팡캐시 적립 서비스 제외 대상", 
                "쿠팡캐시 안내", "연회비", "[연체료율]", "[해외 이용 확인사항]", "[부가서비스 변경 안내]", "[기타]"
            ]
        elif self.INDEX == 3:
            headers = [
                "신한카드 Point Plan(서울시다둥이행복카드) 체크 서비스 유의사항", " [기타 안내]", "고객센터", 
                "금융소비자보호제도 안내", "부가서비스 변경 안내", "해외 이용 확인사항", "체크카드 사용 시간 제한", "연회비 반환 기준", "기타 안내", "[발급 대상]", 
                "한눈에 보기", "서비스별 월 통합 적립 한도", "연회비", "신한카드 Point Plan(서울시다둥이행복카드) 체크 서비스", "일상 생활비 적립 서비스",
                "[월 통합 적립 한도 | 일상 생활비 적립 서비스]", "필수 생활비 적립 서비스", "• 주말 배달앱 포인트 적립", " • 편의점 포인트 적립", "신한카드 Point Plan(서울시다둥이행복카드) 체크 서비스 유의사항"
            ]
        elif self.INDEX == 4:
            headers = [
                "고객센터", "금융소비자보호제도 안내", "부가서비스 변경안내", "해외이용 확인사항", "체크카드 사용 시간 제한", "연회비 반환 기준", "기타 안내", "네이버페이 라인프렌즈 신한카드", 
                "[한눈에 보기]", "[연회비]", "네이버페이 포인트 적립 서비스", "[포인트 관련 세부사항]", "[포인트 적립 제외]",
            ]  

        for header in headers:
            text = re.sub(f'({re.escape(header)})', r'\n\n### \1\n', text)
        
        return text

    # 의미 단위 청킹
    def chunk_text(self, cleaned_text, card_name):
        chunks = []
        parts = cleaned_text.split('### ')
        
        for part in parts:
            part = part.strip()
            if not part: continue

            if '\n' in part:
                lines = part.split('\n', 1)
                section_title = lines[0].strip()
                content = lines[1].strip()
            else:
                continue
            
            if len(content) < 2: 
                continue

            chunk_data = {
                "id": f"{card_name}_{section_title}",
                "text": f"{card_name}/{section_title}/{content}",
                "metadata": {
                    "card_name": card_name,
                    "category": section_title,
                    "content": content
                }
            }
            chunks.append(chunk_data)
            
        return chunks

    def process_pdf_json(self, json_data):
        card_name = json_data.get("card", "Unknown Card")
        raw_contents = json_data.get("content", [])
        
        all_chunks = []
        
        full_text = " ".join(raw_contents)
        cleaned = self.clean_text(full_text)
        chunks = self.chunk_text(cleaned, card_name)
        all_chunks.extend(chunks)
            
        return all_chunks


def main():
    parser = argparse.ArgumentParser(description="pdf parsing")
    parser.add_argument(
        "--idx",
        type=int,
        required=True,
        choices=[0, 1, 2, 3, 4], 
        help=(
            "데이터 선택\n"
            "[0] 국민행복카드_국민\n"
            "[1] 나라사랑카드_국민\n"
            "[2] 쿠팡와우카드_국민\n"
            "[3] 서울시다둥이행복카드_신한\n"
            "[4] 네이버페이_신한\n"
        )
    )
    args = parser.parse_args()

    # 파일명 및 카드명 설정
    file_path = ('국민행복카드_국민.pdf', '나라사랑체크카드_국민.pdf', '쿠팡와우카드_국민.pdf', '서울시다둥이행복카드_신한.pdf', '네이버페이_신한.pdf')
    card_name = ('국민행복카드', '나라사랑체크카드', '쿠팡와우카드', '서울시다둥이행복카드', '네이버페이카드')
    
    # 인스턴스 생성
    PRI = PdfParsing()
    
    # 현재 인덱스 설정
    PRI.INDEX = args.idx
    
    current_pdf = file_path[args.idx]
    current_card = card_name[args.idx]
    
    # PDF 텍스트 추출
    print(f"\n===== PDF 파싱 시작 ({current_card}) =====")
    extracted_data = {}
    
    if args.idx == 0:
        extracted_data = PRI.get_text_three_columns(current_pdf, current_card)
    elif args.idx in (1, 3):
        extracted_data = PRI.get_text_four_columns(current_pdf, current_card)
    elif args.idx == 2:
        extracted_data = PRI.get_text_one_column(current_pdf, current_card)
    elif args.idx == 4:
        extracted_data = PRI.get_text_two_columns(current_pdf, current_card)
    
    PRI.append_to_json(PRI.parsed_file, extracted_data)    
    
    # 데이터 정제 및 청킹
    print(f"\n===== 데이터 정제 및 청킹 ({current_card}) =====")
    optimized_data = PRI.process_pdf_json(extracted_data)
    PRI.append_to_json(PRI.output_file, optimized_data)

    print("\n===== 모든 작업 완료 =====")

if __name__ == "__main__":
    main()