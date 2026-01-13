from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time
from common_module import get_driver, clean_text

driver = get_driver()
categories = ['회원정보', '적립', '지급', '카드', '이용방법']
data = []

try:
    url = "https://korea-pass.kr/notice/faqList.do"
    driver.get(url)
    time.sleep(1)

    for i in range(2, 7):
        print(f'===== {i}번째 카테고리 크롤링 =====')
        category = categories[i-2]

        tab_xpath = f'//*[@id="tab0{i}"]'
        driver.find_element(By.XPATH, tab_xpath).click()
        time.sleep(1)

        lis = driver.find_elements(By.CSS_SELECTOR, '#faqDiv > li')
        count = len(lis)
        print(f"리스트 개수 : {count}개")

        for j in range(1, count + 1):
            try:
                driver.find_element(By.XPATH, tab_xpath).click()
                time.sleep(1)

                question_xpath = f'//*[@id="faqDiv"]/li[{j}]/a'
                btn = driver.find_element(By.XPATH, question_xpath)
                
                # 질문 추출
                q_text = btn.find_element(By.TAG_NAME, 'h4').text
                q_text = clean_text(q_text)
                print(q_text)
                
                # 상세 페이지 진입
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)

                # 답변 추출
                answer_element = driver.find_element(By.CSS_SELECTOR, 'section p') 
                a_text = answer_element.text
                a_text = clean_text(a_text)
                print(a_text)

                # 데이터 저장
                data_entry = {
                    "category_index": category,
                    "id": j,
                    "question": q_text,
                    "answer": a_text
                }
                data.append(data_entry)

                driver.back()
                time.sleep(2)

            except Exception as e:
                print(f"{j}번 처리 중 오류 발생 : {e}")
                continue
    
    print("===== 데이터 저장 중 =====")
    with open('./../../data/special_card/kpass_faq.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

except Exception as e:
    print(f"오류 발생 : {e}")

finally:
    driver.quit()
