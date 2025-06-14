# -*- coding: utf-8 -*-
"""YT_Analysis.ipynb

Original file is located at
    https://colab.research.google.com/drive/1tuISdEHOnUo8OrBjHiCvu8DykdCNFWE6
"""

import pandas as pd
from googleapiclient.discovery import build

# Copy the API key from GCP
API_KEY = 'Your_API_KEY'

def get_trending_videos(API_KEY, max_results=500):
  #build the youtube service
  youtube = build('youtube', 'v3', developerKey=API_KEY)

  #initialize the list to hold video details.
  videos = []

  #fetch the most popular videos
  request = youtube.videos().list(
      part= 'snippet,contentDetails,statistics',
      chart='mostPopular',
      regionCode='US',
      maxResults=50
  )

#paginate through the results if max_results are > 50
  while request and len(videos) < max_results:
    response = request.execute()
    for item in response['items']:
      video_details = {
      'Video_id': item['id'],
      'title': item['snippet']['title'],
      'description': item['snippet']['description'],
      'published_at': item['snippet']['publishedAt'],
      'channel_id': item['snippet']['channelId'],
      'channel_title': item['snippet']['channelTitle'],
      'category_id': item['snippet']['categoryId'],
      'tags': item['snippet'].get ('tags', []),
      'duration': item['contentDetails']['duration'],
      'definition': item['contentDetails']['definition'],
      'caption': item['contentDetails'].get('caption', 'false'),
      'view_count': item['statistics'].get('viewCount', 0),
      'like_count': item['statistics'].get('likeCount', 0),
      'dislike_count': item['statistics'].get('dislikeCount', 0),
      'favorite_count': item['statistics'].get('favoriteCount', 0),
      'comment_count': item['statistics'].get('commentCount', 0)

      }
      videos.append(video_details)

      #get the next page tocken
      request = youtube.videos().list_next(request, response)

  return videos[:max_results]

def save_to_csv(data, file_name):
  df = pd.DataFrame(data)
  df.to_csv(file_name, index=False)

def main():
  trending_videos = get_trending_videos(API_KEY)
  file_name = 'trending_videos.csv'
  save_to_csv(trending_videos, file_name)
  print(f'trending_videos saved to {file_name}')

if __name__ == '__main__':
  main()

# Read csv file.
trending_videos = pd.read_csv('trending_videos.csv')
trending_videos.head()

# Check for missing values
missing_values = trending_videos.isnull().sum()

#display data types
data_types = trending_videos.dtypes

missing_values, data_types

# Fill missing value.
trending_videos['description'].fillna('No description', inplace=True)

#Convert published at to datetime format
trending_videos['published_at'] = pd.to_datetime(trending_videos['published_at'])

# convert tags from string representation to actual list
trending_videos['tags'] = trending_videos['tags'].apply(lambda x: eval(x) if isinstance(x, str) else x)

# Get the descriptive statistics
descriptive_stats = trending_videos[['view_count', 'like_count', 'dislike_count', 'favorite_count', 'comment_count']].describe()
descriptive_stats

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = 'whitegrid')

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

#View count distribution
sns.histplot(trending_videos['view_count'], bins=30, kde=True, ax=axes[0], color='blue')
axes[0].set_title('View Count Distribution')
axes[0].set_xlabel('View Count')
axes[0].set_ylabel('frequency')

#Like count distribution
sns.histplot(trending_videos['like_count'], bins=30, kde=True, ax=axes[1], color='green')
axes[1].set_title('Like Count Distribution')
axes[1].set_xlabel('Like Count')
axes[1].set_ylabel('frequency')

#Comment Count distribution
sns.histplot(trending_videos['comment_count'], bins=30, kde=True, ax=axes[2], color='red')
axes[2].set_title('Comment Count Distribution')
axes[2].set_xlabel('Comment Count')
axes[2].set_ylabel('frequency')

plt.tight_layout()
plt.show()

#Correlation matrix
correlation_matrix = trending_videos[['view_count', 'like_count', 'comment_count']].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, linecolor = 'black')
plt.title('Correlation Matrix of Engagement Metrics')
plt.show()

from googleapiclient.discovery import build

API_KEY = 'Your_API_KEY'
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_category_mapping():
    request = youtube.videoCategories().list(
        part='snippet',
        regionCode='US'
    )
    response = request.execute()
    category_mapping = {}
    for item in response['items']:
        category_id = int(item['id'])
        category_name = item['snippet']['title']
        category_mapping[category_id] = category_name
    return category_mapping

# get the category mapping
category_mapping = get_category_mapping()
print(category_mapping)

