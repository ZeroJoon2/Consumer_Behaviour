#!/usr/bin/env python
# coding: utf-8

# # 1. 필요 라이브러리

import os
import pandas as pd
pd.set_option('display.max_colwidth', None)
import matplotlib.pyplot as plt
import re

from pyspark.sql.functions import col, to_timestamp
import pymysql
import mysql.connector
import pandas as pd
from kiwi import kiwi
from kiwipiepy import Kiwi
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
from konlpy.tag import Kkma
from umap.umap_ import UMAP
import hdbscan
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from pyspark.sql.functions import col, to_timestamp
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification, pipeline
import torch
import emoji
from soynlp.normalizer import repeat_normalize

# 내 노트북에 설치되어있는 글꼴 list 확인
import matplotlib.font_manager as fm
font_list = fm.findSystemFonts(fontpaths = None, fontext = 'ttf')
font_list [:]

# font 경로 설정
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

# 계속되는 글꼴 깨짐으로 Matplotlib의 폰트 설정을 강제로 적용 
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rc('font', family='NanumGothic')

# 마이너스(-) 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# 폰트 적용 확인
print(fm.findSystemFonts(fontpaths=None, fontext='ttf'))
print(plt.rcParams['font.family'])

# # 2. 환경변수 설정
os.environ['PYSPARK_PYTHON'] = '/home/ubuntu/anaconda3/envs/Project/bin/python'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/home/ubuntu/anaconda3/envs/Project/bin/python'
os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars /usr/local/lib/mysql-connector-java-5.1.49-bin.jar pyspark-shell'


# # 3. MySQL에서 테이블 로드
host_ip = "15.168.221.131"  
DATABASE = "SNS_DB"
user_id = "lab13"
user_password = "lab13"
mysql_url = f"jdbc:mysql://{host_ip}:3306/{DATABASE}"

connection = mysql.connector.connect(
    host='localhost',
    user='lab13',
    password='lab13',
    database='SNS_DB',
    charset='utf8mb4'
)

cursor = connection.cursor()
cursor.execute("SHOW TABLES;")  
for table in cursor.fetchall():
    print(table[0])

table_name = "tbCrawled_Danawa"
cursor.execute(f"SELECT * FROM {table_name} LIMIT 10;") 
rows = cursor.fetchall()
for row in rows:
    print(row)

# # 4. 판다스 df로 변환

# SQL 실행 후 데이터를 가져오기
cursor.execute(f"SELECT * FROM {table_name};")
data = cursor.fetchall()

# 데이터 컬럼명 자동 설정 (이전 코드에서 오류 원인 해결)
columns = [desc[0] for desc in cursor.description]  # SQL에서 실제 컬럼명 가져오기

# pandas DataFrame 변환
df_danawa = pd.DataFrame(data, columns=columns)  # 🔥 컬럼 개수를 자동으로 맞춤

# 데이터 확인
df_danawa.head()

# # 5. 데이터 전처리

# ## 5-3 텍스트 정제 

# 나중에 문장을 쪼개기 편리하게 온점, 물음표, 느낌표의 특수문자는 유지
import re
import pandas as pd

# 한국어, 영어, 숫자만 남기고 정제하는 함수
def clean_text(text):
    if isinstance(text, str):  # 문자열인지 확인
        text = text.lower()  # 영어 소문자로 변환
        text = re.sub(r'[^가-힣a-zA-Z0-9\s.,!?]', '', text) # 온점, 콤마, 느낌표, 물음표 유지
        text = re.sub(r'\s+', ' ', text).strip()  # 연속된 공백 제거
        return text
    return ""

# 데이터프레임의 리뷰 컬럼 정제
df_danawa['clean_review'] = df_danawa['review_content'].apply(clean_text)

# 정제된 데이터 확인 (원본 vs 정제된 리뷰 비교)
df_danawa[['review_content', 'clean_review']].head(3)

# ### 5-3-2 불용어 제거

import pandas as pd
import re

# 불용어 리스트
#stopwords = {'잘', '좋아요', '너무', '빠르고', '배송', '정말', '매우'}
stopwords = {'잘', '너무', '정말', '매우'}

# 불용어 제거 함수
def remove_stopwords(text):
    words = text.split()
    return ' '.join([word for word in words if word not in stopwords])

# 불용어 제거 적용
df_danawa['clean_review'] = df_danawa['review_content'].astype(str).apply(remove_stopwords)

