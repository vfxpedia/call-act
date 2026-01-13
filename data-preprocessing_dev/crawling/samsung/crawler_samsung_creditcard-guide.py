import requests
from bs4 import BeautifulSoup
import json
import time
import os
 
OUTPUT_DIR = "samsung_creditcard-guide"
TARGET_URL = "https://www.samsungcard.com/personal/customer-service/creditcard-guide/UHPPCC0322M0.jsp"

def crawl_content(target_url):
    # 저장 폴더 생성 
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # User-Agent 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.samsungcard.com/"
    }

    # 카테고리가 9개이므로 9번 순회
    for num in range(1, 10):
        url = f"{target_url}?ctgSeq=0{num}&ctgNo=ctgNo{num}"
        
        try:
            print(f"=== {num} 페이지 ===")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # 페이지 제목 추출
            title = soup.select_one('h2.t_fz_26')
            page_title = title.get_text(strip=True).strip()

            page_items = []
            accordion_list = soup.select('#inquire_append > li')

            # 아코디언 리스트로부터 항목명과 내용 추출
            for item in accordion_list:
                subject_el = item.select_one('p.tit')
                content_el = item.select_one('.desc_wrap')

                if subject_el and content_el:
                    subject = subject_el.get_text(strip=True)
                    content = content_el.get_text().split()[1]
                    
                    page_items.append({
                        "subject": subject,
                        "content": content
                    })

            json_data = {
                "title": page_title,
                "items": page_items
            }

            file_path = os.path.join(OUTPUT_DIR, f"{page_title}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            
            # 페이지 순회 간격 5초 대기 (마지막 페이지 제외)
            if num < 9:
                print("5초 대기 중 ...")
                time.sleep(5)

        except Exception as e:
            print(f"{num} 페이지 처리 실패: {e}")
            continue

    print(f"크롤링 완료")

if __name__ == "__main__":
    crawl_content(TARGET_URL)