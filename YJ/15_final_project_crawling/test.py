import pandas as pd

from bs4 import BeautifulSoup

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


import requests

import time

url = 'https://search.danawa.com/dsearch.php?query=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90+%EA%B0%A4%EB%9F%AD%EC%8B%9Cs24+256gb%2C+%EC%9E%90%EA%B8%89%EC%A0%9C&originalQuery=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90+%EA%B0%A4%EB%9F%AD%EC%8B%9Cs24+256gb%2C+%EC%9E%90%EA%B8%89%EC%A0%9C&checkedInfo=N&volumeType=allvs&page=1&limit=40&sort=opinionDESC&list=list&boost=true&tab=main&addDelivery=N&coupangMemberSort=N&simpleDescOpen=Y&mode=simple&isInitTireSmartFinder=N&recommendedSort=N&defaultUICategoryCode=122515&defaultPhysicsCategoryCode=224%7C48419%7C48829%7C0&defaultVmTab=8&defaultVaTab=2041&isZeroPrice=Y&quickProductYN=N&priceUnitSort=N&priceUnitSortOrder=A'
target_item = ['S24']
chrome_option = Options()
chrome_option.add_experimental_option('detach', True)

driver = webdriver.Chrome(options=chrome_option)
driver.get(url)

wait = WebDriverWait(driver,10)

wait.until(
    EC.presence_of_element_located((By.ID, 'paginationArea'))
)

# 120개 보기로 바꿈
Select(driver.find_element(by = By.CSS_SELECTOR, value = '#DetailSearch_Wrapper > div.view_opt > div > select')).select_by_value('120')

header = {'User-Agent': 'Mozila/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
res = requests.get(url, headers= header)
soup = BeautifulSoup(res.text, 'html.parser')


soup2 = soup.select('#productListArea > div.main_prodlist.main_prodlist_list > ul')
link_list = []
for i in range(0, len(soup2[0].select('a', class_ = 'click_log_prod_review_count'))):
    if soup2[0].select('a', class_ = 'click_log_prod_review_count')[i]['href'] != '#' or '':
        for target in target_item:
            if target not in soup2[0].select('a', class_ = 'click_log_prod_review_count')[0].find('img').get('alt'):
                link_list.append(soup2[0].select('a', class_ = 'click_log_prod_review_count')[i]['href'])

# 최종 리스트
link_list = [link_list[idx] for idx, link in enumerate(link_list) if 'companyReviewYN=Y' in link_list[idx]]

df = pd.DataFrame(columns = ['scoring', 'market', 'purchasing_date', 'review_title', 'review_content'])

def save_to_df(tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content):
    global df
    tmp_list = []
    for s, m, d, t, c in zip(tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content):
        tmp_list.append([s, m, d, t, c])
        
    df = pd.concat([df, pd.DataFrame(data = tmp_list, columns = ['scoring', 'market', 'purchasing_date', 'review_title', 'review_content'])])

    print('df에 저장완료!')
    return df

def df_to_file(df):
    if df.shape[0] >= 5000:
        df.to_csv('review_data.csv', mode = 'a', index = False, header = False)
        del df
        print('df 한번 지워내고, csv로 저장하기 완료 !')
    else:
        pass


def click_link():
    driver.get(link_list[0])
    review_soup = BeautifulSoup(driver.page_source, 'html.parser').select('#danawa-prodBlog-productOpinion-list-self > div.mall_review > div.area_right')[0]
    return review_soup


# 페이지 리스트 계산
def calc_page_list(review_soup):
    page_list = []
    wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#danawa-prodBlog-companyReview-content-list > div > div > div span'))
    )
    
    page_list.append(review_soup.select('#danawa-prodBlog-companyReview-content-list > div > div > div span')[0].text)
    for i in review_soup.select('#danawa-prodBlog-companyReview-content-list > div > div > div a'):
        page_list.append(i['data-pagenumber'])
    return page_list


# 다음 버튼 유무
def is_click_next_button(page_list) :
    if int(page_list[0]) + 9 == int(page_list[-1]):
        return 1

    else:
        return 0
    
# 해당 페이지 크롤링
def crawling(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    review_soup = soup.select('#danawa-prodBlog-productOpinion-list-self > div.mall_review > div.area_right')
    scoring = [i.text for i in review_soup[0].select('#danawa-prodBlog-companyReview-content-list div.top_info span.point_type_s span')]
    market = [i['alt'] for i in review_soup[0].select('#danawa-prodBlog-companyReview-content-list div.top_info span.mall img')]
    purchasing_date = [i.text for i in review_soup[0].select('#danawa-prodBlog-companyReview-content-list span.date')]
    review_title = [i.text for i in review_soup[0].select('[id^="danawa-prodBlog-companyReview-content-wrap-"] > div.atc_cont > div.tit_W')]
    review_content = [i.text for i in review_soup[0].select('div.atc')]

    return scoring, market, purchasing_date, review_title, review_content


def repit_page(): 
    while True:
        time.sleep(1)
        wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#danawa-prodBlog-productOpinion-list-self > div.mall_review > div.area_right'))
        )
        review_soup = BeautifulSoup(driver.page_source, 'html.parser').select('#danawa-prodBlog-productOpinion-list-self > div.mall_review > div.area_right')[0]
        
        page_list = calc_page_list(review_soup)
        print(page_list)
        
        for i in page_list:
            print(f'{i}페이지 시작합니다.')
            i = int(i)
            if i % 10 == 1:
                tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content = crawling(driver)
                save_to_df(tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content)
                df_to_file(df)

            elif i % 10 >= 2:
                
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'a[data-pagenumber="{i}"]'))
                )

                driver.find_element(By.CSS_SELECTOR, f'a[data-pagenumber="{i}"]').click()
                tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content = crawling(driver)
                save_to_df(tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content)
                df_to_file(df)

            elif i % 10 == 0:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'a[data-pagenumber="{i}"]'))
                )

                driver.find_element(By.CSS_SELECTOR, f'a[data-pagenumber="{i}"]').click()

                tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content = crawling(driver)
                save_to_df(tmp_scoring, tmp_market, tmp_purchasing_date, tmp_review_title, tmp_review_content)
                df_to_file(df)
                
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[id^="danawa-pagination-button-next-"] > span'))
                )
                driver.find_element(By.CSS_SELECTOR, '[id^="danawa-pagination-button-next-"] > span').click()

                print('클릭함')
        
        print(df.tail(5))
        if not driver.find_elements(By.CSS_SELECTOR, '[id^="danawa-pagination-button-next-"] > span'):
            print("모든 페이지를 처리했습니다.")
            break

click_link()
repit_page()
df.to_csv('test_py.csv', encoding='cp949')