# 원본리뷰 vs 불용어 제거된 리뷰 비교
df_danawa[['review_content', 'clean_review']].head(3)

# ### 5-3-3 워드클라우드 확인: 데이터전처리(정제), 불용어 제거 후

import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import re

df_danawa[['clean_review']].head(3)

## all_word 꼭 실행!!-> 밑에 워드 클라우드 실행 시킬 수 있음.
# 'clean_review' 컬럼에서 모든 텍스트 가져오기
all_words = ' '.join(df_danawa['clean_review'])

# 워드클라우드 생성
wordcloud = WordCloud(
    font_path="/Library/Fonts/NanumBarunGothicBold.ttf", 
    width=800,
    height=400,
    background_color='white'
).generate(all_words)

# 워드클라우드 시각화
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # 축 제거
plt.title("다나와 리뷰 워드클라우드 (불용어 제거 후)", fontsize=15)
plt.show()

# Okt 형태소 분석기 객체 생성 
okt = Okt()

# 명사 추출 함수 정의
def extract_nouns(text):
    return okt.nouns(text)  # 명사만 추출

# 'clean_review' 컬럼에서 명사만 추출하여 새로운 'nouns' 컬럼 생성
df_danawa['nouns'] = df_danawa['clean_review'].apply(extract_nouns)

# 'nouns' 컬럼 확인
df_danawa[['clean_review', 'nouns']].head(3)

# # 6. 데이터 분석

# clean_review에서 명사 추출 -> 여기서 추출된 명사 데이터 기반으로 감성분석 진행 예정 (clean_review 명사추출: 5-4-4참고,명사추출 후 실행하기 -> extract_nouns )
df_danawa['nouns'] = df_danawa['clean_review'].apply(extract_nouns)

# 감성 분석을 위한 전역 변수 선언 # 감성 분석 함수 정의 -> 이걸 실행해서 (sentiment_analysis)가 실행됨.
positive_words = ["좋아요", "만족", "최고", "훌륭", "추천", "완벽"]
negative_words = ["별로", "실망", "부족", "최악", "문제", "불만"]

# 감성 분석 함수 (긍정/부정/중립)
def sentiment_analysis(nouns):
    pos_count = sum(1 for word in nouns if word in positive_words)
    neg_count = sum(1 for word in nouns if word in negative_words)

    if pos_count > neg_count:
        return "positive"
    elif pos_count < neg_count:
        return "negative"
    else:
        return "neutral"

# 감성 분석 적용
df_danawa['sentiment'] = df_danawa['nouns'].apply(sentiment_analysis)

# 확인
df_danawa[['nouns', 'sentiment']].head(5)

# 감성 분석 적용 (clean_review 기반) 
# 5-4-3에서 명사만 추출된 'nouns'실행하기 
#df_danawa['sentiment'] = df_danawa['nouns'].apply(sentiment_analysis)

#nouns가 float 형식이라 astype(str)을 적용해서 리스트 형식으로 변경해야함. -> 그래서...밑에서 항상 float 오류가..
df_danawa['sentiment'] = df_danawa['nouns'].astype(str).apply(sentiment_analysis)

# clean_review & item 컬럼 가져오기 
df_selected = df_danawa[['clean_review', 'item']]

# 결과 확인
df_selected.head(3)  

# #### **(1) 아이폰16 (아이폰)**

# 'item'이 '아이폰16'인 데이터에서 'clean_review'만 선택
iphone16_reviews = df_danawa[df_danawa['item'] == '아이폰16'][['clean_review']]

# 결과 확인
iphone16_reviews.head(3)

# 불용어 목록 추가 (제품과 관련 없는 단어들)
stopwords = [
    "배송", "포장", "택배", "차로", "도착", "혜택", "이벤트", "기기", "폰", "그냥", "쇼핑몰", 
    "매우", "자주", "선택", "아쉬움", "바로", "아들","다른", "하이마트", "박살", "이자", "것",
    "주문", "번가", "일단", "화면", "앱", "사용", "프로그램", "기능", "세트", "셀", "데저트", 
    "영상", "진짜", "하이마트", "예약", "사전예약", "부모님", "할인", "개통", "고객", "상담", 
    "선물", "소비자", "생일", "상태", "일정", "반품", "예정", "아이폰", "갤럭시", "구매",
    "구매자", "사전예약", "배송일", "정책","롯데", 
]

