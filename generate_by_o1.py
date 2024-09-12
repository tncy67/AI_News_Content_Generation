import requests
from transformers import pipeline
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import torch

load_dotenv()

# Check if CUDA is available and set the device accordingly
device = 0 if torch.cuda.is_available() else -1

# Initialize the summarization pipeline
summarizer = pipeline('summarization', model="facebook/bart-large-cnn", device=device)

def split_text(text, max_chunk_length=500):
    """
    Splits the text into chunks that the model can handle.
    """
    sentences = text.split('. ')
    chunks = []
    current_chunk = ''
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_length:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + '. '
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def get_top_news(api_key):
    """
    Fetches the top 10 Google News articles using the NewsAPI.
    """
    url = ('https://newsapi.org/v2/top-headlines?'
           'country=us&'
           'pageSize=10&'
           f'apiKey={api_key}')
    response = requests.get(url)
    data = response.json()
    articles = data['articles']
    return articles

def summarize_article(content):
    """
    Summarizes the article content into a few paragraphs.
    """
    chunks = split_text(content)
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    return ' '.join(summaries)


def rewrite_title(title):
    """
    Rewrites the title in a meaningful way.
    """
    # Placeholder for the actual rewriting logic
    rewritten_title = "Breaking: " + title
    return rewritten_title

def generate_educational_content(summary):
    """
    Provides educational content related to the article.
    """
    # Placeholder for the actual content generation
    educational_content = f"Did you know? {summary}"
    return educational_content

def create_youtube_search_query(summary):
    """
    Creates a short summary for YouTube search.
    """
    words = summary.split()
    search_query = ' '.join(words[:5])
    return search_query

def search_youtube(query, api_key):
    """
    Searches for a related YouTube video and retrieves its link and title.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        part='snippet',
        maxResults=1,
        q=query,
        type='video'
    )
    response = request.execute()
    video_title = response['items'][0]['snippet']['title']
    video_id = response['items'][0]['id']['videoId']
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    return video_title, video_link

def create_hashtags(summary):
    """
    Generates one or a few hashtags for the summarized article.
    """
    # Placeholder for actual hashtag generation logic
    hashtags = ['#NewsUpdate', '#BreakingNews']
    return hashtags

def create_blog_post(rewritten_title, summary, educational_content, video_title, video_link, hashtags):
    """
    Combines all elements into a flowing, engaging new news article.
    """
    post = (
        f"{rewritten_title}\n\n"
        f"{summary}\n\n"
        f"{educational_content}\n\n"
        f"Related Video: {video_title}\n"
        f"{video_link}\n\n"
        f"{' '.join(hashtags)}"
    )
    return post

def main():
    news_api_key = os.getenv("NEWS_API")
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")

    articles = get_top_news(news_api_key)
    for article in articles:
        try:
            title = article['title']
            content = article['content'] or article['description']
            if not content:
                print(f"No content available for article: {title}")
                continue
            summary = summarize_article(content)
            rewritten_title = rewrite_title(title)
            educational_content = generate_educational_content(summary)
            search_query = create_youtube_search_query(summary)
            video_title, video_link = search_youtube(search_query, youtube_api_key)
            hashtags = create_hashtags(summary)
            blog_post = create_blog_post(
                rewritten_title, summary, educational_content, video_title, video_link, hashtags
            )
            # Output the blog post
            print(blog_post)
            print("\n" + "=" * 80 + "\n")
        except Exception as e:
            print(f"An error occurred with the article '{title}': {e}")

if __name__ == "__main__":
    main()
