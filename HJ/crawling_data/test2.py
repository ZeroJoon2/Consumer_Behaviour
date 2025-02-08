# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")  # Root 권한 문제 방지
chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 부족 방지
chrome_options.add_argument("--remote-debugging-port=9222")  # 디버깅 포트 추가
chrome_options.add_argument("--disable-gpu")  # GPU 관련 오류 방지
chrome_options.add_argument("--disable-software-rasterizer")  # 소프트웨어 렌더링 비활성화

service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://www.google.com")
print(driver.title)



