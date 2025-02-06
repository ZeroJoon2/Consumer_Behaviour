import os
import time
import json
import pandas as pd
from googleapiclient.discovery import build

# 갤럭시 S24 : '2024-01-17T00:00:00Z'
# 아이폰 16 : '2024-09-10T00:00:00Z'
# 갤럭시 Z 폴드 6/플립 6 : '2024-07-10T00:00:00Z'
# 함수 : search_videos, get_all_comments, save_comments_to_csv
# airflow/dags/etl_youtube_api.py
# airflow/dags/youtube_api_function.py

API_KEY = 'AIzaSyBVLeWNpSeMRAcCTe0yIXfsodlUKWWKoDU'

# API
def get_youtube_service(api_key):
    return build('youtube', 'v3', developerKey=api_key)

youtube_service = get_youtube_service(API_KEY)

# 비디오 
def search_videos(search_query, published_after):
    request = youtube_service.search().list(
        q=search_query,
        part='snippet',
        type='video',
        maxResults=50,
        order='viewCount',
        publishedAfter=published_after
    )
    response = request.execute()
    video_data = [
        {
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'published_at': item['snippet']['publishedAt'],
            'channel_title': item['snippet']['channelTitle']
        }
        for item in response['items']
    ]
    # 아이폰은 첫 번째 영상 제거
    if search_query.lower().startswith('아이폰'):
        video_data = video_data[1:]  # 첫 번째 영상 제거

    return video_data, response.get('nextPageToken')

# 댓글
def get_all_comments(video_id):
    comments = []
    next_page_token = None
    while True:
        request = youtube_service.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            like_count = item['snippet']['topLevelComment']['snippet']['likeCount']
            published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']
            comments.append({'comment': comment, 'like_count': like_count, 'published_at': published_at})

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
        time.sleep(1)

    return comments

# Parquet로 저장
def save_comments_to_parquet(all_comments, filename='youtube_comments.parquet'):
    data = []
    for video_id, video_info in all_comments.items():
        title = video_info['title']
        published_at = video_info['published_at']
        channel_title = video_info['channel_title']
        comments = video_info['comments']

        for comment in comments:
            data.append({
                'video_id': video_id,
                'title': title,
                'publish_date': published_at,
                'channel_name': channel_title,
                'comment': comment['comment'],
                'like_count': comment['like_count'],
                'comment_publish_date': comment['published_at']
            })
    
    df = pd.DataFrame(data)
    df.to_parquet(filename, engine='pyarrow', index=False)
    print(f'저장 완료: {filename}')