# 명사 추출 함수 (불용어 제거)
def extract_nouns_without_stopwords(text):
    nouns = okt.nouns(text)
    return [word for word in nouns if word not in stopwords]  # 불용어 제거

# item이 '아이폰16'인 clean_review에서 명사 추출
df_danawa['nouns'] = df_danawa[df_danawa['item'] == '아이폰16']['clean_review'].apply(extract_nouns_without_stopwords)

# 'nouns' 열 확인
df_danawa['nouns'].head(3)

# 'nouns' 열에서 NaN 값이나 숫자 값 제거
df_danawa['nouns'] = df_danawa['nouns'].apply(lambda x: [] if isinstance(x, float) or isinstance(x, int) else x)

# 그 후 sentiment_analysis 적용
df_danawa['sentiment'] = df_danawa['nouns'].apply(sentiment_analysis)

# 감성 분석 함수 (긍정/부정/중립)
def sentiment_analysis(nouns):
    pos_count = sum(1 for word in nouns if word in positive_words)
    neg_count = sum(1 for word in nouns if word in negative_words)
    
    if pos_count > neg_count:
        return "positive"
    elif pos_count < neg_count:
        return "negative"
    else:
        return "neutral"

# 감성 분석 적용
df_danawa['sentiment'] = df_danawa['nouns'].apply(sentiment_analysis)

# 긍정적, 부정적 리뷰 분류
positive_reviews = df_danawa[df_danawa['sentiment'] == 'positive']['nouns']
negative_reviews = df_danawa[df_danawa['sentiment'] == 'negative']['nouns']

# 명사 리스트 생성
positive_nouns = sum(positive_reviews.tolist(), [])
negative_nouns = sum(negative_reviews.tolist(), [])

# 각 리뷰의 긍정, 부정 단어 카운트
positive_counts = Counter(positive_nouns)
negative_counts = Counter(negative_nouns)


# - 30개 

# 제외할 단어 리스트 (# 워드클라우드에서 제외하고 싶은 단어들)
exclude_words = {
    "문제", "구매", "최고", "만족", "실망", "별로","구입","포인트", "정말","추천","생각", 
    "상품","재고","박스","프로","역시", "처음", "실물", "저", "하루", "슈팅", "마음", "좀", 
    "사람", "이건", "아주", "역시", "완전", "눈", "더", "차", "처음", "저", "고민", "좀", "아주",
    "반", "제", "토요일", "다만", "당일", "주변", "파손", "걱정", "왜", "일찍", "햇", "이", "제품", "다음",
     "핑꾸핑꾸", "양품", "자급","하하","개도", "알짝", "롯데", "예정일", "기도", "출시일", "맥스",
    "할부", "움", "점", "게", "줄", "미니", "후", "쿠팡", "오전", "색상", "화이트", "디자인",
    "리뷰", "애플", "교체", "구오", "듭니", "부시", "취소", "날", "때문", "실수", "티타늄", "컬러",
    "색", "보고", "수", "때", "무", "굿", "로", "불량", "일반", "예상", "케이스", "하자", "나", 
    "휴대폰", "불만", "블랙", "롯대", "일", "교환", '짱짱', '재', '및' '이번', '만', '사서', 
    '나름', '물건', '듯', '설명',' 피트', '최악', '외관', '며칠', '제일', '함', '들락거리', 
    '한참', '언박싱', '인지', '번', '자급', '느낌', '및', '맘', '색감', '가격', '피트', 
    '테스트', '전혀', '휴대', '여기', '소비', '근본', '말', '용', '오늘', '정해진', '이번', 
    '요', '위해', '기분', '조건', '안심', '모로', '개봉', '확인', '사이트', '시간', '점심', 
    '출시', '지급', '출고', '정상', '손', '발송', '하필', '아쥬아쥬', '아이', '발견', '영',
    '역대', '이상', '구형', '날짜', '종이', '건', '대체로', '적극', '품절', '무조건', '보기',
    '여름', '주머니', '색도', '화소', '넣기', '시전', '무렵', '통해', '확', '반응', '금', '경험', 
    '약품', '초기', '하나', '젤', '아이보리', '거나', '고베', '기존', '인치' '옆', '데', '키', 
    '징', '앞', '주위', '검은색', '안', '조금', '완료', '먼지', '일이', '계열','사라', '적립', 
    '핑크', '인치', '십삼', '패킹', '카드', '갓', '스펙', '옆', '색깔', '편의', '항상', '가지', 
    '주어', '등등', '글라스', '계속', '센터', '쓰렵니', '에어캡', '지금', '왓습니닿', '삐르', '뭐', '차이점',
    '라운드', '네추럴', '테두리', '재질', '달라', '내년', '스타일', '비교', '직접', '쿠폰', '최대', '통신사',
    '바롱', '요새', '삿거든', '데져트', '여', '안해', '대체', '캬', '등록', '사실', '이틀', '환불',
    '바꿨늘템데', '방지', '끼', '어제','쿠', '자위', '오후','쿠통', '넝', '투폰', '메인', '랫', '신사', 
    '만전', '플립', '신의한수', '우선', '완죤', '드', '질소', '기일', '모두', '세대', '바꿨늘템데', 
    '그', '부가', '끝판', '정도', '이후', '거', '시', '살짝', '근접', '혹', '내부', '스트레스',
    '보상', '만큼', '버꿨늘템데', '능데', '타','기한', '괜', '별', '기간', '설정', '더라도', '대용', '늘',
    '강력', '하니', '트', '인기', '굳이', '대비', '기스', '온라인', '조일이', '타입', '화요일', 
    '저녁', '월요일', '갑자기', '적립금', '요원', '올해', '짱', '반나절', '이유', '개월', '회사',
    '연장', '가능', '아무', '요즘', '엉망', '건가', '부족', '교통카드', '볼', '차라', '무광', 
    '최고봉', '얼른', '탑제', '불로', '일시', '여기저기', '어이', '확정', '스', '동생', '질', 
    '업글', '상의', '제조', '판매', '상', '대처', '만요', '성비', '때깔', '약간', '그대로', 
    '쿠으', '주', '쿠은', '처럼', '나은', '공식', '어보', '본인', '영접', '자트', '프맥', '모해', '보드',
    '안나', '또', '참고', '오타', '수준', '시도','등', 

}  

