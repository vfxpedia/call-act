from selenium.webdriver.common.by import By
import json
import time
from common_module import get_driver, clean_text

driver = get_driver()
data = []

try:
    url = "http://www.voucher.go.kr/customer/faq/list.do"
    driver.get(url)
    time.sleep(1)

    for i in range(2):
        # 페이지 이동
        if i == 1:
            tab_xpath = '//*[@id="bodyContentWrap"]/div[2]/div/div/button[2]'
            
            next_btn = driver.find_element(By.XPATH, tab_xpath)
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)

        print(f'===== {i}번째 페이지 크롤링 =====')
        lis = driver.find_elements(By.CSS_SELECTOR, 'tbody > tr > td > a')
        count = len(lis)
        print(f"리스트 개수 : {count}개")
        
        
        for j in range(1, count + 1):
            try:
                # 상세 페이지 진입
                xpath = f'//*[@id="bodyContentWrap"]/div[2]/table/tbody/tr[{j}]/td[3]/a'
                btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)
                
                # 질문 추출
                question_element = driver.find_element(By.CSS_SELECTOR, '.title') 
                q_text = question_element.text
                q_text = clean_text(q_text)
                print(q_text)

                # 답변 추출
                answer_element = driver.find_element(By.CSS_SELECTOR, '.content-container') 
                a_text = answer_element.text
                a_text = clean_text(a_text)
                print(a_text)

                # 데이터 저장
                data_entry = {
                    "question": q_text,
                    "answer": a_text
                }
                data.append(data_entry)
                
                # 페이지 이동
                if i == 1:
                    tab_xpath = '//*[@id="bodyContentWrap"]/div[2]/div/div/button[2]'
                    
                    next_btn = driver.find_element(By.XPATH, tab_xpath)
                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(2)

            except Exception as e:
                print(f"{j}번 처리 중 오류 발생 : {e}")
                continue

    # JSON 저장
    print("===== 데이터 저장 중 =====")
    with open('./../../data/special_card/national_happiness_faq.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

except Exception as e:
    print(f"오류 발생 : {e}")

finally:
    driver.quit()