# map trending_videos of category_id and category_name
trending_videos['category_name'] = trending_videos['category_id'].map(category_mapping)

# Bar charts for category counts
plt.figure(figsize= (12, 6))
sns.countplot(y=trending_videos['category_name'], order = trending_videos['category_name'].value_counts().index, palette = 'viridis')
plt.title('Number of Trending Videos by Category')
plt.xlabel('Number of Videos')
plt.ylabel('Category')
plt.show()

# average engagement metrics by category
category_engagement = trending_videos.groupby('category_name')[['view_count', 'like_count', 'comment_count']].mean().sort_values(by='view_count', ascending=False)

fig, axes = plt.subplots(1, 3, figsize=(18, 10))

# view count by category
sns.barplot(y=category_engagement.index, x=category_engagement['view_count'], ax=axes[0], palette='viridis')
axes[0].set_title('Average View Count by Category')
axes[0].set_xlabel('Average View Count')
axes[0].set_ylabel('Category')

# like count by category
sns.barplot(y=category_engagement.index, x=category_engagement['like_count'], ax=axes[1], palette='viridis')
axes[1].set_title('Average Like Count by Category')
axes[1].set_xlabel('Average Like Count')
axes[1].set_ylabel('')

# comment count by category
sns.barplot(y=category_engagement.index, x=category_engagement['comment_count'], ax=axes[2], palette='viridis')
axes[2].set_title('Average Comment Count by Category')
axes[2].set_xlabel('Average Comment Count')
axes[2].set_ylabel('')

plt.tight_layout()
plt.show()

!pip install isodate
import isodate

#Conver ISO 8601 duration to seconds
trending_videos['duration_seconds']= trending_videos['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())

trending_videos['duration_range'] = pd.cut(trending_videos['duration_seconds'], bins=[0, 300, 600, 1200, 2400, 3600, 7200], labels=['0-5 min', '5-10 min', '10-20 min', '20-60 min', '60-120 min', '>120 min'])

# Scatterplot for Video length vs View count
plt.figure(figsize=(10, 6))
sns.scatterplot(x='duration_seconds', y='view_count', data=trending_videos, alpha=0.6, color='purple')
plt.title('Video Length vs Video Count')
plt.xlabel('Video Length (seconds)')
plt.ylabel('View Count')
plt.show()

# Bar Chart Engagement Metrics by Duration
length_engagement = trending_videos.groupby('duration_range')[['view_count', 'like_count', 'comment_count']].mean()

fig, axes = plt.subplots(1,3, figsize=(18, 8))

#View Count by duration
sns.barplot(y=length_engagement.index, x=length_engagement['view_count'], ax=axes[0], palette = 'magma')
axes[0].set_title('Average View Count by Duration')
axes[0].set_xlabel('Average View Count')
axes[0].set_ylabel('Duration')

#Like Count by duration
sns.barplot(y=length_engagement.index, x=length_engagement['like_count'], ax=axes[1], palette = 'magma')
axes[1].set_title('Average Like Count by Duration')
axes[1].set_xlabel('Average Like Count')
axes[1].set_ylabel('')

#Comment Count by Duration
sns.barplot(y=length_engagement.index, x=length_engagement['comment_count'], ax=axes[2], palette = 'magma')
axes[2].set_title('Average Comment Count by Duration')
axes[2].set_xlabel('Average Comment Count')
axes[2].set_ylabel('')

plt.tight_layout()
plt.show()

# Calculate the number of tags for each video
trending_videos['tag_count'] = trending_videos['tags'].apply(len)

#Scatterplot for tags vs num of views
plt.figure(figsize=(10, 6))
sns.scatterplot(x='tag_count', y='view_count', data = trending_videos, alpha=0.6, color = 'orange')
plt.title('Tag Count vs View Count')
plt.xlabel('Tag Count')
plt.ylabel('View Count')
plt.show()

# Extract Hour of Publication
trending_videos['hour_of_publication'] = trending_videos['published_at'].dt.hour

# Bar chart for published hour distribution
plt.figure(figsize=(12, 6))
sns.countplot(x='hour_of_publication', data=trending_videos, palette='coolwarm')
plt.title('Published Hour Distribution')
plt.xlabel('Hour of Publication')
plt.ylabel('Number of Videos')
plt.show()

#Scatter plot for publish hour vs View Count
plt.figure(figsize=(10,6))
sns.scatterplot(x='hour_of_publication', y='view_count', data=trending_videos, alpha=0.6, color = 'teal')
plt.title('Published Hour vs View Count')
plt.xlabel('Hour of Publication')
plt.ylabel('View Count')
plt.show()
