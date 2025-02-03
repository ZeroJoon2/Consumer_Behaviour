from googleapiclient.discovery import build
import json

api_key = 'AIzaSyB91DuDtYBMaloczSLXIGmIlhRJXGU5g_g'
youtube = build('youtube', 'v3', developerKey=api_key)
search_query = '갤럭시 S24 리뷰'
request = youtube.search().list(
    q=search_query,  
    part='snippet',
    type='video',    
    maxResults=50, 
    order='viewCount',
    publishedAfter='2024-01-17T00:00:00Z'
)
search_response = request.execute()


video_data = [
    {
        'video_id': item['id']['videoId'],
        'title': item['snippet']['title'],
        'published_at': item['snippet']['publishedAt'],  
        'channel_title': item['snippet']['channelTitle'] 
    }
    for item in search_response['items']
]

def get_all_comments(video_id):
    comments = []
    next_page_token = None
    while True:
        request = youtube.commentThreads().list(
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

    return comments

all_comments = {}
for video in video_data:
    video_id = video['video_id']
    title = video['title']
    published_at = video['published_at']
    channel_title = video['channel_title']
    comments = get_all_comments(video_id)
    all_comments[video_id] = {
        'title': title,
        'published_at': published_at,
        'channel_title': channel_title,
        'comments': comments
    }
    
with open('youtube_s24_1.json', 'w', encoding='utf-8') as f:
    json.dump(all_comments, f, ensure_ascii=False, indent=4)

print('저장 완료')

import pandas as pd
import json

with open('youtube_s24_1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = []
for video_id, video_info in data.items():
    title = video_info['title']
    published_at = video_info['published_at']
    channel_title = video_info['channel_title']
    for comment_info in video_info['comments']:
        comment = comment_info['comment']
        like_count = comment_info['like_count']
        comment_published_at = comment_info['published_at']
        rows.append([video_id, title, published_at, channel_title, comment, like_count, comment_published_at])

df = pd.DataFrame(rows, columns=['video_id', 'title', 'publish_date', 'channel_name', 'comment', 'like_count', 'comment_publish_date'])
df.to_csv('youtube_s24_1.csv', index=False, encoding='utf-8-sig')

print('CSV 파일 저장 완료')

search_query = '갤럭시 S24 후기'
request = youtube.search().list(
    q=search_query,  
    part='snippet',
    type='video',    
    maxResults=50, 
    order='viewCount',
    publishedAfter='2024-01-17T00:00:00Z'
)
search_response = request.execute()


video_data = [
    {
        'video_id': item['id']['videoId'],
        'title': item['snippet']['title'],
        'published_at': item['snippet']['publishedAt'],  
        'channel_title': item['snippet']['channelTitle'] 
    }
    for item in search_response['items']
]

def get_all_comments(video_id):
    comments = []
    next_page_token = None
    while True:
        request = youtube.commentThreads().list(
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

    return comments

all_comments = {}
for video in video_data:
    video_id = video['video_id']
    title = video['title']
    published_at = video['published_at']
    channel_title = video['channel_title']
    comments = get_all_comments(video_id)
    all_comments[video_id] = {
        'title': title,
        'published_at': published_at,
        'channel_title': channel_title,
        'comments': comments
    }
    
with open('youtube_s24_2.json', 'w', encoding='utf-8') as f:
    json.dump(all_comments, f, ensure_ascii=False, indent=4)

print('저장 완료')

with open('youtube_s24_2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

rows = []
for video_id, video_info in data.items():
    title = video_info['title']
    published_at = video_info['published_at']
    channel_title = video_info['channel_title']
    for comment_info in video_info['comments']:
        comment = comment_info['comment']
        like_count = comment_info['like_count']
        comment_published_at = comment_info['published_at']
        rows.append([video_id, title, published_at, channel_title, comment, like_count, comment_published_at])

df = pd.DataFrame(rows, columns=['video_id', 'title', 'publish_date', 'channel_name', 'comment', 'like_count', 'comment_publish_date'])
df.to_csv('youtube_s24_2.csv', index=False, encoding='utf-8-sig')

print('CSV 파일 저장 완료')