# 상위 30개 단어만 남기기
top_n = 30

# 긍정적 리뷰 워드클라우드 생성 (특정 단어 제외 후 상위 30개만 선택)
positive_filtered_counts = {word: count for word, count in positive_counts.items() if word not in exclude_words}
positive_top30 = dict(Counter(positive_filtered_counts).most_common(top_n))  # 상위 30개 단어 선택
wordcloud_positive = WordCloud(
    font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    background_color="white",
    colormap="Blues",
    width=800,
    height=400
).generate_from_frequencies(positive_top30)

# 부정적 리뷰 워드클라우드 생성 (특정 단어 제외 후 상위 30개만 선택)
negative_filtered_counts = {word: count for word, count in negative_counts.items() if word not in exclude_words}
negative_top30 = dict(Counter(negative_filtered_counts).most_common(top_n))  # 상위 30개 단어 선택
wordcloud_negative = WordCloud(
    font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    background_color="white",
    colormap="Reds",
    width=800,
    height=400
).generate_from_frequencies(negative_top30)

# 시각화 (긍정적 리뷰 워드클라우드)
plt.figure(figsize=(4, 2))
plt.imshow(wordcloud_positive, interpolation="bilinear")
plt.axis("off")
plt.title("아이폰 긍정적 리뷰 워드클라우드", fontsize=14)
plt.show()

# 시각화 (부정적 리뷰 워드클라우드)
plt.figure(figsize=(4, 2))
plt.imshow(wordcloud_negative, interpolation="bilinear")
plt.axis("off")
plt.title("아이폰 부정적 리뷰 워드클라우드", fontsize=14)
plt.show()


# #### **(2) s24 (갤럭시)**



# 'item'이 'S24'인 데이터에서 'clean_review'만 선택
s24_reviews = df_danawa[df_danawa['item'] == 'S24'][['clean_review']]

# 결과 확인
s24_reviews.head(3)

# s24에 대한 리뷰만 선택
s24_reviews = df_danawa[df_danawa['item'] == 'S24']['clean_review']

# 각 리뷰에서 명사 추출 및 불용어 제거
s24_reviews_nouns = s24_reviews.apply(extract_nouns_without_stopwords)


# 감성 분석 적용
s24_reviews_sentiment = s24_reviews_nouns.apply(sentiment_analysis)

