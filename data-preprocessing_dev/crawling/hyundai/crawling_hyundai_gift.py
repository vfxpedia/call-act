import json
import re
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def crawl_hyundaicard_gift(url):
    chrome_options = Options()
    
    # User-Agent 설정
    # PC 모드로 접속 시 보안프로그램 이슈로 인해 접근이 어려우므로 모바일 모드로 설정
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # 보안 경고 및 팝업 무시 설정
    chrome_options.add_argument("--disable-popup-blocking") 
    chrome_options.add_argument("--ignore-certificate-errors")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # alert 창(설치 확인 팝업 등)이 뜰 경우 처리
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"경고창: {alert.text}")
            alert.dismiss() # '취소'를 눌러 설치 페이지 이동 방지
        except:
            pass

        time.sleep(3) # 페이지 로딩 대기

        # HTML 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        page_title = soup.select_one('h1, h2.tit')
        if page_title:
            category = page_title.get_text(strip=True)
            
        filename = re.sub(r'[\\/*?:"<>|]', "", category) + ".json"
        print(f"카테고리: {category}")

        # 데이터 추출
        content_data = []
        
        # 범용적으로 텍스트 덩어리를 찾는 방식
        sections = soup.select('.cnt_section, .content_block, #content')
        
        if not sections:
            sections = [soup.body]

        for section in sections:
            items = section.select('h3, h4, dt, strong.tit')
            
            for item in items:
                title_text = item.get_text(strip=True)
                if not title_text: continue

                details = []
                curr = item.find_next_sibling()
                
                # 다음 제목이 나오기 전까지 내용 수집
                while curr:
                    if curr.name in ['h3', 'h4', 'dt']: # 다음 아이템 시작이면 중단
                        break
                    
                    text = curr.get_text("\n", strip=True)
                    if text and curr.name not in ['script', 'style', 'button']:
                        details.append(text)
                    
                    curr = curr.find_next_sibling()
                
                if details:
                    content_data.append({
                        "item": title_text,
                        "details": "\n".join(details)
                    })

        # 결과 저장
        result = {
            "category": category,
            "data": content_data
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print(f"저장 완료: {filename} (항목 {len(content_data)}개)")

    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    TARGET_URL = "https://www.hyundaicard.com/cpc/cr/CPCCR0644_89.hc"

    crawl_hyundaicard_gift(TARGET_URL)