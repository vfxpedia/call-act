import requests
from bs4 import BeautifulSoup
import urllib3
import json  # json 파일 저장을 위한 모듈

# SSL 인증서 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "https://www.samsungcard.com/home/payment/cashadvance/PGHPPCCPaymentCashadvanceInfoService001"

def crawler(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.samsungcard.com/"
    }

    # 최종 데이터를 담을 딕셔너리 구조 초기화
    result_data = {
        "accordion_list": [],  # 이용방법, 한도 등 메인 아코디언
        "extra_info": [],      # 아코디언 하단 텍스트
        "footer_notice": []    # 페이지 하단 섹션
    }


    response = requests.get(url, headers=headers, verify=False, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(">>> 데이터 수집 시작...")

    # 시작점: '이용안내' 헤더 찾기
    start = soup.find(lambda tag: tag.name == "div" and "이용안내" in tag.get_text())

    # 아코디언 리스트 파싱
    accordion_article = start.find_next("article", class_="accordion")
    
    if accordion_article:
        items = accordion_article.find_all("div", class_="accordion-item")
        
        for item in items:
            # 제목 추출
            btn = item.find("button", class_="accordion-button")
            title = btn.get_text(strip=True)

            # 본문 추출
            body = item.find("div", class_="accordion-body")
            content = body.get_text(separator="\n", strip=True)
            
            result_data["accordion_list"].append({
                "title": title,
                "content": content
            })

    # 하단 추가 정보 탐색 (형제 요소 순회)
    current = accordion_article
    while current:
        current = current.find_next_sibling()
        if not current:
            break
        
        # 일반 안내 문구
        if current.name == "div" and "ready" in current.get("class", []):
            lists = current.find_all("li")
            for li in lists:
                text = li.get_text(strip=True)
                result_data["extra_info"].append(text)
        
        # 페이지 하단 안내문: '꼭 확인하세요!' 섹션
        if current.name == "section":
            check_btn = current.find("button", class_="accordion-button")
            if check_btn:
                section_title = check_btn.get_text(strip=True)
                result_data["footer_notice"]["title"] = section_title
                result_data["footer_notice"]["items"] = []

                check_body = current.find("div", class_="accordion-body")
                if check_body:
                    check_items = check_body.find_all("li")
                    for item in check_items:
                        item_text = item.get_text(strip=True)
                        result_data["footer_notice"]["items"].append(item_text)

    # json 저장
    file_name = "samsung_card_info.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)

    print("=== 작업 완료 ===")

if __name__ == "__main__":
    crawler(TARGET_URL)