# 긍정/부정 리뷰 분리
positive_reviews_s24 = s24_reviews[s24_reviews_sentiment == "positive"]
negative_reviews_s24 = s24_reviews[s24_reviews_sentiment == "negative"]

# 긍정, 부정 키워드 추출
positive_nouns_s24 = sum(positive_reviews_s24.apply(extract_nouns_without_stopwords), [])
negative_nouns_s24 = sum(negative_reviews_s24.apply(extract_nouns_without_stopwords), [])

# 키워드 빈도수 계산
positive_counts_s24 = Counter(positive_nouns_s24)
negative_counts_s24 = Counter(negative_nouns_s24)


# - 30개 

# 제외할 단어 리스트 (워드클라우드에서만 제외할 단어들)
exclude_words = {"문제", "구매", "삼성", "수", "제품", "구입", "추천", "만족", "최고", "핸드폰", "별로", "울트라",
                 "노트", "이번", "마음", "성능", "케이스", "색상", "더", "고민", "생각", "자급", "안", "좀", "하나",
                 "역시", "모두", "다음", "조금", "지금", "적극", "정도", "이", "그", "중", "기존", "후", "말", "정품", 
                 "완전", "교체", "크기", "듭니", "모델", "걱정", "크기", "부족", "센터", "필름", "참여", "점", "사이즐", 
                 "날", "플러스", "서비스", "유심", "를", "거", "저", "제", "때", "맘", "정말", "전자", "비", "부분", 
                 "커서", "또한", "시리즈", "최신", "전체", "손", "사은", "컬러", "품", "아주", "면", "휴대폰", "손목",
                 "차이", "처음", "무엇", "제일", "상품", "보고", "감", "해", "설정", "걸", "제공", "도", "듯", "고려", 
                 "계속", "어머니", "전", "사용자", "다시", "확장", "픽업", "등", "못", "색", "불만", "가격", 
                 "플립", "기본", "사이즈", "사", "가정", "쿠폰", "장점", "여기", "이제", "요", "마블", "불량", "케이블", 
                 "제로", "판매", "매장", "분", "상황", "가지", "스토어","액정", "오렌지", "앞", "능이", "하루", "기간", "블랙",
                 "그레이", "가성", "비", "용", "블루", "교환", "테두리", "테스트", "안내", "문의", "단", "기다림", "강남", "때문", 
                 "뭐", "수령", "느낌", "결과", "사람", "실망", '짜꾸', '이전', '움', '점도', '폴드', '옐로우', '로', '아들', '예전',
                 '살짝', '당일', '가장', '신청', '보호', '거의', '체감', '기분', '시간', '다행', '개봉', '아무', '주말', '고장', 
                 '출시', '평소', '또', '인식', '부담', '이틀', '달', '모든','강력', '대비', '확인', '재고', '박스', '후기', '모든', 
                 '바이올렛', '초기', '노란색', '이용', '자꾸', '실물', '개', '선호', '날짜', '와이프', '함', '활성화', '진', '사실',
                 '전용', '지인', '자녀', '새', '보조', '서로', '당황', '한번', '해결', '백만원', '시', '항상','무척', '습', '애플', 
                 '모친', '직접', '발전', '위해', '신세계', '우선', '참고', '게', '꼭', '덕분', '하니', '색감', '심', '직원', 
                 '찍', '데', '빛', '설명', '검은색', '부착', '내용', '이상','처리', '인터넷', '추가', '고', '아이', '곳', 
                 '실시간', '조건', '더욱','할부', '오늘', '동안', '연락', '지연', '답', '키', '전화', '방문', '언제', '대리점',
                 '쓰기','색깔', '줌', '친구', '활용', '보기', '전반', '개월', '쓱', '가입', '출고', '결제', '안심', '물량', 
                 '일자', '알뜰폰', '커버', '경로', '왜', '경우','건', '대해', '실감', '비교', '크게', '번', '주변', 
                 '페이지', '이건', '일', '팀', '태그', '프로모션', '그때', '편입', '각', '니', '파손', '해외', 
                 '무광', '고급', '적용', '공지', '톤', '사서', '대화', '첨부', '이후', '상담사', '돈','공홈', '차별', 
                 '세계', '한국인', '고가', '취향', '슬림', '접', '수준', '남지', '어제', '오후','한지', '온라인', 
                 '쇼마젠시', '굿', '금제', '가폰', '행시', '취급', '조작', '그것', '올해', '감사', '자체', '및', 
                 '부가', '그대로', '로젠택배', '고질', '주의', '역대', '기대', '기변', '주위', '연속', '크림', '임', '배달', 
                 '년전', '가끔','신뢰', '이슈', '약간', '오닉스', '동생', '버벅임', '마침', '차','생활', '작동', '일절',
                 '화이트', '끝', '가까이',
                 }

# 상위 30개 단어만 선택하는 함수
def get_top_n_words(word_counts, n=30):
    return dict(Counter({word: count for word, count in word_counts.items() if word not in exclude_words}).most_common(n))

# 긍정적 & 부정적 리뷰 워드클라우드 생성
positive_top_30_s24 = get_top_n_words(positive_counts_s24, 30)
negative_top_30_s24 = get_top_n_words(negative_counts_s24, 30)

# 워드클라우드 생성 함수
def generate_wordcloud(word_freq, colormap, title):
    if word_freq:
        wordcloud = WordCloud(
            font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            background_color="white",
            colormap=colormap,
            width=800,
            height=400
        ).generate_from_frequencies(word_freq)

        plt.figure(figsize=(4, 2))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(title, fontsize=14)
        plt.show()
    else:
        print(f"⚠️ '{title}'에 해당하는 단어가 없습니다.")

# 긍정적 리뷰 워드클라우드 (상위 30개)
generate_wordcloud(positive_top_30_s24, "Blues", "갤럭시 S24 긍정적 리뷰 워드클라우드")

# 부정적 리뷰 워드클라우드 (상위 30개)
generate_wordcloud(negative_top_30_s24, "Reds", "갤럭시 S24 부정적 리뷰 워드클라우드")


# # 7. 아이폰과 갤럭시 평균 계산

# 'scoring' 컬럼의 데이터를 정수형으로 변환하고, 'item'별 평균 계산
df_danawa['scoring'] = pd.to_numeric(df_danawa['scoring'], errors='coerce')  # 숫자형으로 변환

# item별 평균 score 계산
average_scores = df_danawa.groupby('item')['scoring'].mean()

# 결과 출력
print(average_scores)

# 'scoring'과 'item' 컬럼만 선택해서 미리보기
df_danawa[['scoring', 'item']].head(3)  # 첫 3개 데이터 확인

# 'scoring' 컬럼을 문자열로 변환한 후 '점' 제거 및 숫자만 추출
df_danawa['scoring'] = df_danawa['scoring'].astype(str)  # 먼저 문자열로 변환
df_danawa['scoring'] = df_danawa['scoring'].str.replace('점', '', regex=False)  # '점' 제거
df_danawa['scoring'] = pd.to_numeric(df_danawa['scoring'], errors='coerce')  # 숫자로 변환, 변환 불가시 NaN 처리

# 'scoring'과 'item' 컬럼만 출력하여 확인
print(df_danawa[['scoring', 'item']].head(3))

# 'scoring'과 'item_id' 컬럼을 선택하고, NaN 값을 가진 행을 제거
df_selected = df_danawa[['scoring', 'item']].dropna(subset=['scoring'])

# 결과 확인
print(df_selected.head(3))  # 상위 10개 출력

# 'scoring' 컬럼에서 '점'을 제거하고, 숫자만 추출 후 평균과 최대값 계산
df_danawa['scoring'] = df_danawa['scoring'].str.replace('점', '', regex=False)  # '점' 제거
df_danawa['scoring'] = pd.to_numeric(df_danawa['scoring'], errors='coerce')  # 숫자형으로 변환

# 최대 점수와 평균 점수 계산
max_score = df_danawa['scoring'].max()
mean_score = df_danawa['scoring'].mean()

# 결과 출력
print(f"최대 점수: {max_score}")
print(f"평균 점수: {mean_score:.2f}")


# 'item'별 평균 점수 계산 (S24와 아이폰)
average_score_by_item = df_danawa.groupby('item')['scoring'].mean()

# 결과 출력
print(average_score_by_item)


# 1. 최대점수(Max Score): 100점(scoring columns max)   
# 2. 평균점수(Mean Score): 전체 평균점수 97.32(scoring cloumns all number mean)
#     - 전체적으로 높은 점수가 부여되어져 있음.  
# 3. item별 평균 점수
#    - s249(삼성): 96.86점  
#    - 아이폰15(아이폰): 98.18점  
#    -> 아이폰16이 s24보다 평균이 약간 높다는걸 알 수 있음.  

